import csv
import json
from urllib.parse import quote

import scrapy
from scrapy.exceptions import CloseSpider

from google_reviews.items import GoogleReviewItem
from google_reviews.urls_enum import Urls
from google_reviews.utils import parse_gmaps_page, parse_google_business_info


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
        self.reviews_number = None
        self.search_venue = search_venue
        self.unique_reviews = set()
        self.csv_filename = csv_filename
        with open(csv_filename, "w") as csv_file:
            self.writer = csv.DictWriter(
                csv_file, fieldnames=self.fields, quoting=csv.QUOTE_MINIMAL
            )
            self.writer.writeheader()

    def start_requests(self):
        search_item = self.search_venue

        try:
            # validate business page
            cid, url = parse_google_business_info(search_item)
            self.id_2 = cid
            self.id_4, self.id_1, self.reviews_number = parse_gmaps_page(url, cid)
            yield scrapy.Request(
                url=self.create_list_entities_url(), callback=self.parse_reviews
            )
        except Exception as e:
            self.logger.info(
                "The search item is not a business to review and has no CID assigned to, please enter the correct venue!"
            )
            raise CloseSpider(
                "The search item is not a venue to review, please insert the correct venue string"
            )

    def create_list_entities_url(self) -> str:
        """
        the url for the reviews request is under this format
        "https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=de&pb=!1m2!1y{id_1}!2y{id_2}!2m1!2i10!3s{id_3}!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{id_4}!7e81"


        id_1:
        id_2 : cid
        id_3: id of the next review, it gets updated every time there is a listentitiesreviews Get request. It does not exist in the beginning
        id_4: fixed token is parsed from the gmaps page  of the business

        """
        if self.id_3:
            url = f"{Urls.LIST_ENTITIES_PREFIX.value}{self.id_1}!2y{self.id_2}!2m2!2i10!3s{self.id_3}!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{self.id_4}!7e81"
        else:
            url = f"{Urls.LIST_ENTITIES_PREFIX.value}{self.id_1}!2y{self.id_2}!2m1!2i10!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b0!5m2!1s{self.id_4}!7e81"
        return url

    def write_review_to_csv(self, review_dict):
        with open(self.csv_filename, "a", newline="") as csvfile:
            fieldnames = review_dict.keys()
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            writer.writerow(review_dict)

    def parse_reviews(self, response):
        """Parse reviews from the response json data and store them in the csv file"""
        try:
            print("List of Entites URL is: ", response.url)
            reviews_raw = json.loads(response.text[5:])[2]
            self.id_3 = quote(reviews_raw[3][-1])  # the last element of the review list

            for review in reviews_raw:
                rev = GoogleReviewItem(review)
                review_dict = rev.__dict__
                if str(review_dict) not in self.unique_reviews:
                    self.write_review_to_csv(review_dict)
                    self.unique_reviews.add(str(review_dict))

            return scrapy.Request(
                url=self.create_list_entities_url(), callback=self.parse_reviews
            )
        except IndexError:
            return
        except TypeError or AttributeError:
            raise "Unexpected format"
