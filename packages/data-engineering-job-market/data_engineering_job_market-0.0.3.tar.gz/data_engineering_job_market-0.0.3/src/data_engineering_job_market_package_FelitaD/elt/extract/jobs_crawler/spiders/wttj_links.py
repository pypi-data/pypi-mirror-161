import scrapy
from scrapy.crawler import CrawlerProcess


class WttjLinksSpider(scrapy.Spider):
    """
    This Spider is used to render Javascript. It outputs all job links into a file.
    """
    name = 'wttj_links'
    start_urls = ['https://www.welcometothejungle.com/fr/jobs?page={page_number}&aroundQuery=&query=data%20engineer&refinementList%5Bcontract_type_names.fr%5D%5B%5D=CDI&refinementList%5Bcontract_type_names.fr%5D%5B%5D=CDD%20%2F%20Temporaire&refinementList%5Bcontract_type_names.fr%5D%5B%5D=Autres&refinementList%5Bcontract_type_names.fr%5D%5B%5D=VIE&refinementList%5Bcontract_type_names.fr%5D%5B%5D=Freelance']

    BASE_URL = 'https://www.welcometothejungle.com'

    links = set()

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0].format(page_number=1),
                             self.parse_jobs_list,
                             meta={"playwright": True, "playwright_include_page": True})

    async def parse_jobs_list(self, response):
        """ Parse javascript rendered results page and obtain individual job page links. """
        page = response.meta['playwright_page']

        job_elements = await page.query_selector_all('//*[@class="ais-Hits-list-item"]//a')
        for job_element in job_elements:
            job_link = await job_element.get_attribute('href')
            job_url = self.BASE_URL + job_link
            self.links.add(job_url)

        while True:
            try:
                next_locator = page.locator('//*[@aria-label="Next page"]')
                async with page.expect_navigation():
                    await next_locator.click()

                job_elements = await page.query_selector_all('//*[@class="ais-Hits-list-item"]//a')
                for job_element in job_elements:
                    job_link = await job_element.get_attribute('href')
                    job_url = self.BASE_URL + job_link
                    self.links.add(job_url)
            except TimeoutError:
                print("Cannot find a next button on ", page.url)
                break
            finally:
                with open('wttj_links.txt', 'w') as f:
                    f.write(str(self.links))

        await page.close()


if __name__ == '__main__':
    process = CrawlerProcess(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                # "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
            "CONCURRENT_REQUESTS": 32,
            'ROBOTSTXT_OBEY': False,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,
            'AUTOTHROTTLE_START_DELAY': 5,
            'AUTOTHROTTLE_MAX_DELAY': 60
        }
    )
    process.crawl(WttjLinksSpider)
    process.start()
