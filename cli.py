import argparse

import scrapy.crawler

from google_reviews.spiders.googlereviewspider import GoogleReviewsSpider
from log.logger import logger

# e.g. args.search "Neni Berlin"

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--search", help="search for  business")
parser.add_argument("-o", "--output", help="the CSV file name of output file")
args = parser.parse_args()


if __name__ == "__main__":
    if not args.search:
        raise "please enter a correct search venue"

    process = scrapy.crawler.CrawlerProcess()
    if args.output:
        process.crawl(
            GoogleReviewsSpider, search_term=args.search, csv_filename=args.output
        )
    else:
        process.crawl(GoogleReviewsSpider, search_term=args.search)
    process.start()
