import boto3
from urllib import parse
from rs4 import pathtool
import os
from botocore.exceptions import ClientError

S3 = boto3.resource ('s3')
def upload (source, target, acl = None):
    parts = parse.urlparse (target) # 's3://roadkore/weights/adsa.h5'
    assert parts.scheme == 's3'
    bucket_name = parts.netloc
    bucket = S3.Bucket(name = bucket_name)
    extra_args = {}
    if acl == 'public':
        extra_args ['ACL'] = 'public-read'
    bucket.upload_file (source, parts.path [1:], ExtraArgs = extra_args)

def download (source, target):
    parts = parse.urlparse (source) # 's3://roadkore/weights/adsa.h5'
    assert parts.scheme == 's3'
    bucket_name = parts.netloc
    bucket = S3.Bucket(name = bucket_name)
    pathtool.mkdir (os.path.dirname (target))
    bucket.download_file (parts.path [1:], target)

def remove (target):
    parts = parse.urlparse (target) # 's3://roadkore/weights/adsa.h5'
    assert parts.scheme == 's3'
    bucket_name = parts.netloc
    key = parts.path [1:]
    S3.Object (bucket_name, key).delete ()
delete = remove

def exists (target):
    parts = parse.urlparse (target) # 's3://roadkore/weights/adsa.h5'
    assert parts.scheme == 's3'
    bucket_name = parts.netloc
    key = parts.path [1:]
    try:
        S3.Object(bucket_name, key).load ()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise
    else:
        return True