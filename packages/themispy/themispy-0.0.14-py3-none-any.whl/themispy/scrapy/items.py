# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FileDownloader(scrapy.Item):
    """
    Scrapy Item Class defined for downloading files.
    
    Attributes are:
    * 'file_urls': stores the urls used for downloading files.
    * 'files': stores metadata info about downloading process.
    """
    file_urls = scrapy.Field() # Do not rename this!
    files = scrapy.Field() # Do not rename this!
