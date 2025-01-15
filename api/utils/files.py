import json
import os

import boto3
from botocore.exceptions import ClientError
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


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


class PdfLangchainLoader:
    def __init__(self, bucket_name, region_name=None):
        self.s3_client = boto3.client('s3', region_name=region_name or os.getenv('REGION'))
        self.lambda_client = boto3.client('lambda', region_name=region_name or os.getenv('REGION'))
        self.bucket_name = bucket_name
        self.content = None

    def load(self, pdf_key):
        documents = []
        event = {"pdf_key": pdf_key}
        try:
            response = self.lambda_client.invoke(
                FunctionName="dv-oai-srv-dev-pdf-function",
                InvocationType='RequestResponse',
                Payload=json.dumps(event),
            )

            payload = response['Payload'].read().decode("utf-8")
            documents = self.process_lambda_response(payload)
        except ClientError as e_res:
            print(f"Error al invocar la Lambda: {e_res}")

        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.content = splitter.split_documents(
            [
                Document(
                    page_content=doc['page_content'],
                    metadata=doc['metadata']
                ) for doc in documents
            ]
        )
        print(self.content)

        return self.content

    def process_lambda_response(self, payload):
        try:
            response_data = eval(payload)
            return response_data.get("response", [])
        except Exception as e_res:
            print(f"Error al procesar la respuesta de Lambda: {e_res}")
            return []


class CsvLangchainLoader:
    def __init__(self, bucket_name, region_name=None):
        self.s3_client = boto3.client('s3', region_name=region_name or os.getenv('REGION'))
        self.bucket_name = bucket_name
        self.content = None

    def load(self, csv_key):
        tmp_csv = '/tmp/tmp.csv'
        with open(tmp_csv, 'wb') as f_csv:
            self.s3_client.download_fileobj(self.bucket_name, csv_key, f_csv)
        with open(tmp_csv, 'r', encoding='utf-8') as f_csv:
            csv_content = f_csv.readlines()
        self.content = [line.strip().split(',') for line in csv_content][1:]
        os.remove(tmp_csv)

        return self.content


class CsvSimpleQA:
    def __init__(self, csv_content):
        self.csv_content = {row[0]: row[1] for row in csv_content}

    def run(self, question):
        return self.csv_content.get(question, "No se encontró respuesta en nuestras FAQ")


class KnowledgeBase:
    def __init__(self, pdf_langchain_loader, csv_langchain_loader):
        self.pdf_langchain_loader = pdf_langchain_loader
        self.csv_langchain_loader = csv_langchain_loader
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    def vector_store_from_pdf(self, pdf_key):
        documents = self.pdf_langchain_loader.load(pdf_key)
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    def faq_from_csv(self, csv_key):
        return self.csv_langchain_loader.load(csv_key)

    def query(self, question):
        if not self.vector_store:
            return "La base de conocimiento aun no es construida"
        results = self.vector_store.similarity_search(question, k=3)
        return results
