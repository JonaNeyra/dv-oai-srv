import boto3


def decrypt_ssm_patameter(parameter_name):
    ssm_client = boto3.client('ssm')

    response = ssm_client.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )

    return response['Parameter']['Value']
