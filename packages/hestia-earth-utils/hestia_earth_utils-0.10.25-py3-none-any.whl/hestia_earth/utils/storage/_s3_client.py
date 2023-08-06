import os

BUCKET = os.getenv('AWS_BUCKET')
BUCKET_GLOSSARY = os.getenv('AWS_BUCKET_GLOSSARY')
_s3_client = None


# improves speed for connecting on subsequent calls
def _get_s3_client():
    global _s3_client
    import boto3
    _s3_client = boto3.session.Session().client('s3') if _s3_client is None else _s3_client
    return _s3_client


def _get_bucket(glossary: bool = False) -> str:
    return BUCKET_GLOSSARY if glossary else BUCKET


def _load_from_bucket(bucket: str, key: str):
    from botocore.exceptions import ClientError
    try:
        return _get_s3_client().get_object(Bucket=bucket, Key=key)['Body'].read()
    except ClientError:
        return None


def _exists_in_bucket(bucket: str, key: str):
    from botocore.exceptions import ClientError
    try:
        _get_s3_client().head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False
