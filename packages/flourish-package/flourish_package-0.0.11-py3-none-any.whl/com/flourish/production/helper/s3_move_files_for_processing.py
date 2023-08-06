import boto3
from datetime import datetime
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
import re

def s3ReturnOldestFile(bucket, s3PathPrefix, fileNamePrefix, fileTypeWithDot):
    all_files = {}
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket, Prefix=s3PathPrefix)

    fileType = s3PathPrefix + fileNamePrefix
    oldestFileName = ''

    if(bucket is not None and s3PathPrefix is not None and fileNamePrefix is not None):
        for response in response_iterator:
            for object_data in response['Contents']:
                key = object_data['Key']
                lastModified = object_data['LastModified']
                if key.startswith(fileType):
                    if key.endswith(fileTypeWithDot):
                        key = key.replace(s3PathPrefix, '')
                        all_files[key] = lastModified
        if(len(all_files) > 0):
            oldestFileName = list(all_files.keys())[0]
    return oldestFileName

def returnTimestamp():
    timeKey = '_' + datetime.now().strftime('%Y%m%d%H%M%S%f')
    return timeKey

def applyTimestampSuffix(fileName):
    timeKey = returnTimestamp()
    file_prefix = os.path.splitext(fileName)[0]
    file_extension = os.path.splitext(fileName)[1]
    finalFileName = file_prefix + timeKey + file_extension
    return finalFileName

def s3CopyRawToProcessed(sourceBucket, sourceKey, destBucket, destKey):
    s3 = boto3.resource('s3')
    copy_source = {'Bucket': sourceBucket, 'Key': sourceKey}
    s3.meta.client_copy(copy_source, destBucket, destKey)
    return destBucket+destKey

def s3ReturnSourceFileKey(sourcePrefix, derivedSourceFileName):
    sourceFileKey = sourcePrefix + derivedSourceFileName
    return sourceFileKey

def s3DeleteSourceFile(sourceBucket, sourceFileKey):
    if not (sourceBucket is None and sourceFileKey is None):
        s3 = boto3.resource("s3")
        obj = s3.Object(sourceBucket, sourceFileKey)
        obj.delete()
    return (sourceBucket + sourceFileKey)

def s3MoveFileToProcessed(sourceBucket, sourcePrefix, sourceFileNameBeginsWith, sourceFileTypeWithDot, destinationBucket, destinationPrefix, deleteSourceFile=False):
    oldestFile = s3ReturnOldestFile(sourceBucket, sourcePrefix, sourceFileNameBeginsWith, sourceFileTypeWithDot)
    finalFileName = applyTimestampSuffix(oldestFile)
    sourceKey = s3ReturnSourceFileKey(sourcePrefix, oldestFile)
    destinationKey = s3ReturnSourceFileKey(destinationPrefix, finalFileName)
    stringOutput = s3CopyRawToProcessed(sourceBucket, sourceKey, destinationBucket, destinationKey)
    print('Destination File: ', stringOutput)
    if deleteSourceFile:
        s3DeleteSourceFile(sourceBucket, sourceKey)
    return stringOutput

def s3ReturnOldestFileMatchingTheGivenPattern(bucket, s3PathPrefix, fileNamePattern, fileTypeWithDot):
    all_files = {}
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket, Prefix=s3PathPrefix)

    fileType = s3PathPrefix + fileNamePattern
    oldestFileName = ''

    if(bucket is not None and s3PathPrefix is not None and fileNamePattern is not None):
        for response in response_iterator:
            for object_data in response['Contents']:
                key = object_data['Key']
                lastModified = object_data['LastModified']
                match = re.match(fileType, key)
                if match:
                    if key.lower().endswith(fileTypeWithDot.lower()):
                        key = key.replace(s3PathPrefix, '')
                        all_files[key] = lastModified
        if(len(all_files) > 0):
            oldestFileName = list(all_files.keys())[0]
    return oldestFileName

def s3GetAllFilesMatchingTheGivenPattern(bucket, s3PathPrefix, fileNamePattern, fileTypeWithDot):
    all_files = {}
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket, Prefix=s3PathPrefix)

    fileType = s3PathPrefix + fileNamePattern
    oldestFileName = ''

    if(bucket is not None and s3PathPrefix is not None and fileNamePattern is not None):
        for response in response_iterator:
            for object_data in response['Contents']:
                key = object_data['Key']
                match = re.match(fileType, key)
                if match:
                    if key.lower().endswith(fileTypeWithDot.lower()):
                        key = key.replace(s3PathPrefix, '')
                        all_files.append(key)
    return all_files
