import os
import re
from typing import Union

import boto3
import nure.path
import nure.sync.cache
import botocore.exceptions


class S3Uri:
    def __init__(self, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key

    PARSE_RE = re.compile(R"^s3://(?P<bucket>[0-9a-z.-]+)\/(?P<key>([0-9A-Za-z!\-_.*'\()]+/?)+)(?<!/)$")

    @staticmethod
    def parse(uri: str):
        # Bucket name
        # https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html
        # Object name
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
        # this implementation just covers sub-set of S3 URI
        match = S3Uri.PARSE_RE.match(uri)
        if match is None:
            raise ValueError('input string is not S3 URI')

        group_dict = match.groupdict()
        return S3Uri(group_dict['bucket'], group_dict['key'])

    @property
    def uri(self):
        return f's3://{self.bucket}/{self.key}'

    def __str__(self) -> str:
        return self.uri

    def __repr__(self) -> str:
        return f'S3Uri({self.bucket}, {self.key})'


class S3(nure.sync.cache.LocalFileCache):
    def __init__(self, root_path='data/s3', ttl=None) -> None:
        super(S3, self).__init__(root_path, ttl)

    @staticmethod
    def _to_s3uri_(s3_uri: Union[str, S3Uri]):
        # unify s3_uri type
        if isinstance(s3_uri, str):
            s3_uri = S3Uri.parse(s3_uri)

        return s3_uri

    def key_to_local_relative_path(self, s3_uri: Union[str, S3Uri], *args, **kargs) -> str:
        s3_uri = S3._to_s3uri_(s3_uri)
        return os.path.join(s3_uri.bucket, s3_uri.key)

    def retrieve(self, s3_uri: Union[str, S3Uri], local_file_path):
        s3_uri = S3._to_s3uri_(s3_uri)

        s3 = boto3.resource('s3')
        s3.meta.client.download_file(s3_uri.bucket, s3_uri.key, local_file_path)

    def _infer_s3uri_(self, local_file_path):
        relative_path = os.path.relpath(local_file_path, self.root_path)
        components = nure.path.splitall(relative_path)
        bucket = components[0]
        key = '/'.join(components[1:])

        return S3Uri(bucket, key)

    def upload(self, local_file_path, s3_uri=None):
        if s3_uri is None:
            s3_uri = self._infer_s3uri_(local_file_path)
        else:
            s3_uri = S3._to_s3uri_(s3_uri)

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(local_file_path, s3_uri.bucket, s3_uri.key)

        return s3_uri

    def metadata(self, s3_uri: Union[str, S3Uri]):
        if isinstance(s3_uri, str):
            s3_uri = S3Uri.parse(s3_uri)

        s3 = boto3.resource('s3')
        try:
            meta = s3.meta.client.head_object(Bucket=s3_uri.bucket, Key=s3_uri.key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None

            raise e

        return meta

    def exist(self, s3_uri: Union[str, S3Uri]):
        return self.metadata(s3_uri) is not None
