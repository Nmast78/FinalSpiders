import scrapy
from typing import Iterable
from monsterScraper.items import MonsterscraperItem
from scrapy_playwright.page import PageMethod
import json
from bs4 import BeautifulSoup

class MonsterspiderSpider(scrapy.Spider):
    name = "monsterSpider"

    # Method to build the url that will be used to get the data
    def getRequestUrl(self, keyword):
        # Return the base url with parameters encoded
        #return "https://www.google.com/search?q=" + keyword
        return "https://www.google.com/search?q=Internship+in+Arkansas&ibp=htl;jobs" 

    # CODE STARTS HERE Update test
    # This method calls the request method on a url and sets the callback so the response will go to the parse method
    def start_requests(self):
        # Define the list of all 50 states
        locationList = ["Arkansas"]
        """
        locationList = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii",
                                      "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
                                      "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
                                      "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
                                      "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
        """

        # For each state get the url and call scrapy request
        for location in locationList:
            keyword = "Internship+in+" + location
            monsterUrl = self.getRequestUrl(keyword)
            yield scrapy.Request(
                url=monsterUrl,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_timeout', 5000)
                    ],
                    'location': location,
                    'dont_redirect': True,
                },
                errback=self.errback
            )

    async def parse(self, response):
        # Grab the page from the playwright meta data
        page = response.meta["playwright_page"]
        #jobs = response.xpath("//a[@class='esVihe']/@href").extract()  
        jobID = response.xpath("//div[@class='BjJfJf PUpOsf']/text()").extract()
        screenshot = await page.screenshot(path="example.png", full_page=True)
        # Wait for the page to close
        await page.close()

    # Go into each job and get things like full job description and external link
    async def parseFullJob(self, response):
        pass
    
    # Method called when playwright generates an error
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        self.logger.error(repr(failure))
