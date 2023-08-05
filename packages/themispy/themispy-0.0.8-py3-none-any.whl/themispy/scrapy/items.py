# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FileDownloader(scrapy.Item):
    """
    Scrapy Item Class defined for downloading files.
    
    The only attribute is:
    * 'file_urls': stores the urls used for downloading files. Do not rename this.
    """
    file_urls = scrapy.Field() # Do not rename this
