from hashlib import md5
from io import BytesIO

from google.cloud import storage


class CloudStorageHelper:
    def __init__(self, client: storage.Client):
        self.client = client

    def estimate_suffix(self, binary_data: bytes):
        def detect_image_mime_type(binary_data):
            if binary_data.startswith(b'\xff\xd8'):
                return 'image/jpeg'
            elif binary_data.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image/png'
            elif binary_data.startswith((b'GIF87a', b'GIF89a')):
                return 'image/gif'
            elif binary_data.startswith(b'BM'):
                return 'image/bmp'
            elif binary_data.startswith(b'RIFF') and binary_data[8:12] == b'WEBP':
                return 'image/webp'
            else:
                return None

        mapping = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
        }

        return mapping.get(detect_image_mime_type(binary_data), '')

    def upload_file(self, bucket_name: str, file_data: bytes) -> storage.Blob:
        # Upload file to GCS and the blob object
        file_suffix = self.estimate_suffix(file_data)
        file_prefix = md5(file_data).hexdigest()
        filename = file_prefix + file_suffix
        blob = self.client.bucket(bucket_name).blob(filename)

        if not blob.exists():
            blob.upload_from_file(BytesIO(file_data))

        return blob

    def create_blob(self, bucket_name: str, filename: str) -> storage.Blob:
        blob = self.client.bucket(bucket_name).blob(filename)
        return blob

    def get_signed_url(self, bucket_id: str, blob_id: str, method: str, expiration: int = 3600) -> str:
        bucket = self.client.bucket(bucket_id)
        # bucket.cors = [
        #     {
        #         "origin": ["*"],
        #         "responseHeader": ["*"],
        #         "method": ["*"],
        #         "maxAgeSeconds": 3600
        #     }
        # ]
        # bucket.patch()
        blob = bucket.blob(blob_id)
        return blob.generate_signed_url(
            expiration=expiration,
            version="v4",
            method=method)
