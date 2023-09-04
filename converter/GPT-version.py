import io
import os
from minio import Minio
from minio.error import S3Error
from PIL import Image

# MinIO configuration
MINIO_ENDPOINT = 'synology.netbird.cloud:9000'
MINIO_ACCESS_KEY = 'converter'
MINIO_SECRET_KEY = '5dOgcCgxWhmYdfVlHQKLIsBna8FKhvNCOkXJ8Wam'

# Source and destination bucket names
SOURCE_BUCKET = 'sd-new'
DESTINATION_BUCKET = 'synology-b'


def create_bucket_if_not_exists(minio_client, bucket_name):
    try:
        minio_client.make_bucket(bucket_name)
        print(f'Bucket created: {bucket_name}')
    except S3Error as err:
        if err.code == 'BucketAlreadyOwnedByYou':
            print(f'Bucket already exists: {bucket_name}')
        else:
            raise


def resize_and_compress_image(image, max_dimension=1024, quality=80):
    # Resize the image while maintaining aspect ratio
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        image.thumbnail((max_dimension, max_dimension))

    # Convert the image to RGB mode (if not already)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Save the image to a temporary in-memory buffer
    output_buffer = io.BytesIO()
    image.save(output_buffer, 'JPEG', quality=quality)

    return output_buffer


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

            try:
                # Retrieve the image data from MinIO
                image_data = minio_client.get_object(source_bucket, object_name)
                
                # Check the length of the image data
                image_size = len(image_data.read())

                # Check if the image data is empty
                if image_size == 0:
                    print(f'Error: Empty image data for {object_name}')
                    continue

                # Attempt to open the image with PIL
                try:
                    image = Image.open(io.BytesIO(image_data.read()))
                except Exception as pil_error:
                    print(f'Error opening image {object_name} with PIL: {str(pil_error)}')
                    continue  # Skip to the next image if PIL cannot open it

                # Resize and compress the image
                image_buffer = resize_and_compress_image(image)

                # Upload the resized and compressed image to the destination bucket
                minio_client.put_object(
                    destination_bucket,
                    object_name,
                    image_buffer,
                    len(image_buffer.getvalue()),
                )

                print(f'Image converted and uploaded: {object_name}')
            except Exception as e:
                print(f'Error processing image {object_name}: {str(e)}')
                continue  # Skip to the next image if an error occurs
        else:
            print(f'Skipping non-image file: {object_name}')


if __name__ == '__main__':
    convert_images(SOURCE_BUCKET, DESTINATION_BUCKET)
