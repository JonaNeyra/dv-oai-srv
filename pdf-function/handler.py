import io
import os

import boto3
import fitz
from PIL import Image

bucket = os.getenv('DV_PRODUCT_BUCKET')


class PdfExtractor:
    def __init__(self, bucket_name: str, region_name=None):
        self.s3_client = boto3.client('s3', region_name=region_name or os.getenv('REGION'))
        self.bucket_name = bucket_name

    def run(self, pdf_key):
        tmp_pdf = '/tmp/tmp.pdf'
        with open(tmp_pdf, 'wb') as f_pdf:
            self.s3_client.download_fileobj(self.bucket_name, pdf_key, f_pdf)

        documents = self.extract_text(tmp_pdf)

        os.remove(tmp_pdf)

        return documents

    def extract_text(self, pdf_path):
        documents = []
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text = page.get_text("text")
                print(text)
                if not text:
                    text = self.ocr_image(page)
                documents.append(
                    {
                        'metadata': {'source': pdf_path, 'page': page.number + 1},
                        'page_content': text,
                    },
                )

        return documents

    def ocr_image(self, page):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes()))
        img.save('/tmp/page.png', 'PNG')
        ocr_text = page.get_text("ocr")
        return ocr_text


pdf_extractor = PdfExtractor(bucket)


def lambda_handler(event, context):
    print(event)
    documents = pdf_extractor.run(event["pdf_key"])
    print(context)
    return {
        'response': documents
    }
