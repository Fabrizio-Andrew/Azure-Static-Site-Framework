import logging
from io import StringIO
import csv

import azure.functions as func


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes\n")

    body = myblob.read().decode("utf-8")
    logging.info(f"raw body: {body}")

    csv_reader = csv.reader(body.split('\n'), delimiter='|')
    for row in csv_reader:
        logging.info(row)
    parsed_csv = list(csv_reader)
    logging.info(f"parsed csv: {parsed_csv}")
