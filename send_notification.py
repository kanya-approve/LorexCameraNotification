import boto3
import json
import time
from botocore.exceptions import ClientError
from os import environ
from twilio.rest import Client

phone_numbers = environ["SMS_RECIPIENTS"].split(",")
twilio_number = environ["TWILIO_PHONE_NUMBER"]
collection_id = environ["REKOGNITION_COLLECTION_ID"]
email_notification_arn = environ["EMAIL_NOTIFICATION_ARN"]
static_site_url = environ["SITE_URL"]
static_site_image_path = environ["SITE_IMAGE_PATH"]
s3_client = boto3.client("s3")
sns_client = boto3.client("sns")
rekognition_client = boto3.client("rekognition")
twilio_client = Client()

current_time = str(time.time())

sentence_end = "detected by a camera."


def get_image_from_received_motion_alert(bucket, key):
    image = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
    return image


def get_detected_face(received_image):
    detected = "An object"

    try:
        response = rekognition_client.search_faces_by_image(
            CollectionId=collection_id, Image={"Bytes": received_image}
        )

        if len(response["FaceMatches"]) > 0:
            detected = response["FaceMatches"][0]["Face"]["ExternalImageId"]
        else:
            detected = "An unknown person"
    except ClientError as e:
        print(e)

        response = rekognition_client.detect_labels(Image={"Bytes": received_image})

        labels = []

        for label in response["Labels"]:
            if len(label["Instances"]) > 0:
                labels.append(label["Name"].lower())

        if len(labels) > 0:
            labels = ", and a ".join(labels)

            if "person" in labels:
                detected = "A " + labels

    return detected


def send_sms_notification(body, image_url):
    results = []

    for number in phone_numbers:
        message = twilio_client.messages.create(
            to=number.strip(), from_=twilio_number, body=body, media_url=image_url
        )
        results.append(
            {
                "To": message.to,
                "Error Code": message.error_code,
                "Error Message": message.error_message,
            }
        )

    return results


def send_email_notification(body, image_url):
    response = sns_client.publish(
        TopicArn=email_notification_arn,
        Message="<p>"
        + body
        + '</p><br><a href="'
        + image_url
        + '">'
        + image_url
        + "</a>",
        Subject="Motion detected on camera",
    )

    return response


def save_image_to_s3(received_image):
    s3_client.put_object(
        ACL="public-read",
        ContentType="image/jpeg",
        Body=received_image,
        Bucket=static_site_url,
        Key=static_site_image_path + current_time + ".jpg",
    )

    return (
        "https://"
        + static_site_url
        + "/"
        + static_site_image_path
        + current_time
        + ".jpg"
    )


def execute(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    print("Reference bucket: " + bucket + ", key: " + key)

    image = get_image_from_received_motion_alert(bucket, key)
    detected = get_detected_face(image)

    image_url = bucket + "/" + key

    verb = "was"

    if "and a" in detected:
        verb = "were"

    sentence = detected + verb + " " + sentence_end
    print(sentence)

    if detected != "An object":
        return send_sms_notification(sentence, image_url)
    else:
        return send_email_notification(sentence, image_url)
