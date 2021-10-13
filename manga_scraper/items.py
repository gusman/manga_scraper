# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MangaScraperItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    chapter = scrapy.Field() 
    pages = scrapy.Field()
