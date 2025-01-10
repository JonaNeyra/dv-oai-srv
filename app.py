import os

import openai
from flask import Flask, request, jsonify, make_response
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


@app.route('/process_email', methods=["POST"])
def process_email():
    data = request.json
    email_content = data.get('email_content')

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un potente asistente que propone correos como borrador."},
            {"role": "user", "content": f"Responde a la siguiente consulta: {email_content}"}
        ],
    )

    generated_text = response.choices[0].text.strip()
    return jsonify({'response': generated_text})


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
