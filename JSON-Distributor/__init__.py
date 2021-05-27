import logging
from io import StringIO
import os
import csv
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from .validation import Validate_Member
from.configsettings import ConfigSettings
import uuid


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes\n")

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(ConfigSettings.STORAGE_CONNECTION_STRING)

    # Create required containers (if they don't already exist)
    CreateContainersIfNotExist(ConfigSettings.STORAGE_CONNECTION_STRING, blob_service_client)

    # Extract the csv body from stream
    body = myblob.read().decode("utf-8")
    logging.info(f"raw body: {body}")

    # Parse the body string
    csv_reader = csv.reader(body.split('\n'), delimiter='|')

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

            error_id = uuid.uuid1()
            logging.info(f"Error ID: {error_id}\n"
                        "Error Creating file. Check failed files container for details.")
            error_dict = { 'id': error_id, 'errors': errors, 'body': row_dict }
            # Create file
            with open(f"{error_id}", "w") as outfile:
                json.dump(error_dict, outfile)
        else:
            # Create a file name and body
            filename = f"{row_dict['agency_abbrev']}-{row_dict['title']}-{row_dict['first_name']}-{row_dict['last_name']}.json"
            file_body = json.dumps(row_dict, indent = 4)

            # Write JSON data to the file
            file = open(filename, 'w')
            file.write(file_body)
            file.close()

            # Create the blob client
            blob_client = blob_service_client.get_blob_client(container=ConfigSettings.JSON_FILES_CONTAINERNAME, blob=filename)

            # Upload the file
            with open(filename, 'rb') as outfile:
                blob_client.upload_blob(outfile)
            
            logging.info(f"File Created: {row_dict['agency_abbrev']}-{row_dict['title']}-{row_dict['first_name']}-{row_dict['last_name']}.json")

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