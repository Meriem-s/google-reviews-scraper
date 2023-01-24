# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy


class GoogleReviewItem(scrapy.Item):
    name = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()
    rating = scrapy.Field()
    time = scrapy.Field()
    did_owner_reply = scrapy.Field()
    owner_reply = scrapy.Field()

    def __init__(self, review_raw: dict):
        owner_reply = review_raw[9][1] if review_raw[9] else ""
        super(GoogleReviewItem, self).update(
            {"name": review_raw[0][1],
             "content": review_raw[3],
             "link": review_raw[18],
             "rating": review_raw[4],
             "time": datetime.datetime.utcfromtimestamp(review_raw[27] / 1000),
             "did_owner_reply": review_raw[9],
             "owner_reply":   owner_reply     
            })