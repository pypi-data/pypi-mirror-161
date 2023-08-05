from urllib.parse import urlparse
import pyarrow.dataset as ds
import boto3


def get_parquet_file_metadata(s3_uri):
    dataset = ds.dataset(s3_uri)
    n_columns = len(dataset.schema.names)
    total_n_rows = 0
    for batch in dataset.to_batches(columns=[dataset.schema.names[0]], batch_size=500000, use_async=True):
        total_n_rows += batch.num_rows
    return n_columns, total_n_rows


def get_metadata(s3_uri):
    s3_client = boto3.client("s3")
    bucket, key = extract_bucket_and_key(s3_uri)
    metadata = s3_client.head_object(
        Bucket=bucket,
        Key=key
    )
    return metadata


def s3_listdir(s3_uri, max_list_len=1000):
    """
    Copied from technician's adviser
    Replicates os.listdir() functionality for boto3. Returns a list of all objects underneath the
    folder `directory_name` in Bucket `bucket_name`. To be clear, S3 has no folders. We actually
    return all objects in the top-level bucket with the `directory_name` prefix, but the apparent
    functionality is the same to the end-user.

    :param s3_uri: S3 uri to list
    :param max_list_len: Max items to return in initial list

    :return: list of strings giving the names of all objects in the directory `directory_name`
    """
    client = boto3.client("s3")
    bucket_name, directory_name = extract_bucket_and_key(s3_uri)
    is_truncated = True
    continuation_token = None
    keys = []
    while is_truncated:
        if continuation_token is None:
            response = client.list_objects_v2(Bucket=bucket_name, Prefix=directory_name, MaxKeys=max_list_len)
            if response['KeyCount'] == 0:
                return []
        else:
            response = client.list_objects_v2(Bucket=bucket_name,
                                              Prefix=directory_name,
                                              MaxKeys=max_list_len,
                                              ContinuationToken=continuation_token)
        is_truncated = response.get('IsTruncated', False)
        continuation_token = response.get('NextContinuationToken', None)
        keys += [obj.get('Key') for obj in response['Contents']]

    return [f"s3://{bucket_name}/{key}" for key in keys]


def extract_bucket_and_key(s3_uri):
    parsed_url = urlparse(s3_uri)
    bucket_name = parsed_url.netloc
    directory_name = parsed_url.path[1:]
    return bucket_name, directory_name

