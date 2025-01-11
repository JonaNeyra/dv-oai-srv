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
sls plugin install -n serverless-ssm-fetch
```

- Add your API Key generated from OpenAI in the .env file (`for local server`)
```bash
OPENAI_API_KEY={ADD_YOUR_KEY}
```
> How to generate a API Key ➡️ [Medium](https://medium.com/@woyera/your-first-steps-in-ai-using-openais-gpt-4o-mini-with-python-e03e8d47aef7)
> * Remember to have credits and tokens for the selected model
> * This config is for local server

- Add your API Key generated from OpenAI and save this as Parameter in the SSM Parameter Store
> How to create a Parameter ➡️ [Serverless Framework Blog](https://www.serverless.com/blog/aws-secrets-management)
> * The parameter name is (path): `/serverless-framework/deployment/credentials/openai-api-key-param`, [Here the reason](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-hierarchies.html)

- Add your credentials to get and use the Google Sheet file and save this as Parameter in the SSM Parameter Store
> How to create a Parameter ➡️ [Serverless Framework Blog](https://www.serverless.com/blog/aws-secrets-management)
> * Save the Google Credentials
> * serverless-ssm-fetch retrieve the value in the ENV vars [See more](https://medium.com/@daxaymakwana/simplifying-aws-ssm-parameter-retrieval-with-the-serverless-ssm-fetch-plugin-778a494f6307)
> * The parameter name is (path): `/serverless-framework/deployment/credentials/google-credentials-param`, [Here the reason](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-hierarchies.html)