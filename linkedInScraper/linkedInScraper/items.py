import scrapy

class LinkedinscraperItem(scrapy.Item):
    jobID = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    partDescription = scrapy.Field()
    time = scrapy.Field()
    url = scrapy.Field()
    fullAddress = scrapy.Field()
    extUrl = scrapy.Field()
    fullDescription = scrapy.Field()
