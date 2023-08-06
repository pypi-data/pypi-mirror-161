import datetime
import json

from themispy.project.utils import PROJECT_PATH, build_path


# Azure Storage Connection
def get_connection_string() -> str:
    """Get Azure Web Jobs Storage Key from 'local.settings.json'."""
    with open(build_path('local.settings.json')) as local_settings:
        return json.load(local_settings)['Values']['AzureWebJobsStorage']


# Azure Storage Ingestion Relative Path
def build_ingestion_path(base_container: str = 'ingestion',
                         dir_partition: str = '/mining/') -> str:
    INGESTION_PATH = PROJECT_PATH.partition(dir_partition)[2] \
        + datetime.datetime.now().strftime('/%Y/%m/%d')
    INGESTION_PATH = f"{base_container}/{INGESTION_PATH}"
    return INGESTION_PATH

INGESTION_PATH = build_ingestion_path()
