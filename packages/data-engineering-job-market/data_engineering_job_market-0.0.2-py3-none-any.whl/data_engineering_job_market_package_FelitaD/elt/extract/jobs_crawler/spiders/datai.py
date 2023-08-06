import re
import math
import scrapy
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from datetime import datetime

from elt.extract.jobs_crawler.items import JobsCrawlerItem
from itemloaders.processors import MapCompose, Join


class DataiSpider(scrapy.Spider):
    """
    Spider designed to scrape datAI.jobs website.
    """
    name = 'datai'
    start_urls = ['https://datai.jobs/jobs/?s=data+engineer&post_type=job_listing&search_location&filter_job_listing_region=europe&query_type_job_listing_region=or']

    def parse(self, response):
        """ Parse 1st page of results and obtain the total number of pages to scrape. """
        results_string = response.xpath('//*[@class="showing_jobs"]//text()').get()
        total_results = re.search('(?<=of.)\d+(?=.jobs)', results_string).group(0)
        number_of_pages = math.ceil(int(total_results)/30)

        for page_number in range(1, number_of_pages + 1):
            page_url = f'https://datai.jobs/jobs/page/{page_number}/?s=data+engineer&post_type=job_listing' \
                       '&search_location&filter_job_listing_region=europe&query_type_job_listing_region=or'
            yield scrapy.Request(page_url, self.parse_jobs_list)

    def parse_jobs_list(self, response):
        """ Parse all pages of jobs listing and access individual job pages. """
        jobs_page = response.xpath('//*[@class="job_listings list"]/li/a/@href').getall()
        for job_page in jobs_page:
            yield scrapy.Request(job_page, self.yield_job_item)

    def yield_job_item(self, response):
        l = ItemLoader(item=JobsCrawlerItem(), response=response)
        l.add_value('url', response.url)
        l.add_value('title', response.xpath('//*[@class="site-content-page-title"]/text()').get())
        l.add_value('company', response.xpath('//*[@class="single-job-listing-company__name"]//text()').get())
        l.add_value('location', response.xpath('//*[@class="google_map_link"]//text()').get())
        l.add_value('type', response.xpath('//*[@class="job-types"]/li/text()').get(),
                    MapCompose(str.strip))
        l.add_value('industry', response.xpath('//*[contains(text(), "Industry")]/parent::div/*['
                                               '@class="single-job-listing-overview__detail-content--value"]//text('
                                               ')').get())
        l.add_value('text', response.xpath('//*[@class="single-job-listing__description job-description"]//text()').getall(),
                    Join(''))
        l.add_value('created_at', datetime.now())
        return l.load_item()


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
    process.crawl(DataiSpider)
    process.start()