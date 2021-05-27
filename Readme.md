# Summary

This framework uses an Azure function to consume an uploaded csv file, convert the data to JSON files, and store those files in blob containers.

The resulting JSON files can be queried by static websites directly from Azure Blob Storage.

A very basic UI is included in the Static folder.  It currently incorporates elements of USWDS and the chcoc.gov website.

# Getting Started

- Fork the framework repository to create a new repository for each new site to be created.
- Pull site repository to local machine.
- Install requirements.txt
- Using a python virtual environment is recommended. (I used pyenv)
- Create a local.settings.json file with your Azure Storage connection string
- Set the names of your containers via JSON-Distributor configsettings.py file (optional)

# Setting up Azure Storage

The Content distributor requires 1 container to be set up by default - the uploads container.  (If a different name is used for this container, the binding path must also be updated in function.json.) The uploads container should be set to "private" settings.

All other containers are automatically created by the JSON-Distributor (if they don't already exist.)

To query JSON content from storage containers, ensure that a CORS policy is set for your storage account to allow GET requests from everywhere (*).