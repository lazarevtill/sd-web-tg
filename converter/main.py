import io
import os
import urllib.parse
from minio import Minio
from minio.error import ResponseError
from PIL import Image

# MinIO configuration
MINIO_ENDPOINT = 'your_minio_endpoint'
MINIO_ACCESS_KEY = 'your_access_key'
MINIO_SECRET_KEY = 'your_secret_key'

# Source and destination bucket names
SOURCE_BUCKET = 'source_bucket'
DESTINATION_BUCKET = 'destination_bucket'


def create_bucket_if_not_exists(minio_client, bucket_name):
    try:
        minio_client.make_bucket(bucket_name)
        print(f'Bucket created: {bucket_name}')
    except ResponseError as err:
        if 'Your previous request to create the named bucket succeeded' in str(err):
            print(f'Bucket already exists: {bucket_name}')
        else:
            raise


def convert_images(source_bucket, destination_bucket):
    # Connect to MinIO server
    minio_client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    # Create the destination bucket if it doesn't exist
    create_bucket_if_not_exists(minio_client, destination_bucket)

    # Retrieve list of objects in the source bucket
    objects = minio_client.list_objects(source_bucket, recursive=True)

    # Iterate over each object in the source bucket
    for obj in objects:
        # Extract object name
        object_name = obj.object_name

        # Check if the object is an image file (you can customize the file extensions)
        if object_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f'Converting image: {object_name}')

            # Retrieve the image data from MinIO
            image_data = minio_client.get_object(source_bucket, object_name)

            # Open the image with PIL
            image = Image.open(io.BytesIO(image_data.read()))

            # Convert the image to WebP format
            # (you can customize the conversion options)
            image = image.convert('RGB')

            # Define the directory path for the temporary converted file
            temp_dir = os.path.dirname(object_name)
            temp_path = f'temp/{temp_dir}'

            # Create the directory if it doesn't exist
            os.makedirs(temp_path, exist_ok=True)

            # Save the converted image to a temporary file
            temp_file = f'{temp_path}/{os.path.basename(object_name)}.webp'
            image.save(temp_file, 'webp', quality=80)

            # Close the temporary file handle
            image.close()

            # Open the temporary file
            image_buffer = open(temp_file, 'rb')

            # Upload the converted image to the destination bucket
            minio_client.put_object(
                destination_bucket,
                object_name,
                image_buffer,
                os.path.getsize(temp_file),
            )

            # Close the temporary file handle
            image_buffer.close()

            # Delete the temporary file
            os.remove(temp_file)

            print(f'Image converted and uploaded: {object_name}')
        else:
            print(f'Skipping non-image file: {object_name}')


if __name__ == '__main__':
    convert_images(SOURCE_BUCKET, DESTINATION_BUCKET)
