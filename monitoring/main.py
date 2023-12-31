import os
from minio import Minio
import time

# MinIO server configuration
MINIO_ENDPOINT = '192.168.1.54:9000'
MINIO_ACCESS_KEY = 'monitor'
MINIO_SECRET_KEY = 'FfmTeua5Esd7ius4zi48Qz5lCg3NXx0ilOMIATtu'
MINIO_BUCKET_NAME = 'sd-new'

# Folder to monitor
MONITOR_FOLDER = '/path/to/folder_to_monitor'  # Use forward slashes for Linux

# Path to the file for saving uploaded file names
UPLOADED_FILES_FILE = 'uploaded_files.txt'

# Create MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Function to upload a file to MinIO


def upload_file(file_path):
    file_name = os.path.basename(file_path)

    # Ignore *.tmp files
    if file_name.endswith('.tmp'):
        print(f"Ignoring {file_path} (tmp file)")
        return

    # Check if file has already been uploaded
    if file_name in uploaded_files:
        print(f"File {file_path} already uploaded")
        return

    try:
        # Remove Windows folders above the monitoring directory from the file path
        relative_path = os.path.relpath(file_path, MONITOR_FOLDER)
        object_name = relative_path.replace(
            '\\', '/')  # Use forward slash for Linux

        # Upload the file to MinIO
        minio_client.fput_object(MINIO_BUCKET_NAME, object_name, file_path)

        # Add the uploaded file name to the set of uploaded files
        uploaded_files.add(file_name)

        print(f"Uploaded {file_path} to MinIO")
    except Exception as e:
        print(f"Error uploading {file_path} to MinIO: {str(e)}")

# Function to monitor the folder and subfolders for new files


def monitor_folder():
    for root, _, files in os.walk(MONITOR_FOLDER):
        for file in files:
            # Construct the full file path
            file_path = os.path.join(root, file)
            upload_file(file_path)


if __name__ == "__main__":
    uploaded_files = set()

    while True:
        monitor_folder()
        time.sleep(60)  # Check for new files every 60 seconds
