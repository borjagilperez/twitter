# -*- coding: utf-8 -*-

import io

import boto3

class Client:

    def __init__(self, region_name=None, endpoint_url=None, aws_access_key_id=None, aws_secret_access_key=None, config=None):

        self.__session = boto3.session.Session()
        self.__client = self.__session.client('s3',
            region_name=region_name, endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
            config=config)

    def download_file(self, bucket_name, object_key, out_file):
        
        self.__client.Bucket(bucket_name).download_file(object_key, out_file)

    def upload_file(self, source_file, bucket_name, object_key):

        self.__client.upload_file(source_file, bucket_name, object_key)

    def read_object(self, bucket_name, object_key):

        obj = self.__client.get_object(Bucket=bucket_name, Key=object_key)
        return obj['Body'].read().decode('utf-8')

    def put_object(self, source, bucket_name, object_key):

        self.__client.put_object(Body=source, Bucket=bucket_name, Key=object_key)

    def put_df2csv(self, df, bucket_name, object_key):

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, encoding='utf-8')
        source = csv_buffer.getvalue()
        self.put_object(source, bucket_name, object_key)
