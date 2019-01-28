import binascii
import boto3
import json
import mailparser
import os
import time
from botocore.exceptions import ClientError
from twilio.rest import Client

phone_numbers = os.environ['PHONE_NUMBERS'].split(',')
twilio_number = os.environ['TWILIO_PHONE_NUMBER']
collection_id = os.environ['FACES_COLLECTION']
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
twilio_client = Client()

current_time = str(time.time())

def get_image_from_received_motion_alert(bucket, key):
	mail_object_from_s3 = s3_client.get_object(Bucket = bucket, Key = key)['Body'].read()
	mail = mailparser.parse_from_bytes(mail_object_from_s3)

	if len(mail.attachments) != 1:
		raise Exception('Received a test alert')

	attachment = mail.attachments.pop(0)
	attachment = attachment.pop('payload')
	attachment = binascii.a2b_base64(attachment)
	return attachment

def get_detected_face(received_image):
	detected = 'An object'
	
	try:
		response = rekognition_client.search_faces_by_image(CollectionId = collection_id, Image = {
			'Bytes': received_image
		})
		
		if len(response['FaceMatches']) > 0:
			detected = response['FaceMatches'][0]['Face']['ExternalImageId']
		else:
			detected = 'An unknown person'
	except ClientError as e:
		print(e)

		response = rekognition_client.detect_labels(Image = {
			'Bytes': received_image
		})
		
		labels = []
		
		for label in response['Labels']:
			if len(label['Instances']) > 0:
				labels.append(label['Name'].lower())
		
		if len(labels) > 0:
			labels = ', and a '.join(labels)

			if 'person' in labels:
				detected = 'A ' + labels
		
	return detected


def send_sms_notification(body, image_url):
	results = []
	
	for number in phone_numbers:
		message = twilio_client.messages.create(to = number.strip(), from_ = twilio_number, body = body, media_url = image_url)
		results.append({
			'To': message.to,
			'Error Code': message.error_code,
			'Error Message': message.error_message
		})

	return results

def save_image_to_s3(received_image):
	s3_client.put_object(ACL = 'public-read', ContentType = 'image/jpeg', Body = received_image, Bucket = 'bkanya.com', Key = 'Sites/Images/' + current_time + '.jpg')

	return 'https://bkanya.com/Sites/Images/' + current_time + '.jpg'

def lambda_handler(event, context):
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']
	print('Reference bucket: ' + bucket + ', key: ' + key)

	received_image = get_image_from_received_motion_alert(bucket, key)
	detected = get_detected_face(received_image)
	print(detected + ' was detected by the front door camera.')

	if detected != 'An object':
		image_url = save_image_to_s3(received_image)
		print('Upload detected image to ' + image_url)
		verb = 'was'

		if 'and a' in detected:
			verb = 'were'

		return send_sms_notification(detected + ' ' + verb + ' detected by the front door camera.', image_url)
	else:
		return 'Did not detect a person'
