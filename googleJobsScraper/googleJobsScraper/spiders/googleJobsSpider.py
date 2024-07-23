import asyncio
from googleJobsScraper.items import GooglejobsscraperItem
import scrapy
from scrapy_playwright.page import PageMethod


class GooglejobsspiderSpider(scrapy.Spider):
    name = "googleJobsSpider"

    # Method to build the url that will be used to get the data
    def getRequestUrl(self, keyword):
        # Return the base url with parameters encoded
        return "https://www.google.com/search?hl=en&q=" + keyword + "&ibp=htl;jobs"
    
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
            googleUrl = self.getRequestUrl(keyword)
            yield scrapy.Request(
                url=googleUrl,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_timeout', 5000),
                    ],
                    'dont_redirect': True,
                    'tableName': location,
                },
                errback=self.errback
            )

    # Parse through the response and collect data
    async def parse(self, response):
        # Grab the page from the playwright meta data
        page = response.meta["playwright_page"]
        # Scroll down page
        # FOR SOME REASON INFINITE SCROLLING NOT WORKING
        div_selector = "div.zxU94d"
        await page.wait_for_selector(div_selector)
        for i in range(1,12):
            quote_count = 10 * i
            # await page.wait_for_selector(f".iFjolb:nth-child({quote_count})")
            await page.evaluate(f"""
                let div = document.querySelector("div.zxU94d");
                div.scrollTop = div.scrollHeight;
            """)
        screenshot = await page.screenshot(path="example.png", full_page=True)
        # Wait for the page content
        html = await page.content()
        # Wait for the page to close
        await page.close()
        # Get all jobs from the html content and store in new response variable
        newResponse = scrapy.Selector(text=html)
        # Get key data from each partial job view
        jobID = newResponse.xpath("//li[@class='iFjolb gws-plugins-horizon-jobs__li-ed']/@data-ved").extract()
        jobTitle = newResponse.xpath("//div[@class='BjJfJf PUpOsf']/text()").extract()
        jobCompany = newResponse.xpath("//div[@class='vNEEBe']/text()").extract()
        jobLocation = newResponse.xpath("//div[@class='Qk80Jf']/text()").extract()
        # briefDescription = newResponse.xpath("").extract() # Doesn't work
        timeAgoPosted = newResponse.xpath("//span[@class='LL4CDc' and contains(@aria-label, 'Posted')]/span/text()").extract()
        jobUrl = newResponse.xpath("//div[@data-share-url]/@data-share-url").extract()

        # Loop through arrays from parsing and build IndeedScraperItems
        for i in range(len(jobTitle)):
            jobItem = GooglejobsscraperItem()

            # Set tableName
            jobItem['tableName'] = response.meta['tableName']

            jobItem['jobID'] = jobID[i].strip() if i < len(jobID) else None
            jobItem['title'] = jobTitle[i].strip() if i < len(jobTitle) else None
            jobItem['company'] = jobCompany[i].strip() if i < len(jobCompany) else None
            jobItem['location'] = jobLocation[i].strip() if i < len(jobLocation) else None
            #jobItem['partDescription'] = briefDescription[i].strip() if i < len(briefDescription) else None
            jobItem['time'] = timeAgoPosted[i] if i < len(timeAgoPosted) else None
            jobItem['url'] = jobUrl[i].strip() if i < len(jobUrl) else None

            # List of fields to check
            fields_to_check = ['jobID', 'title', 'company', 'location', 'time', 'url']

            # Check for None fields and send email if any of them are
            for field in fields_to_check:
                if jobItem[field] is None:
                    # SEND EMAIL
                    pass

            yield jobItem
            # Use this and comment out above yield jobItem to parse each full job
            """
            yield scrapy.Request(url=jobItem["url"], callback=self.parseFullJob, meta={'data' : jobItem})
            """

    # Go into each job and get things like full job description and external link
    def parseFullJob(self, response):
        pass

        # Method called when playwright generates an error
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        self.logger.error(repr(failure))
