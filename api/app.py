import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI

from api.utils.ssm_handler import decrypt_ssm_patameter
from utils.files import Files, KnowledgeBase, PdfLangchainLoader, CsvLangchainLoader, CsvSimpleQA

load_dotenv()

app = Flask(__name__)
api_key = decrypt_ssm_patameter('/serverless/deployment/credentials/openai-api-key-param')
os.environ['OPENAI_API_KEY'] = api_key
bucket_name = os.getenv('DV_PRODUCT_BUCKET')
pdf_loader = PdfLangchainLoader(bucket_name)
csv_loader = CsvLangchainLoader(bucket_name)
knowledge_base = KnowledgeBase(pdf_loader, csv_loader)


@app.route('/upload_to_bucket', methods=["GET"])
def upload_to_bucket():
    try:
        file_uploader = Files(bucket_name=bucket_name)
        file_uploader.upload()
        return jsonify({'message': 'Files uploaded successfully'})
    except Exception as e:
        return make_response(jsonify(error=str(e)), 500)


@app.route('/process_email', methods=["POST"])
def process_email():
    data = request.json
    email_content = data.get('email_content')

    knowledge_base.vector_store_from_pdf('product-knowledge-base.pdf')
    faq_csv_content = knowledge_base.faq_from_csv('faq-knowledge-base.csv')

    csv_qa_chain = CsvSimpleQA(faq_csv_content)
    faq_response = csv_qa_chain.run(email_content)

    if faq_response != "No se encontró respuesta en nuestras FAQ":
        return jsonify({'response': faq_response})

    results = knowledge_base.query(email_content)
    if results:
        llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        retrieval_qa = RetrievalQA(llm=llm, retriever=knowledge_base.vector_store.as_retriever())
        answer = retrieval_qa.run(email_content)
        return jsonify({'response': answer})

    return jsonify({'response': 'No se encontró una respuesta relevante.'})


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
