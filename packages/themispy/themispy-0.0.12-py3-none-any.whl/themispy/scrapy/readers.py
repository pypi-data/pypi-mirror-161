from azure.storage.blob import ContainerClient

from themispy.azure.tools import get_connection_string, INGESTION_PATH
from themispy.project.utils import PROJECT_TITLE


def read_jsonl(container: str = INGESTION_PATH,
               attr: str = 'url',
               encoding: str = 'UTF-8') -> 'list[str]':
    """Reads all JSON Lines datasources from the specified container."""
    attr = f'"{attr}": "'
    
    container_client = ContainerClient.from_connection_string(
        conn_str=get_connection_string(),
        container_name=container
    )
    
    stream = container_client.download_blob(f"{PROJECT_TITLE}_crawler.jsonl")
    content, datasources = [], []
    
    for i in stream.content_as_text(encoding=encoding).split(attr):
        if i.startswith('http'):
            content.append(i)
        
    for i in content:
        idx = i.find('"')
        i = i[:idx]
        datasources.append(i)
    
    return datasources
