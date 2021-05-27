import os

# Contains configuration settings for the JSON Distributor

class ConfigSettings:
    STORAGE_CONNECTION_STRING = os.environ['chcocgov_STORAGE']

    JSON_FILES_CONTAINERNAME = 'jsonfiles'
    
    ERROR_FILES_CONTAINERNAME = 'errorfiles'

    ARCHIVE_CONTAINERNAME = 'archivefiles'

    BLOB_FILENAME = 'blob.csv'

