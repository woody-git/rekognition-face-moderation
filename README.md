# Image Moderation with Amazon Rekognition

This repo contains some exmaples on how to work on image moderation with Amazon Rekognition by adding bbox to face elements detected by the AWS API.

The repo contains AWS Lambda functions that leverages on FFMPEG static distribution.

In order to create a FFMPEG Lambda Layer and use the code in this repo, you can follow steps in this blogpost:
https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/

# Image moderation for GDPR compliancy (gdpr_compliance_function.py)
This function mask all reference of a list of sensible object that Amazon Rekognition can detect 
['Id Cards','Document','Driving License','Car','Business Card','Credit Card', 'Laptop','License Plate','Mobile Phone','Passport']
It also search for faces with Amazon Rekognition Face Analysis.
All references of objects and Faces are covered by a black bbox
- It supports .jpg and .png
- You need to add Amazon Rekognition privileges in the AWS Lambda role, in order to let the Lambda function calls Amazon Rekognitoin APIs
- Change "S3_DESTINATION_BUCKET" bucket with your destination bucket
- This function places the output image in "yourbucket"/output folder. An S3 output folder is expected in destination bucket

# Eyes moderation function (lambda_function.py)
- This function is covering the eyes with two green bbox with 50% transaprency
- Only support jpg images
- You need to add rekognition privileges in the lambda role in order to let the lambda function calls Rekognitoin Face Analysis
- Change "S3_DESTINATION_BUCKET" bucket with your destination bucket
- This function places the output image in "yourbucket"/output folder. An S3 output folder is expected in destination bucket

![pexels-maria-orlova-4946649](https://user-images.githubusercontent.com/2033376/111336382-7a889880-8675-11eb-8a71-3172fa81e1cf.jpg)
![pexels-maria-orlova-4946649_moderated_left](https://user-images.githubusercontent.com/2033376/111336468-8f652c00-8675-11eb-9b18-9d6db66a3156.jpg)
