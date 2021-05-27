import logging
from io import StringIO
import os
import csv
import json
import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from .validation import Validate_Member
from.configsettings import ConfigSettings
import uuid


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes\n")

    timestamp = datetime.datetime.now()

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(ConfigSettings.STORAGE_CONNECTION_STRING)

    # Create required containers (if they don't already exist)
    CreateContainersIfNotExist(ConfigSettings.STORAGE_CONNECTION_STRING, blob_service_client)

    # Extract the csv body from stream
    body = myblob.read().decode("utf-8")
    logging.info(f"raw body: {body}")

    try: 
        # Parse the body string
        csv_reader = csv.reader(body.split('\n'), delimiter='|')

        # Store a copy of the uploaded original in the archive container
        filename = myblob.name + "_" + str(timestamp)
        UploadBlob(filename, body, ConfigSettings.ARCHIVE_CONTAINERNAME, blob_service_client)
        
    except:
        # Catch invalid file formats
        error_id = uuid.uuid1()
        logging.info(f"Error ID: {error_id} Uploaded file format is invalid.")
        error_dict = { "error": {myblob.name: "Invalid Format"}, "body": body }
        filename = f"{error_id}_file_format_error.json"

        # Convert error dict to json string
        file_body = json.dumps(error_dict, indent = 4)

        UploadBlob(filename, file_body, ConfigSettings.ERROR_FILES_CONTAINERNAME, blob_service_client)
        raise Exception(f"Error ID: {error_id} Uploaded file format is invalid.")

    # The first row of the csv is a list of table headers
    key = next(csv_reader)

    for row in csv_reader:
        row_dict = {}
        i=0

        # For however many values in row, append it to the dict with the corresponding key
        for value in row:
            row_dict[key[i]] = value
            i+=1

        # Validate the resulting dict
        errors = Validate_Member(row_dict)
        if len(errors) > 0:

            # Create unique error file name and body
            error_id = uuid.uuid1()
            logging.info(f"Error ID: {error_id}\n"
                "Error Creating JSON file. Check failed files container for details.")
            filename = f"{error_id}_row_validation_error.json"
            error_dict = { 'id': error_id, 'errors': errors, 'body': row_dict }
            
            # Convert error dict to json string
            file_body = json.dumps(error_dict, indent = 4)

            UploadBlob(filename, file_body, ConfigSettings.ERROR_FILES_CONTAINERNAME, blob_service_client)
            
        else:
            # Create a file name and body
            filename = f"{row_dict['agency_abbrev']}-{row_dict['title']}-{row_dict['first_name']}-{row_dict['last_name']}.json"
            file_body = json.dumps(row_dict, indent = 4)

            UploadBlob(filename, file_body, ConfigSettings.JSON_FILES_CONTAINERNAME, blob_service_client)
            
            logging.info(f"File Created: {filename}")

"""
Creates the JSON, ERROR, and ARCHIVE containers if they do not already exist.
"""
def CreateContainersIfNotExist(connection_string, blob_service_client):

    # Create the JSON container (if it doesn't already exist)
    json_container = ContainerClient.from_connection_string(connection_string, ConfigSettings.JSON_FILES_CONTAINERNAME)
    try:
        container_properties = json_container.get_container_properties()
    except Exception as e:
        json_container = blob_service_client.create_container(ConfigSettings.JSON_FILES_CONTAINERNAME)

    # Create the error container (if it doesn't already exist)
    error_container = ContainerClient.from_connection_string(connection_string, ConfigSettings.ERROR_FILES_CONTAINERNAME)
    try:
        container_properties = error_container.get_container_properties()
    except Exception as e:
        json_container = blob_service_client.create_container(ConfigSettings.ERROR_FILES_CONTAINERNAME)

    # Create the archive container (if it doesn't already exist)
    archive_container = ContainerClient.from_connection_string(connection_string, ConfigSettings.ARCHIVE_CONTAINERNAME)
    try:
        container_properties = archive_container.get_container_properties()
    except Exception as e:
        json_container = blob_service_client.create_container(ConfigSettings.ARCHIVE_CONTAINERNAME)

def UploadBlob(filename, file_body, cont, blob_service_client):

    # Write data to the file
    file = open(filename, 'w')
    file.write(file_body)
    file.close()

    # Create the blob client
    blob_client = blob_service_client.get_blob_client(container=cont, blob=filename)

    # Upload the file
    with open(filename, 'rb') as outfile:
        blob_client.upload_blob(outfile)
