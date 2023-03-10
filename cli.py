import argparse

import scrapy.crawler

from google_reviews.spiders.googlereviewspider import GoogleReviewsSpider
from google_reviews.utils import count_rows_csv


# e.g. args.search "Neni Berlin"
class GoogleReviewsCrawler:
    def __init__(self, search: str, output: str = "reviews.csv"):
        self.search = search
        self.output = output
        self.spider = GoogleReviewsSpider

    def run(self):
        if not self.search:
            raise "please enter a correct search venue"
        process = scrapy.crawler.CrawlerProcess()
        if self.output:
            process.crawl(
                self.spider, search_venue=self.search, csv_filename=self.output
            )
        else:
            process.crawl(self.spider, search_venue=self.search)
        process.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("search", help="search for the business")
    parser.add_argument("-o", "--output", help="the filename of the csv output file")
    args = parser.parse_args()
    crawler = GoogleReviewsCrawler(search=args.search, output=args.output)
    crawler.run()
