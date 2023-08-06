from azure.storage.blob import BlobClient

from themispy.azure.tools import get_connection_string, INGESTION_PATH
from themispy.project.utils import PROJECT_TITLE


def read_jsonl(blob_name: str = f"{PROJECT_TITLE}_crawler.jsonl",
               conn_str: str = get_connection_string(),
               container: str = INGESTION_PATH, attr: str = 'url',
               encoding: str = 'UTF-8', startswith: str = 'http') -> 'list[str]':
    """Reads all JSON Lines datasources from the specified blob and container."""
    attr = f'"{attr}": "'
    
    blob_client = BlobClient.from_connection_string(
        conn_str=conn_str,
        container_name=container, blob_name=blob_name
    )
    
    stream = blob_client.download_blob()
    content, datasources = [], []
    
    for i in stream.content_as_text(encoding=encoding).split(attr):
        if i.startswith(f"'{startswith}'"):
            content.append(i)
        
    for i in content:
        idx = i.find('"')
        i = i[:idx]
        datasources.append(i)
    
    return datasources
