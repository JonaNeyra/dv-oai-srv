import os

import boto3
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
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
        self.bucket_name = bucket_name
        self.content = None

    def load(self, pdf_key):
        tmp_pdf = '/tmp/tmp.pdf'
        with open(tmp_pdf, 'wb') as f_pdf:
            self.s3_client.download_fileobj(self.bucket_name, pdf_key, f_pdf)
        loader = PyPDFLoader(tmp_pdf)
        documents = loader.load()
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.content = splitter.split_documents(documents)
        os.remove(tmp_pdf)

        return self.content


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
