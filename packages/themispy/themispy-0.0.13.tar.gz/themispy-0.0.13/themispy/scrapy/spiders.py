from multiprocessing import Process, Queue

from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor


def run_spider(spider: Spider, pipeline: str = None,
               settings: dict = None, override: bool = False,
               project_name: str = 'scraping') -> None:
    """
    Process for running spiders.
    
    Attributes are:
    * 'spider': Spider Class used for crawling.
    * 'pipeline': Must be either 'blob' or 'download'.
    * 'settings': Scrapy Settings object.
    * 'override': If set to 'True', the settings passed will
    override all previous settings.
    """
    if pipeline is not None and pipeline != 'blob' and pipeline !='download':
        raise Exception("Pipeline must be either 'blob' or 'download'.")
    
    # Configure Scrapy Project Settings
    scrapy_settings = get_project_settings()
    
    if pipeline == 'blob':
        scrapy_settings.update({
            'ITEM_PIPELINES': {f'{project_name}.{project_name}.pipelines.BlobUploadPipeline': 1}
        })
    elif pipeline == 'download':
        scrapy_settings.update({
            'ITEM_PIPELINES': {f'{project_name}.{project_name}.pipelines.FileDownloaderPipeline': 1},
            'FILES_STORE': 'Khipo-Themis_Project',
            'FILES_EXPIRES': 0
        })
    
    if settings is not None:
        if override:
            scrapy_settings = get_project_settings()
        
        scrapy_settings.update(settings)
    
    
    def multiprocess(queue: Queue) -> None:
        """Setup incoming spider running call for multiprocessing."""
        try:
            configure_logging(settings=scrapy_settings)
            runner = CrawlerRunner(settings=scrapy_settings)
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            queue.put(None)
        except Exception as e:
            queue.put(e)

    queue_ = Queue()
    process = Process(target=multiprocess, args=(queue_,))
    process.start()
    result = queue_.get()
    process.join()

    if result is not None:
        raise result
