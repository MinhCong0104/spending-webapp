import boto3

s3 = boto3.resource('s3')

# # Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)

bucket = s3.Bucket('superstorm-vda-app-consulting-dev')

li = bucket.get_available_subresources()
print(li)
    