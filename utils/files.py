import os
import boto3


class Files:
    DEFAULT_FILE = [
        'product-knowledge-base.pdf',
        'faq-knowledge-base.csv',
    ]
    def __init__(self, bucket_name, region_name=None):
        self.s3_client = boto3.client('s3', region_name=region_name or os.getenv('REGION'))
        self.bucket_name = bucket_name

    def upload(self):
        root_directory = './'
        for filename in os.listdir(root_directory):
            if filename in self.DEFAULT_FILE:
                file_path = os.path.join(root_directory, filename)
                self.s3_client.upload_file(file_path, self.bucket_name, filename)
                print(f'Uploaded {filename} to {self.bucket_name}')
