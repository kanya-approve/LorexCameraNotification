## Lorex Camera Notification

#### Requirements

 1. Python
 2. Run setup.py
 3. Twilio account
 4. Faces indexed into Rekognition by using [this](https://docs.aws.amazon.com/goto/aws-cli/rekognition-2016-06-27/IndexFaces)

#### Lambda Deploy Instructions

 1. Create an environment variable named PHONE_NUMBERS with a comma delimited list of phone numbers to notify of detected objects on camera
 2. Create an environment variable named TWILIO_PHONE_NUMBER with the phone number that will send text messages from Twilio
 3. Create an environment variable named FACES_COLLECTION with the name of the Rekognition collection containing your indexed faces
 4. Create an email on SES
 5. Create an email rule to dump received emails to an S3 bucket
 6. Create an S3 put object event that will trigger the lambda function