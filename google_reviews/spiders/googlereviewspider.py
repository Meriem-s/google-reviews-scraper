import csv
import json
from urllib.parse import quote

import scrapy
from scrapy.exceptions import CloseSpider

from google_reviews.items import GoogleReviewItem
from google_reviews.urls_enum import Urls
from google_reviews.utils import (
    get_google_business_info,
    get_reviews_tokens,
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

    def __init__(self, csv_filename="venue_reviews.csv", search_venue: str = ""):
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
        self.search_venue = search_venue
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fields)
        self.writer.writeheader()

    def start_requests(self):
        search_item = self.search_venue

        # validate business page
        cid, url = get_google_business_info(search_item)
        if cid:
            yield scrapy.Request(
                url=url, callback=self.update_list_entites_ids, meta={"cid": cid}
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

    def update_list_entites_ids(self, response):
        """
        the url for the reviews request is under this format
        "https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=de&pb=!1m2!1y{id_1}!2y{id_2}!2m1!2i10!3s{id_3}!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{id_4}!7e81"


        id_1:
        id_2 : cid
        id_3: id of the next review, it gets updated every time there is a listentitiesreviews Get request. It does not exist in the beginning
        id_4: fixed token is parsed from the gmaps page  of the business

        """
        self.id_2 = str(response.meta["cid"])
        self.id_4, self.id_1 = get_reviews_tokens(response.url, self.id_2)


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
                self.writer.writerow(rev.__dict__)

            return scrapy.Request(
                url=self.create_list_entities_url(), callback=self.parse_reviews
            )
        except IndexError:
            return
        except TypeError or AttributeError:
            raise "Unexpected format"
