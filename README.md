# Lorex Camera Motion Detected

## Prerequisites


 1. Motion detection setup on your Lorex DVR
 2. Lorex DVR
 3. Python 3
 4. Same requirements as listed [here](https://serverless.com/framework/docs/providers/aws/guide/quick-start/)
 5. An always on machine in your network...network attached storage options such as [this](https://www.amazon.com/Diskless-Cloud-Network-Attached-Storage/dp/B01AWH05KK/ref=sr_1_1?keywords=wdmycloud&qid=1557723024&s=electronics&sr=1-1-spell) work great with custom firmware installed following [this](https://drive.google.com/drive/folders/0B_6OlQ_H0PxVRXF4aFpYS2dzMEE) tutorial
 6. Picture(s) of those you'd like to index the faces of in Rekognition
    1. The files must be named NAME-PICTURENUMBER.EXTENSION - Ex: brian-4.png or brian-5.jpg
 7. Static website with domain hosted on S3 with path for the motion detected alert images
 8. Twilio account that has sms enabled
 9. A comma delimited list of recipient phone numbers with international code prepended
 10. Get a number on Twilio to send sms from
 11. Get your twilio account sid
 12. Get your twilio auth token

## Instructions

 1. Run the below commands with the appropriate values filled in

    ```console
    npm install
    sls deploy --smsRecipients 'Result of #9 of prerequisites' \
    --twilioNumber 'Result of #10 of prerequisites' \
    --twilioAccountSid 'Result of #11 of prerequisites' \
    --twilioAuthToken 'Result of #12 for prerequisites' \
    --domain 'Domain result of #7 in prerequisites' \
    --domainPath 'Path result of #7 in prerequisites' \
    --facesCollectionId 'This can be any identifier or you can go with the default of OurFaces by removing this' \
    --s3fsUser 'This can be any identifier or you can go with the default of S3FSUser by removing this argument'
    ```

 2. Create and note an access key for the newly created S3FSUser
 3. Note the name of the created MotionBucket
 4. Follow [this](https://github.com/s3fs-fuse/s3fs-fuse/wiki/Fuse-Over-Amazon) tutorial to get s3fs setup on the always machine identified in prerequisite #3
 5. Setup an ftp server with this newly created s3fs mount as the location for uploads
 6. Enable FTP upload to this ftp server from the Lorex DVR settings