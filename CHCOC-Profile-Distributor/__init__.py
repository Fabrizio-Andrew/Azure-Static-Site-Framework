import logging
from io import StringIO
import csv
import json
import azure.functions as func
from .validation import Validate_Member
import uuid


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes\n")

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
            with open(f"{row_dict['agency_abbrev']}-{row_dict['title']}-{row_dict['first_name']}-{row_dict['last_name']}.json", 'w') as outfile:
                json.dump(row_dict, outfile)
            logging.info(f"File Created: {row_dict['agency_abbrev']}-{row_dict['title']}-{row_dict['first_name']}-{row_dict['last_name']}.json")

