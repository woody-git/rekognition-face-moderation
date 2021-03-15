# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0 (https://spdx.org/licenses/MIT-0.html)

import json
import os
import subprocess
import shlex
import boto3

S3_DESTINATION_BUCKET = "eyes-moderation-demo"
SIGNED_URL_TIMEOUT = 60

def lambda_handler(event, context):

    s3_client = boto3.client('s3')
    reko = boto3.client('rekognition')
    
    # Read bucket and key of the image that triggered the Lamdba function
    s3_source_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_source_key = event['Records'][0]['s3']['object']['key']
    
    # Extract the file name of the image to analyze
    s3_source_basename = os.path.splitext(os.path.basename(s3_source_key))[0]
    
    file_ext = '.jpg'
    # This function will generate a filename with same name and moderated.jpg as suffix
    s3_destination_filename = s3_source_basename + "_moderated_left"
    
    # The elaborated file will be placed in the same bucket and at this key
    s3_destination_key = "output/" + s3_destination_filename
    
    # Names for location where the image is temparary saved and the location for the new  
    local_input_filename = "/tmp/" + s3_source_basename
    local_output_filename = "/tmp/" + s3_destination_filename
    local_output_final_finalname = "/tmp/" + s3_destination_filename + "_moderated_final" 
    
    #download image on lambda tmp area
    s3_client.download_file(s3_source_bucket, s3_source_key, local_input_filename)

    #Calling Rekognition for face analyis on the uploaded image
    response = reko.detect_faces(Image={'S3Object':{'Bucket':s3_source_bucket,'Name':s3_source_key}},Attributes=['ALL'])

    for faceDetail in response['FaceDetails']:
        for eyesDetails in faceDetail['Landmarks']:
            # Left Eye
            if str(eyesDetails['Type']) == 'leftEyeLeft': le_width = str(eyesDetails['X'])
            if str(eyesDetails['Type']) == 'leftEyeRight': le_high = str(eyesDetails['X'])
            if str(eyesDetails['Type']) == 'leftEyeUp': le_left = str(eyesDetails['Y'])
            if str(eyesDetails['Type']) == 'leftEyeDown': le_top = str(eyesDetails['Y'])
            # Right Eye
            if str(eyesDetails['Type']) == 'rightEyeLeft': re_width = str(eyesDetails['X'])
            if str(eyesDetails['Type']) == 'rightEyeRight': re_high = str(eyesDetails['X'])
            if str(eyesDetails['Type']) == 'rightEyeUp': re_left = str(eyesDetails['Y'])
            if str(eyesDetails['Type']) == 'rightEyeDown': re_top = str(eyesDetails['Y'])
            
        l_width = float(le_high) - float(le_width)
        l_high = float(le_top) - float(le_left) + 0.01
        l_left = le_width
        l_top = le_left 
        
        design_bbox(local_input_filename, l_width, l_high, l_left, l_top)
        
        r_width = float(re_high) - float(re_width)
        r_high = float(re_top) - float(re_left) + 0.01
        r_left = re_width
        r_top = re_left   
        
        design_bbox(local_input_filename + file_ext, r_width, r_high, r_left, r_top)
        
    try:
        
        resp = s3_client.upload_file(local_input_filename + file_ext + file_ext, s3_source_bucket, s3_destination_key + file_ext)        

    except:
        print("An exception occurred in running ffmpeg command")

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete successfully')
    }
    
    
    
def design_bbox(image_file, bb_width, bb_high, bb_left, bb_top) :
    try:
        ffmpeg_cmd1 = "/opt/bin/ffmpeg -y -i \"" + image_file + "\" -vf drawbox=x=iw*" + str(bb_left) + ":y=ih*" + str(bb_top) + ":w=iw*" + str(bb_width) + ":h=ih*" + str(bb_high) + ":color=green@0.5:t=fill " + image_file + '.jpg'
        print("FFMPEG Command 1: " + ffmpeg_cmd1)
        os.system(ffmpeg_cmd1)
    except:
        print("An exception occurred in running design bbox function.")
    finally:
        return 0
