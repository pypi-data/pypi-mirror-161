import os
from datetime import datetime
import boto3
from helper import environment

s3 = boto3.resource('s3')

def get_the_oldest_file_matching_a_given_pattern_in_an_s3_location(bucketName, locationInsideBucket, fileNamePattern):
    fileToMove = {
        'Bucket': bucketName,
        'Key': locationInsideBucket+'/'+fileNamePattern
    }
    s3.meta.client.move(fileToMove, bucketName, locationInsideBucket+'/received/'+datetime.now().strftime("%Y-%m-%d"))

def getNamesOfFilesInGivenS3Location(bucket, s3PathPrefix):

    fileNames = []

    s3_client = boto3.client('s3')

    session = boto3.Session(aws_access_key_id='AKIARPVUS76HTYKVJAIJ', 
        aws_secret_access_key='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')

    s3 = session.resource('s3')
    bucket_object = s3.Bucket(bucket)

    for file_object in bucket_object.objects.filter(Prefix = s3PathPrefix):
        fileNames.append(file_object.key)

    return fileNames

def uncompressGZCompressedCSVFileIntoCSVFile(bucket, prefix, fileName, input_extension, output_extension):
    s3Client = boto3.client('s3')

    for object in s3Client.list_objects_v2(Bucket=bucket, Prefix=prefix+fileName+input_extension)['Contents']:
        print(object)
        if object['Size'] <= 0:
            continue

        print(object['Key'])
        r = s3Client.select_object_content(
            Bucket=bucket,
            Key=object['Key'],
            ExpressionType='SQL',
            Expression="select * from s3object",
            InputSerialization={'CompressionType': 'GZIP', 'CSV': {'RecordDelimiter': '\n', 'FieldDelimiter': ','}},
            OutputSerialization={'CSV': {'QuoteFields': 'ASNEEDED', 'RecordDelimiter': '\n', 'FieldDelimiter': ',', 'QuoteCharacter': '"', 'QuoteEscapeCharacter': '"'}}
        )

        f = open(fileName+output_extension, "wb")

        for event in r['Payload']:
            if 'Records' in event:
                records = event['Records']['Payload']
                f.write(records)

        f.close()

    object = s3.Object(bucket, prefix+fileName+output_extension)
    object.put(Body=open(fileName+output_extension, 'rb'))

    os.remove(fileName+output_extension)