import scrapy
import ast
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import Join

from elt.extract.jobs_crawler.items import JobsCrawlerItem


class SpotifySpider(scrapy.Spider):

    name = 'spotify'

    @staticmethod
    def extract_links():
        with open('spotify_links.txt', 'r') as f:
            links = ast.literal_eval(f.read())
            return links

    def start_requests(self):
        links = self.extract_links()
        for link in links:
            yield scrapy.Request(link, self.yield_job_item)

    def yield_job_item(self, response):
        l = ItemLoader(item=JobsCrawlerItem(), response=response)

        l.add_value('url', response.url)

        title = response.xpath('//h1/span/text()').get()
        subtitle = response.xpath('//h1/text()').get()
        if subtitle:
            job_title = title + '- ' + subtitle
        else:
            job_title = title
        l.add_value('title', job_title)

        l.add_value('company', 'Spotify')

        remote = response.xpath('//span[text()="Remote EMEA"]').get()
        if remote == 'Remote EMEA':
            l.add_value('remote', 'Remote EMEA')

        l.add_value('location',
                    response.xpath('//p[text()="Location"]/parent::div//span/text()').get())

        l.add_value('type',
                    response.xpath('//p[text()="Job type"]/following-sibling::p/text()').get())

        l.add_value('industry', 'NA')

        l.add_value('text',
                    response.xpath('//div[contains(@class, "singlejob_rightContent")]/div[1]//text()').getall(), Join())

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
    process.crawl(SpotifySpider)
    process.start()
