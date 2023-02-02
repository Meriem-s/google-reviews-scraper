# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime
from dataclasses import dataclass


@dataclass
class GoogleReviewItem:
    name: str
    content: str
    link: str
    rating: int
    time: str
    did_owner_reply: bool
    owner_reply: str

    def __init__(self, review_raw: dict):
        self.name = review_raw[0][1]
        self.content = review_raw[3]
        self.link = review_raw[18]
        self.rating = review_raw[4]
        self.time = (datetime.datetime.utcfromtimestamp(review_raw[27] / 1000))
        self.did_owner_reply = review_raw[9] is not None
        self.owner_reply = review_raw[9][1] if self.did_owner_reply else ""
