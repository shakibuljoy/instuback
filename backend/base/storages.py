from storages.backends.s3boto3 import S3Boto3Storage
import boto3

from django.conf import settings

class S3StaticStorage(S3Boto3Storage):
    """Storage for static files in S3."""
    bucket_name = "instustatic"
    location = "instuzilla-static-files"

class S3MediaStorage(S3Boto3Storage):
    """Storage for media files in S3."""
    bucket_name = "instustatic"
    location = "instumedia"



def generate_presigned_url(file_key, expiration=600):
    """
    Generate a pre-signed URL for a private S3 object.
    
    :param expiration: Time in seconds before URL expires (default: 600s or 10 minutes)
    :return: Pre-signed URL string
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": S3MediaStorage.location+'/'+file_key},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
