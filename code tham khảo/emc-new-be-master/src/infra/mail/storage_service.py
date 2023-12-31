from pydantic import BaseModel
import boto3
import urllib.parse

class FileLocation(BaseModel):
    bucket: str
    key: str


client = boto3.client('s3')


class StorageService():
    async def get_file_url(self, location: FileLocation):
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': location.get('bucket'),
                'Key': location.get('key')
            },
            ExpiresIn=3600
        )
        return url

    async def list_files(self, bucket: str, prefix: str):
        res = client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
        )
        return res

    async def copy_file(self, source_bucket: str, source_object_key: str,
                        destination_bucket: str, destination_key: str):
        res = client.copy_object(
            Bucket=destination_bucket,
            CopySource=urllib.parse.quote(f'{source_bucket}/{source_object_key}'),
            Key=destination_key,
            ACL='bucket-owner-full-control'
        )
        return res

    async def put_file(self, file: str, location: FileLocation):
        res = client.put_object(
            Bucket=location.get('bucket'),
            Key=location.get('key'),
            Body=file
        )
        return res


storage_service = StorageService()
