# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobsCrawlerItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    type = scrapy.Field()
    industry = scrapy.Field()
    text = scrapy.Field()
    remote = scrapy.Field()
    created_at = scrapy.Field()


