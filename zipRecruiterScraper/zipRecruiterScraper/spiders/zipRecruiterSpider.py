from zipRecruiterScraper.items import ZipRecruiterscraperItem
import scrapy
from urllib.parse import urlencode
from scrapy_playwright.page import PageMethod
import json
from bs4 import BeautifulSoup
import math
import re

class ZiprecruiterspiderSpider(scrapy.Spider):
    name = "zipRecruiterSpider"

    # Method to build the url that will be used to get the data
    def getRequestUrl(self, keyword, location):
        # Define parameters
        parameters = {'search' : keyword, 'location' : location}
        # Return the base url with parameters encoded
        return "https://www.ziprecruiter.com/jobs-search?" + urlencode(parameters)

    # CODE STARTS HERE
    # This method calls the request method on a url and sets the callback so the response will go to the parse method
    def start_requests(self):
        # Define keyword and the list of all 50 states
        keyword = "Internship"
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
            zipRecruiterUrl = self.getRequestUrl(keyword, location)
            yield scrapy.Request(
                url=zipRecruiterUrl,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_timeout', 5000)
                    ],
                    'location': location
                },
                errback=self.errback
            )

    # Parse through the response and collect data
    async def parse(self, response):
        totalJobCount = 0
        # Get location from metadata to construct new url in here
        location = response.meta.get('location')
        # Grab the page from the playwright meta data
        page = response.meta["playwright_page"]
        # Wait for the page to close
        await page.close()

        # Grab the script from the response
        dataObject = response.xpath("//div[@class='site_content']/script[@id='js_variables']").extract()

        # If we get something continue
        if dataObject:
            # Join list into string
            dataObject = ''.join(dataObject)
            # Initialize BS object to parse html
            soup = BeautifulSoup(dataObject, 'lxml')
            # Find the script tag
            script_tag = soup.find('script', {'id': 'js_variables'})

            # If our script tag exists continue
            if script_tag:
                json_content = script_tag.string.strip()
                data = json.loads(json_content)
                totalJobCount = data.get('totalJobCount')
                # Get the jobList data from our json object
                job_list = data.get('jobList', [])
                for job in job_list:
                    locationMatch = re.search(r"location=([^']+)", job.get('LocationURL')) 
                    jobItem = ZipRecruiterscraperItem()
                    
                    jobItem['jobID'] = None
                    jobItem['title'] = job.get('Title') or None
                    jobItem['company'] = job.get('OrgName') or None
                    jobItem['location'] = job.get('Locations') or locationMatch.group(1) or None
                    jobItem['partDescription'] = None
                    jobItem['time'] = job.get('PostedTime') or None
                    jobItem['url'] = job.get('JobURL') or None

                    yield jobItem
                    # Use this and comment out above yield jobItem to parse each full job
                    """
                    yield scrapy.Request(
                        url=jobItem['url'],
                        callback=self.parseFullJob,
                        meta={
                            'playwright': True,
                            'playwright_include_page': True,
                            'playwright_page_methods': [
                                PageMethod('wait_for_timeout', 5000)
                            ],
                            'location': location
                        },
                        errback=self.errback
                    )
                    """
            else:
                # EMAIL HERE
                pass

        # Call the getNextUrl method to get the next page
        """
        numPages = math.ceil(totalJobCount / 20)
        for num in range(2, numPages):
            next_request = await self.getNextUrl(response.meta['location'], num)
            if next_request:
                yield next_request
        """
    
    # Method to build next page url
    async def getNextUrl(self, location, num):
        keyword = "Internship"
        # Define parameters
        parameters = {'search' : keyword, 'location' : location, 'page' : num}
        # Return the base url with parameters encoded
        zipRecruiterUrl = "https://www.ziprecruiter.com/jobs-search?" + urlencode(parameters)
        # Return scrapy request to parse method
        return scrapy.Request(
                url=zipRecruiterUrl,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_timeout', 5000)
                    ],
                    'location': location
                },
                errback=self.errback
        )
    
    # Go into each job and get things like full job description and external link
    async def parseFullJob(self, response):
        pass
    
    # Method called when playwright generates an error
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        self.logger.error(repr(failure))

