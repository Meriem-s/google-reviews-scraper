import csv
import json
import re
from urllib.parse import quote, urlencode

import scrapy
from scrapy.exceptions import CloseSpider

from google_reviews.items import GoogleReviewItem
from google_reviews.urls_enum import Urls
from google_reviews.utils.business_page_validator import (
    get_google_business_info,
    get_reviews_token,
)


class GoogleReviewsSpider(scrapy.Spider):
    name = "google_reviews"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "INFO",
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        "RETRY_TIMES": 5,
        "venue_maps_page_url": None,
    }

    def __init__(self, csv_filename="reviews.csv", **kwargs):
        self.fields = [
            "name",
            "content",
            "link",
            "rating",
            "time",
            "did_owner_reply",
            "owner_reply",
        ]
        self.id_1 = ""
        self.id_2 = ""
        self.id_3 = ""
        self.id_4 = ""
        self.id_5 = ""
        self.csv_file = open(csv_filename, "w")
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fields)
        self.writer.writeheader()

    def start_requests(self):
        search_item = "Neni Berlin"  # hardcoded for now

        # validate business page
        cid, url = get_google_business_info(search_item)
        if cid:
            yield scrapy.Request(
                url=url, callback=self.get_list_entites_ids, meta={"cid": cid}
            )
        else:
            self.logger.info(
                "The search item is not a business to review and has no CID assigned to, please enter the correct venue!"
            )
            raise CloseSpider(
                "The search item is not a venue to review, please insert the correct venue string"
            )

    def create_list_entities_url(self) -> str:
        print("self.id_3", self.id_3)
        if self.id_3:
            url = f"{Urls.LIST_ENTITIES_PREFIX.value}{self.id_1}!2y{self.id_2}!2m2!2i10!3s{self.id_3}!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{self.id_4}!7e81"
        else:
            url = f"{Urls.LIST_ENTITIES_PREFIX.value}{self.id_1}!2y{self.id_2}!2m2!2i10!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{self.id_4}!7e81"

        print(url)
        return url

    def get_list_entites_ids(self, response):
        """
        the url for the reviews request is under this format
        "https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=de&pb=!1m2!1y{id_1}!2y{id_2}!2m1!2i10!3s{id_3}!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{id_4}!7e81"


        id_1: is parsed below from the response content
        id_2 : cid
        id_3: id of the next review, it gets updated every time there is a listentitiesreviews Get request. It does not exist in the beginning
        id_4: fixed token is parsed from the gmaps page  of the business

        """
        self.id_4 = get_reviews_token(response.url)
        self.id_2 = str(response.meta["cid"])
        self.id_1 = re.search(
            rf'null,null,null,null,null,null,\[\\"(.*?)\\",\\"{self.id_2}\\"\]',
            response.text,
        ).group(1)

        yield scrapy.Request(
            url=self.create_list_entities_url(), callback=self.parse_reviews
        )

    def parse_reviews(self, response):
        """Parse reviews from the response json data and store them in the csv file"""
        try:
            reviews_raw = json.loads(response.text[5:])[2]
            self.id_3 = quote(reviews_raw[3][-1])  # the last element of the review list

            for review in reviews_raw:

                rev = GoogleReviewItem(review)

            return scrapy.Request(
                url=self.create_list_entities_url(), callback=self.parse_reviews
            )
        except IndexError:
            return
        except TypeError or AttributeError:
            raise "Unexpected format"
