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
    Create a google Url from a given string
    """
    google_dict = {"q": query}
    if site:
        web = urlparse(site).netloc
        google_dict["as_sitesearch"] = web
        return Urls.GOOGLE_SEARCH.value + urlencode(google_dict)
    return Urls.GOOGLE_SEARCH.value + urlencode(google_dict)


def get_google_business_info(search_item: str) -> tuple[int, str]:
    """return cid and google map page of the business if it exists"""

    try:
        url = get_google_url(search_item)
        browser = splinter.Browser("firefox", headless=True, incognito=True)
        browser.visit(url)
        soup = BeautifulSoup(browser.html, "html.parser")
        cid = soup.find("a", {"data-rc_q": search_item})["data-rc_ludocids"]
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


def get_reviews_token(url: str) -> str:
    try:
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.implicitly_wait(5)
        button = driver.find_element(
            By.CSS_SELECTOR, "button.ZiKfbc.tUdUte.Hk4XGb.ZqLNQd"
        )
        jstrack = button.get_attribute("jstrack")
        jstrack_string = jstrack.split(":")[0]
        driver.close()
        return jstrack_string

    except TimeoutException as e:
        raise (f"Timeout error: {e}")

    except NoSuchElementException as e:
        raise (f"Element not found: {e}")

    except Exception as e:
        raise (f"An error occurred: {e}")
