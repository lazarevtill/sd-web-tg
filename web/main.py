from flask import Flask, render_template, request, jsonify
from minio import Minio

app = Flask(__name__)

# Set your MinIO credentials
MINIO_ENDPOINT = 'synology.netbird.cloud:9000'
MINIO_ACCESS_KEY = 'web'
MINIO_SECRET_KEY = '3dMYRxBBGorsj0GBG6V4OX4phQQggcaGmj2EhCFX'
MINIO_BUCKET_NAME = 'webpage'

# Number of images to load per page
page_size = 12

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_images', methods=['POST'])
def load_images():
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Get the page number from the request
    page = int(request.json.get('page', 1))

    # Retrieve a page of objects in the bucket
    objects = minio_client.list_objects(MINIO_BUCKET_NAME, recursive=True)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    objects = list(objects)[start_index:end_index]

    # Extract the URLs of the image objects
    image_urls = []
    for obj in objects:
        if obj.object_name.endswith('.jpg') or obj.object_name.endswith('.png'):
            image_url = minio_client.presigned_get_object(MINIO_BUCKET_NAME, obj.object_name)
            # print("Image URL:", image_url)  # Debugging line
            image_urls.append(image_url)


    # Calculate the next page number
    next_page = page + 1 if len(objects) == page_size else None

    return jsonify({'image_urls': image_urls, 'next_page': next_page})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
