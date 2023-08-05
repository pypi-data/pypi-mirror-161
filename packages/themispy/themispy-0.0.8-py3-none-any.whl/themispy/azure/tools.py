import datetime
import json

from themispy.project.utils import PROJECT_PATH, build_path


# Azure Storage Connection
def get_connection_string() -> str:
    """Get Azure Web Jobs Storage Key from 'local.settings.json'."""
    with open(build_path('local.settings.json')) as local_settings:
        return json.load(local_settings)['Values']['AzureWebJobsStorage']


# Azure Storage Ingestion Relative Path
INGESTION_PATH = PROJECT_PATH.partition('/mining/')[2] \
    + datetime.datetime.now().strftime('/%Y/%m/%d')
