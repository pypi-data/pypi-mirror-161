import functools
from typing import Dict

import boto3
from moto import mock_s3

from curia.utils.s3 import extract_bucket_and_key


def _create_seed_s3_data(seed_s3_data: Dict[str, dict]):
    if not isinstance(seed_s3_data, dict):
        raise TypeError("seed_s3_data should be a dict!")
    s3_client = boto3.client("s3")
    created_buckets = set()
    for s3_uri, object_data in seed_s3_data.items():
        bucket, key = extract_bucket_and_key(s3_uri)
        if bucket not in created_buckets:
            s3_client.create_bucket(
                Bucket=bucket
            )
            created_buckets.add(bucket)

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            **object_data
        )


def curia_mock_s3(seed_s3_data: Dict[str, dict]):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            _create_seed_s3_data(seed_s3_data)
            return fn(*args, **kwargs)
        wrapper = mock_s3(wrapper)
        return wrapper
    return decorator