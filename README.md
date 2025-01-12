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

- The files to be used will be uploaded to the bucket but not to the repository
> Leave them in the root of the project and rename them to consume them
> - PDF: product-knowledge-base.pdf
> - Sheet: faq-knowledge-base.csv

- Add your API Key generated from OpenAI and the bucket in the .env file (`for local server`)
```bash
OPENAI_API_KEY={ADD_YOUR_KEY}
DV_PRODUCT_BUCKET=dv-product-bucket
```
> How to generate a API Key ➡️ [Medium](https://medium.com/@woyera/your-first-steps-in-ai-using-openais-gpt-4o-mini-with-python-e03e8d47aef7)
> * Remember to have credits and tokens for the selected model
> * This config is for local server

- Add your API Key generated from OpenAI and save this as Parameter in the SSM Parameter Store
> How to create a Parameter ➡️ [Serverless Framework Blog](https://www.serverless.com/blog/aws-secrets-management)
> * The parameter name is (path): `/serverless/deployment/credentials/openai-api-key-param`, [Here the reason](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-hierarchies.html)

- `Alternative` - Add your credentials to get and use the Google Sheet file and save this as Parameter in the SSM Parameter Store
> How to create a Parameter ➡️ [Serverless Framework Blog](https://www.serverless.com/blog/aws-secrets-management)
> * Use this alternative if you have the file in Drive and want to consume it from Google Sheets
> * Save the Google Credentials created en Google Cloud Console
> * Add to serverless.yml: `GOOGLE_CREDENTIALS: ${ssm:/serverless/deployment/credentials/google-credentials-param}`
> * serverless-ssm-fetch retrieve the value in the ENV vars [See more](https://medium.com/@daxaymakwana/simplifying-aws-ssm-parameter-retrieval-with-the-serverless-ssm-fetch-plugin-778a494f6307)
> * The parameter name is (path): `/serverless/deployment/credentials/google-credentials-param`, [Here the reason](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-hierarchies.html)

It's required to have the stack created in the cloud to be able to upload the knowledge base, to do this you must execute this command first
```bash
serverless deploy
```
> Once the stack is built in the cloud, we can upload the files to S3 from the local server
> * Serve the project locally with: ```$ serverless wsgi serve```
> * Calls the GET endpoint: /upload_to_bucket
> * Wait for files to be uploaded to s3