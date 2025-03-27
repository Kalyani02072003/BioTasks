import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Storage details
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")  # Load from .env
AZURE_BLOB_CONTAINER = "biotex"  
BLOB_NAME = "proteinfold"
DOWNLOAD_PATH = "downloaded_file.txt"  # Local path to save the file

# Create BlobServiceClient using the connection string
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

# Get container client
container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)

# Download the blob
blob_client = container_client.get_blob_client(BLOB_NAME)
with open(DOWNLOAD_PATH, "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())

print(f"File '{BLOB_NAME}' downloaded successfully as '{DOWNLOAD_PATH}'")
