import boto3
import json

class SecretService():

    def get_secret(self, secret_id):
        client = boto3.client('secretsmanager')
        res = client.get_secret_value(SecretId=secret_id)
        secret_string = res.get('SecretString')
        try:
            # try to decode it into a dict if it was JSON encoded
            return json.loads(secret_string)
        except json.decoder.JSONDecodeError:
            return secret_string


secret_service = SecretService()
