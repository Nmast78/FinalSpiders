# Define here the models for your scraped items
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZipRecruiterscraperItem(scrapy.Item):
    tableName = scrapy.Field()
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
