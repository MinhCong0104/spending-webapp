import boto3

client = boto3.client('sqs')


class QueueService():
    async def send_message(self, message: str, queue_url: str):
        res = client.send_message(
            QueueUrl=queue_url,
            MessageBody=message
        )
        return res


queue_service = QueueService()
