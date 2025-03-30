from azure.storage.blob import BlobServiceClient
import os
import glob

# Azure Storage Configuration
connection_string = os.getenv("AZURE_CONNECTION_STRING")  # Ensure this is set in your environment
container_name = "proteinfold"

def upload_task_outputs(task_id, task_output_folder):
    """
    Uploads all files in the task output folder to Azure Blob Storage.
    
    Args:
    - task_id (str): Unique task identifier.
    - task_output_folder (str): Local directory containing output files.
    
    Returns:
    - List of blob URLs for uploaded files.
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

            blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_path}"
            uploaded_files.append(blob_url)

        return {"task_id": task_id, "uploaded_files": uploaded_files}

    except Exception as e:
        return {"error": str(e)}
