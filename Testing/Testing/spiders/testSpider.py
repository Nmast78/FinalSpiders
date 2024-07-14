import scrapy

class TestspiderSpider(scrapy.Spider):
    name = "testSpider"

    def start_requests(self):
        yield scrapy.Request(url='http://quotes.toscrape.com/js/', callback=self.parse, meta=dict(playwright = True, playwright_include_page = True,))

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        print(response)
        #input("Press Enter to continue...")
        test = response.xpath("//span[@class='text']/text()").extract()
        print("Test output: ")
        print(test)