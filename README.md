## Dependencies

- Virtual Environment Python 3.10 (.venv)
- AWS CLI
- Serverless Framework

## Steps

- Install Flask project dependencies
 ```bash
 pip install -r requirements.txt
 ```

- Install Serverless Framework plugins
```bash
sls plugin install -n serverless-wsgi
sls plugin install -n serverless-python-requirements
```

- Add your API Key generated from OpenAI in the .env file
```bash
OPENAI_API_KEY={ADD_YOUR_KEY}
```
> How to generate a API Key ➡️ [Medium](https://medium.com/@woyera/your-first-steps-in-ai-using-openais-gpt-4o-mini-with-python-e03e8d47aef7)
> * Remember to have credits and tokens for the selected model