from flask import Flask, render_template, request
import os
from minio import Minio
import redis
from io import BytesIO

app = Flask(__name__)

# MinIO configuration
MINIO_ENDPOINT = 'synology.netbird.cloud:9000'
MINIO_ACCESS_KEY = 'web'
MINIO_SECRET_KEY = '3dMYRxBBGorsj0GBG6V4OX4phQQggcaGmj2EhCFX'
MINIO_BUCKET_NAME = 'synology-b'

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Pagination settings
page_size = 12

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_image_from_minio(image_path):
    try:
        data = minio_client.get_object(MINIO_BUCKET_NAME, image_path)
        return data.read()  # Read image data as binary, no need to decode it
    except Exception as e:
        print(f"Unexpected error fetching image from MinIO: {str(e)}")
        return None

def get_image_from_minio(image_path):
    try:
        data = minio_client.get_object(MINIO_BUCKET_NAME, image_path)
        return data.read()  # Read image data as binary, no need to decode it
    except Exception as e:
        print(f"Unexpected error fetching image from MinIO: {str(e)}")
        return None


def get_image_from_cache(image_path):
    cached_data = redis_client.get(image_path)
    if cached_data:
        return BytesIO(cached_data)
    return None

def add_image_to_cache(image_path, image_data):
    redis_client.set(image_path, image_data)

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    image_paths = get_image_from_minio()
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_image_paths = image_paths[start_idx:end_idx]
    
    images = []
    for image_path in paginated_image_paths:
        cached_image = get_image_from_cache(image_path)
        if cached_image:
            images.append(cached_image)
        else:
            image_data = get_image_from_minio(image_path)
            if image_data:
                add_image_to_cache(image_path, image_data)
                images.append(BytesIO(image_data))
    
    total_pages = (len(image_paths) + page_size - 1) // page_size
    
    return render_template('index.html', images=images, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
