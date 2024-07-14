from urllib.parse import urlencode
import scrapy
import re
from indeedScraper.items import IndeedscraperItem
from lxml import html
from ..emailSender import send_email

class IndeedspiderSpider(scrapy.Spider):
    name = "indeedSpider"

    # Method to build the url that will be used to get the data
    def getRequestUrl(self, keyword, location):
        # Define parameters
        parameters = {'q': keyword, 'l': location}
        # Return the base url with parameters encoded
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

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
            indeedUrl = self.getRequestUrl(keyword, location)
            yield scrapy.Request(indeedUrl, callback=self.parse)

    # Parse through the response and collect data
    def parse(self, response):
        # Get key data from each partial job view
        jobID = response.xpath("//a[@class='jcs-JobTitle css-jspxzf eu4oa1w0']/@data-jk").extract()
        jobTitle = response.xpath("//a[@class='jcs-JobTitle css-jspxzf eu4oa1w0']/span/text()").extract()
        jobCompany = response.xpath("//span[@class='css-63koeb eu4oa1w0']/text()").extract()
        jobLocation = response.xpath("//div[@class='css-1p0sjhy eu4oa1w0']/text()").extract()
        briefDescription = response.xpath("//div[@class='css-9446fg eu4oa1w0']/text()").extract() # Doesn't work
        timeAgoPosted = response.xpath("//span[@class='css-qvloho eu4oa1w0']/text()").extract()
        jobUrl = response.xpath("//a[@class='jcs-JobTitle css-jspxzf eu4oa1w0']/@href").extract()

        # Remove non-breaking space characters in location field
        jobLocation = [location for location in jobLocation if location != '\xa0']
        # Grab digit from timeAgoPosted string
        timeAgoPosted = [int(re.findall(r'\d+', item)[0]) if re.findall(r'\d+', item) else 0 for item in timeAgoPosted]


        # Loop through arrays from parsing and build IndeedScraperItems
        for i in range(len(jobTitle)):
            jobItem = IndeedscraperItem()

            jobItem['jobID'] = jobID[i].strip() if i < len(jobID) else None
            jobItem['title'] = jobTitle[i].strip() if i < len(jobTitle) else None
            jobItem['company'] = jobCompany[i].strip() if i < len(jobCompany) else None
            jobItem['location'] = jobLocation[i].strip() if i < len(jobLocation) else None
            jobItem['partDescription'] = briefDescription[i].strip() if i < len(briefDescription) else None
            jobItem['time'] = timeAgoPosted[i] if i < len(timeAgoPosted) else None
            jobItem['url'] = "https://www.indeed.com" + jobUrl[i].strip() if i < len(jobUrl) else None

            # List of fields to check
            fields_to_check = ['jobID', 'title', 'company', 'location', 'partDescription', 'time', 'url']

            # Check for None fields and send email if any of them are
            for field in fields_to_check:
                if jobItem[field] is None:
                    # send_email(field)
                    pass

            yield jobItem
            # Use this and comment out above yield jobItem to parse each full job
            """
            yield scrapy.Request(url=jobItem["url"], callback=self.parseFullJob, meta={'data' : jobItem})
            """

        # Get link to next page if there is one. Call parse on that page
        """
        nextPage = response.xpath("//a[@class='css-akkh0a e8ju0x50']/@href").extract()
        if nextPage:
            nextPageLink = "https://www.indeed.com" + nextPage[0]
            yield scrapy.Request(nextPageLink, callback=self.parse)
        """

    # Go into each job and get things like full job description and external link
    def parseFullJob(self, response):
        jobItem = response.meta['data']
        # Get key data from full job page
        fullAddress = response.xpath("//div[@class='css-1ojh0uo eu4oa1w0']/text()").extract()[0]
        externalJobLink = response.xpath("//button[@class='css-1oxck4n e8ju0x51']/@href").extract()
        # Get desc and join all the individual parts into fullDesc
        desc = response.xpath("//div[@id='jobDescriptionText']//div | //div[@id='jobDescriptionText']//ul").extract()
        fullDesc = " ".join(desc)

        # Add items to job item
        jobItem['fullAddress'] = fullAddress or None
        jobItem['extUrl'] = externalJobLink or None
        jobItem['fullDescription'] = fullDesc or None

        # List of fields to check
        fields_to_check = ['fullAddress', 'extUrl', 'fullDescription']

        # Check for None fields and send email if any of them are
        for field in fields_to_check:
            if jobItem[field] is None:
                send_email(field)

        yield jobItem

