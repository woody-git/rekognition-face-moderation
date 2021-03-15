# Face Moderation with Amazon Rekognition

This repo contains an exmaple on how to work on moderation, adding bbox to face elements detected by Amazon Rekognition Face Analysis.

The repo contains a python lambda function that leverages on FFMPEG statis distribution.

In order to create a FFMPEG Lambda Layer and use the code in this repo, you can follow these steps:
https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/

NOTE:

- This function is covering the eyes with two green bbox with 50% transaprency
- You need to add rekognition privileges in the lambda role in order to let the lambda function calls Rekognitoin Face Analysis
- Change the bucket name in the python code with your bucket
- This sample only support jpg at the moment
- This function places the output jpg (with bbox on eyes) at -> "yourbucket"/output so an S3 output folder is expected in defined bucket
