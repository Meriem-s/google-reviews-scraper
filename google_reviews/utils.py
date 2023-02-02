import re
from urllib.parse import urlencode, urlparse

import pandas as pd
import splinter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from google_reviews.spiders.custom_exceptions import NoCidFound

from google_reviews.urls_enum import Urls


def get_google_url(query: str, site: str = "") -> str:
    """ "
    Utils Function
    Create a google Url Search from a given string
    """
    google_dict = {"q": query}
    if site:
        web = urlparse(site).netloc
        google_dict["as_sitesearch"] = web
        return Urls.GOOGLE_SEARCH.value + urlencode(google_dict)
    return Urls.GOOGLE_SEARCH.value + urlencode(google_dict)


def parse_google_business_info(place_name: str) -> tuple[int, str]:
    """return cid, url of gmaps place if it exists"""

    try:
        url = get_google_url(place_name)
        print("Google Search Url: ", url)
        browser = splinter.Browser("firefox", headless=True, incognito=True)
        browser.visit(url)
        soup = BeautifulSoup(browser.html, "html.parser")
        try:
            cid = soup.find("a", {"data-rc_q": place_name})["data-rc_ludocids"]
        except Exception as e:
            raise NoCidFound
        data_url = soup.find("a", {"data-url": True})["data-url"]
        business_url = Urls.GOOGLE.value + data_url
        print("Google Maps Url: ", business_url)
        browser.quit()
        return int(cid), business_url

    except TimeoutException as e:
        raise (f"Timeout error: {e}")

    except NoSuchElementException as e:
        raise (f"Element not found: {e}")
    except Exception as e:
        raise (f"An error occurred: {e}")


def parse_gmaps_page(url: str, cid: str) -> tuple[str, str, int]:

    """Gets reviews tokens from a gmaps page as well as number of reviews of the venue"""
    try:
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(10)

        driver.get(url)

        # Reject all cookies
        try:
            button = driver.find_element(
                By.CSS_SELECTOR,
                "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7",
            )
            button.click()

        except:
            print("no 'Reject all' button exists")
        driver.implicitly_wait(10)
        button = driver.find_element(
            By.CSS_SELECTOR, "button.ZiKfbc.tUdUte.Hk4XGb.ZqLNQd"
        )

        jstrack = button.get_attribute("jstrack")
        jstrack_string = jstrack.split(":")[0]
        id_1 = re.search(
            f'null,null,null,null,null,null,\[\\\\"([0-9]+)\\\\",\\\\"',
            driver.page_source,
        ).group(1)

        # Get number of reviews
        review_span = driver.find_element_by_xpath('//span[@jstcache="104"]')
        review_text = review_span.text
        reviews_number = extract_reviews_number(review_text)

        driver.close()

        return jstrack_string, id_1, reviews_number

    except TimeoutException as e:
        raise (f"Timeout error: {e}")

    except NoSuchElementException or AttributeError as e:
        raise (f"Element not found: {e}")

    except Exception as e:
        raise (f"An error occurred: {e}")


def extract_reviews_number(review_text: str) -> int:
    """Extract reviews number from a text.

    e.g: review_text 3,049 reviews
    Output: 3049

    """
    parts = review_text.split(" ")
    reviews = parts[0]
    if "," in reviews:
        reviews = reviews.replace(",", "")
    print("Number of reviews: ", reviews)
    return int(reviews)


def count_rows_csv(file_path) -> int:
    df = pd.read_csv(file_path)
    row_count = len(df.index)
    print("Number of rows in the CSV file: ", row_count)
