from flask import Flask, render_template, jsonify, request
import minio
import redis
import base64
import logging

app = Flask(__name__)

# MinIO Configuration
MINIO_ENDPOINT = 'synology.netbird.cloud:9000'
MINIO_ACCESS_KEY = 'web'
MINIO_SECRET_KEY = '3dMYRxBBGorsj0GBG6V4OX4phQQggcaGmj2EhCFX'
MINIO_BUCKET_NAME = 'webpage'

# Redis Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Initialize MinIO client
minio_client = minio.Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Number of images per page
page_size = 10

# Configure logging
logging.basicConfig(level=logging.ERROR)

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    offset = (page - 1) * page_size
    images = get_images_from_minio(offset, page_size)
    return render_template('index.html', images=images, page=page)

@app.route('/images')
def get_images():
    page = int(request.args.get('page', 1))
    offset = (page - 1) * page_size
    images = get_images_from_minio(offset, page_size)
    return jsonify(images)

def get_images_from_minio(offset, limit):
    images = []
    for i in range(offset, offset + limit):
        image_path = f'image_{i}.jpg'
        try:
            image_data = redis_client.get(image_path)
            if image_data is not None:
                images.append(base64.b64encode(image_data).decode('utf-8'))
            else:
                image_data = minio_client.get_object(MINIO_BUCKET_NAME, image_path).read()
                redis_client.set(image_path, image_data)
                images.append(base64.b64encode(image_data).decode('utf-8'))
        except Exception as e:
            error_message = f"Error fetching image {image_path}: {str(e)}"
            logging.error(error_message)
            images.append(error_message)
    return images

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
