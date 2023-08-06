# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
from io import BytesIO

from azure.storage.blob import ContainerClient
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.misc import md5sum

from themispy.azure.tools import get_connection_string, INGESTION_PATH
from themispy.project.utils import PROJECT_TITLE, split_filepath
  

class BlobUploadPipeline:
    """
    Custom class created in order to upload blobs to Azure Storage.
    The connection to Azure Storage is made during the 'process_item'
    method in the Item Pipeline phase.
    """
    def open_spider(self, spider):
        self.container_client = ContainerClient.from_connection_string(
            conn_str=get_connection_string(),
            container_name=INGESTION_PATH
        )
        
        self.blob_client = self.container_client.get_blob_client(f"{spider.name}.jsonl")

    
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + '\n'
        self.blob_client.upload_blob(data=line, blob_type='AppendBlob')
        return item

    
class FileDownloaderPipeline(FilesPipeline):
    """
    Custom class created in order to upload downloaded files to Azure Storage.
    Even though you don't actually store downloaded files locally, you still must
    pass a 'FILES_STORE' value to your spider settings.
    """
    def file_downloaded(self, response, request, info, *, item=None):
        path = self.file_path(request, response=response, info=info, item=item)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        
        # Azure Container Client
        container_client = ContainerClient.from_connection_string(
            conn_str=get_connection_string(),
            container_name=INGESTION_PATH
        )
        
        # Blob Upload
        docname, docext = split_filepath(response.url)
        blob_client = container_client.get_blob_client(f"{PROJECT_TITLE}_{docname}{docext}")
        blob_client.upload_blob(data=buf)
        return checksum
