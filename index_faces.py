import boto3
from os import environ

s3_client = boto3.client("s3")
s3_paginator = s3_client.get_paginator("list_objects_v2")
rekognition_client = boto3.client("rekognition")
collection_id = environ["REKOGNITION_COLLECTION_ID"]
faces_to_index_bucket = environ["FACES_TO_INDEX_BUCKET"]


def index_face(bucket, key, name):
    response = rekognition_client.index_faces(
        CollectionId=collection_id,
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        ExternalImageId=name,
        MaxFaces=1,
    )

    return response


def execute(event, context):
    response_iterator = s3_paginator.paginate(Bucket=faces_to_index_bucket)

    try:
        rekognition_client.create_collection(CollectionId=collection_id)
    except:
        pass

    for response in response_iterator:
        for item in response.pop("Contents", []):
            key = item["Key"]
            name = key[key.rfind("/") + 1 :]
            name = name.split("-")
            name = name[0]
            print(index_face(faces_to_index_bucket, key, name))

    return "Finished indexing faces"
