from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os
import glob

# Azure Storage Configuration
connection_string = os.getenv("AZURE_CONNECTION_STRING")  # Ensure this is set in your environment
container_name = "proteinfold"

def generate_sas_url(blob_service_client, container_name, blob_path, expiry_hours=1):
    """
    Generates a SAS token for a given blob.

    Args:
    - blob_service_client: BlobServiceClient instance.
    - container_name (str): Azure Blob Storage container name.
    - blob_path (str): Path to the blob inside the container.
    - expiry_hours (int): SAS token expiry time in hours.

    Returns:
    - str: URL with SAS token for the blob.
    """
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_path,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),  # Grant read permission
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_path}?{sas_token}"

def upload_task_outputs(task_id, task_output_folder):
    """
    Uploads all files in the task output folder to Azure Blob Storage and returns SAS URLs.

    Args:
    - task_id (str): Unique task identifier.
    - task_output_folder (str): Local directory containing output files.

    Returns:
    - dict: Contains task_id and list of file SAS URLs.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        files = glob.glob(os.path.join(task_output_folder, "*"))
        uploaded_files = []

        for file_path in files:
            filename = os.path.basename(file_path)
            blob_path = f"freewilson/{task_id}/{filename}"  
            blob_client = container_client.get_blob_client(blob_path)

            with open(file_path, "rb") as file:
                blob_client.upload_blob(file, overwrite=True)

            # Generate SAS URL
            sas_url = generate_sas_url(blob_service_client, container_name, blob_path)
            uploaded_files.append(sas_url)

        return {"task_id": task_id, "uploaded_files": uploaded_files}

    except Exception as e:
        return {"error": str(e)}
