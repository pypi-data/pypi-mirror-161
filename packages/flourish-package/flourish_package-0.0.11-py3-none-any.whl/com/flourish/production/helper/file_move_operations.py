from datetime import datetime
import boto3
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDirectory)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helper import environment

s3 = boto3.resource('s3')

def move_sample_raw_file_from_sample_raw_folder_to_sample_received_folder(source, fileName):
    fileToMove = {
        'Bucket': environment.platform_s3_bucket_name,
        'Key': environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/'+source+'/'+fileName
    }
    s3.meta.client.move(fileToMove, environment.platform_s3_bucket_name, environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/'+source+'/received/'+datetime.now().strftime("%Y-%m-%d"))

def move_raw_file_from_raw_folder_to_received_folder(source, fileName):
    fileToMove = {
        'Bucket': environment.platform_s3_bucket_name,
        'Key': environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/'+source+'/'+fileName
    }
    s3.meta.client.move(fileToMove, environment.platform_s3_bucket_name, environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/'+source+'/received/'+datetime.now().strftime("%Y-%m-%d"))

def move_file_between_s3_locations(sourceBucket, folderInsideSourceBucket, nameOfFileToMove, destinationBucket, folderInsideDestinationBucket):
    fileToMove = {
        'Bucket': sourceBucket,
        'Key': folderInsideSourceBucket+'/'+nameOfFileToMove
    }
    s3.meta.client.move(fileToMove, destinationBucket, folderInsideDestinationBucket)

def move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(fileLocationInBucket, fileName, destinationLocationInBucket, destinationFileName):
    fileLocationInBucketWithoutBucketName = fileLocationInBucket.replace('s3://'+environment.platform_s3_bucket_name+'/', '')
    destinationLocationInBucketWithoutBucketName = destinationLocationInBucket.replace('s3://'+environment.platform_s3_bucket_name+'/', '')
    fileToMove = {
        'Bucket': environment.platform_s3_bucket_name,
        'Key': fileLocationInBucketWithoutBucketName+'/'+fileName
    }
    s3.Object(environment.platform_s3_bucket_name, destinationLocationInBucketWithoutBucketName+'/'+destinationFileName).copy_from(
        CopySource=fileToMove
    )
    s3.Object(environment.platform_s3_bucket_name, fileLocationInBucketWithoutBucketName+'/'+fileName).delete()

def move_file_from_one_location_to_another_in_s3_bucket(fileLocationInBucketWithFileName, destinationLocationInBucket):
    fileToMove = {
        'Bucket': environment.platform_s3_bucket_name,
        'Key': fileLocationInBucketWithFileName
    }
    s3.Object(
        environment.platform_s3_bucket_name, 
        destinationLocationInBucket+fileLocationInBucketWithFileName[fileLocationInBucketWithFileName.rfind('/')+1:]
    ).copy_from(
        CopySource=fileToMove
    )
    s3.Object(
        environment.platform_s3_bucket_name, 
        fileLocationInBucketWithFileName
    ).delete()

def move_files_from_one_location_to_another_in_s3_bucket(fileNamePattern, destinationLocationInBucket):
    bucket = s3.Bucket(environment.platform_s3_bucket_name)
    matchingFiles = bucket.objects.filter(Prefix=fileNamePattern)
    for matchingFile in matchingFiles:
        print(matchingFile.key[matchingFile.key.rfind('/')+1:])
        move_file_from_one_location_to_another_in_s3_bucket(matchingFile.key, destinationLocationInBucket)
