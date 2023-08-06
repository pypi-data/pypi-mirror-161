import scrapy
import ast
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import Join

from elt.extract.jobs_crawler.items import JobsCrawlerItem


class WttjSpider(scrapy.Spider):
    """
    Spider to scrape jobs information on Welcome to the Jungle Website.
    The individual pages are not rendered with Javascript so it only uses Scrapy.
    """
    name = 'wttj'

    @staticmethod
    def extract_links():
        with open('wttj_links.txt', 'r') as f:
            links = ast.literal_eval(f.read())
            return links

    def start_requests(self):
        links = self.extract_links()
        for link in links:
            yield scrapy.Request(link, self.yield_job_item)

    def yield_job_item(self, response):
        l = ItemLoader(item=JobsCrawlerItem(), response=response)
        l.add_value('url', response.url)
        l.add_value('title', response.xpath('//*[text()="Le poste"]/parent::h4/following-sibling::h4/text()').get())
        l.add_value('company',
                    response.xpath('//*[text()="La tribu"]/parent::h4/following-sibling::a//text()').get())
        l.add_value('remote',
                    response.xpath('//*[@name="remote"]/parent::span/following-sibling::span//text()').get())
        l.add_value('location',
                    response.xpath('//*[@name="location"]/parent::span/following-sibling::span/text()').get())
        l.add_value('type',
                    response.xpath('//*[@name="contract"]/parent::span/following-sibling::span/span/text()').get())
        l.add_value('industry',
                    response.xpath('//*[@name="tag"]/parent::span/following-sibling::span/text()').get())
        l.add_value('text',
                    response.xpath('//h2/following-sibling::div//text()').getall(), Join())
        l.add_value('created_at', datetime.now())
        yield l.load_item()


if __name__ == '__main__':
    process = CrawlerProcess(
        settings={
            'ROBOTSTXT_OBEY': False,
            'ITEM_PIPELINES': {'elt.extract.jobs_crawler.pipelines.JobsCrawlerPipeline': 300, },
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,
            'AUTOTHROTTLE_START_DELAY': 5,
            'AUTOTHROTTLE_MAX_DELAY': 60
        }
    )
    process.crawl(WttjSpider)
    process.start()
