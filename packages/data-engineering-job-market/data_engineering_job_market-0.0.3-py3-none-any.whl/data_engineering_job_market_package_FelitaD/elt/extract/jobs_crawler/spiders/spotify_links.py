import scrapy
from scrapy.crawler import CrawlerProcess
from playwright._impl._api_types import TimeoutError


class SpotifyLinksSpider(scrapy.Spider):

    name = 'spotify_links'
    start_urls = ['https://www.lifeatspotify.com/jobs?c=engineering&c=data&l=remote-emea&l=stockholm&l=london&l=berlin&l=amsterdam&l=sweden-home-mix&l=copenhagen&l=germany-home-mix&l=barcelona&l=gothenburg']
    spotify_links = set()

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],
                             self.parse,
                             meta={"playwright": True, "playwright_include_page": True})

    async def parse(self, response):
        page = response.meta['playwright_page']
        print(page)

        while True:
            try:
                load_more_locator = page.locator('//button[@aria-label="Load more jobs"]')
                await load_more_locator.click()
            except TimeoutError:
                print("No more jobs to load.")
                break

        links = await page.query_selector_all('//a')
        for link in links:
            href = await link.get_attribute('href')
            if href.startswith('/jobs/'):
                self.spotify_links.add('https://www.lifeatspotify.com' + href)

        with open('spotify_links.txt', 'w') as f:
            f.write(str(self.spotify_links))


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
    process.crawl(SpotifyLinksSpider)
    process.start()