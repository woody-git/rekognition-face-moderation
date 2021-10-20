# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0 (https://spdx.org/licenses/MIT-0.html)

import json
import os
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
    filepath_name_index =os.path.splitext(os.path.basename(s3_source_key)) 
    s3_source_basename = filepath_name_index[0]
    file_ext = filepath_name_index[1]
    # Create output S3 file key
    s3_destination_key = "output/" + s3_source_basename + "_gdpr_compliant" + file_ext
    
    # Names for location where the image is temparary saved and the location for the new
    local_input_filename = "/tmp/" + s3_source_basename + '10' + file_ext
    last_processed_filename = local_input_filename

    #download image on lambda tmp area
    s3_client.download_file(s3_source_bucket, s3_source_key, local_input_filename)

    # FACES BLUR
    #Calling Rekognition for face analyis on the uploaded image
    faceResponse = reko.detect_faces(Image={'S3Object':{'Bucket':s3_source_bucket,'Name':s3_source_key}},Attributes=['ALL'])
    
    for faceDetail in faceResponse['FaceDetails']:       
        l_width = str(round(faceDetail['BoundingBox']['Width'], 2))
        l_height = str(round(faceDetail['BoundingBox']['Height'], 2))
        l_left = str(round(faceDetail['BoundingBox']['Left'], 2))
        l_top = str(round(faceDetail['BoundingBox']['Top'], 2))    
        last_processed_filename = design_bbox(last_processed_filename, l_width, l_height, l_left, l_top)

    
    # ID CARDS AND CAR PLATES BLUR
    labelsResponse = reko.detect_labels(Image={'S3Object':{'Bucket':s3_source_bucket,'Name':s3_source_key}})
    for label in labelsResponse['Labels']:
        if label['Name'] in ['Id Cards','Document','Driving License','Car','Business Card','Credit Card',
                    'Laptop','License Plate','Mobile Phone','Passport']: #,'Person','Road Sign','Tablet Computer']:
            for inst in label['Instances']:
                l_width = str(round(inst['BoundingBox']['Width'], 2))
                l_height = str(round(inst['BoundingBox']['Height'], 2))
                l_left = str(round(inst['BoundingBox']['Left'], 2))
                l_top = str(round(inst['BoundingBox']['Top'], 2))   
                last_processed_filename = design_bbox(last_processed_filename, l_width, l_height, l_left, l_top)

    try:
        s3_client.upload_file(last_processed_filename, s3_source_bucket, s3_destination_key)        
    except:
        print("An exception occurred on final elaborated file upload on S3.")
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete successfully')
    }
    
    
    
def design_bbox(input_image_file_name, bb_width, bb_height, bb_left, bb_top) :
    
    input_file_basename = input_image_file_name[:-4]
    input_file_ext = input_image_file_name[-4:]

    output_filename = ''
    num_iteration = input_file_basename[-2:]
    iter_number = int(num_iteration) + 1
    num_iteration = str(iter_number)

    output_filename = input_file_basename[:-2] + num_iteration + input_file_ext

    try:
        ffmpeg_cmd1 = "/opt/bin/ffmpeg -y -i \"" + input_image_file_name + "\" -vf drawbox=x=iw*" + str(bb_left) + ":y=ih*" + str(bb_top) + ":w=iw*" + str(bb_width) + ":h=ih*" + str(bb_height) + ":color=black:t=fill " + output_filename
        os.system(ffmpeg_cmd1)
    except:
        print("An exception occurred in running ffmpeg command.")
    finally:
        return output_filename
