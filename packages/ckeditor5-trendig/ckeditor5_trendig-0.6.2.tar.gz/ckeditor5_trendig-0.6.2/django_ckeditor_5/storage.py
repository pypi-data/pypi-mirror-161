from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticEditStorage(S3Boto3Storage):
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    location = getattr(settings, 'AWS_PUBLIC_MEDIA_LOCATION', None)
    default_acl = "public-read"