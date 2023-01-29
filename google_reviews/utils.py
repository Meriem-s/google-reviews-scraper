import re
from urllib.parse import urlencode, urlparse

import splinter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

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


def get_google_business_info(place_name: str) -> tuple[int, str]:
    """return cid and url of gmaps place if it exists"""

    try:
        url = get_google_url(place_name)
        browser = splinter.Browser("firefox", headless=True, incognito=True)
        browser.visit(url)
        soup = BeautifulSoup(browser.html, "html.parser")
        cid = soup.find("a", {"data-rc_q": place_name})["data-rc_ludocids"]
        data_url = soup.find("a", {"data-url": True})["data-url"]
        business_url = Urls.GOOGLE.value + data_url
        browser.quit()
        return int(cid), business_url

    except TimeoutException as e:
        raise (f"Timeout error: {e}")

    except NoSuchElementException as e:
        raise (f"Element not found: {e}")

    except Exception as e:
        raise (f"An error occurred: {e}")


def get_reviews_tokens(url: str, cid: str) -> tuple[str, str]:

    """Gets reviews tokens from a gmaps page"""
    try:
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.get(url)
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
        driver.close()
        return jstrack_string, id_1

    except TimeoutException as e:
        raise (f"Timeout error: {e}")

    except NoSuchElementException or AttributeError as e:
        raise (f"Element not found: {e}")

    except Exception as e:
        raise (f"An error occurred: {e}")
