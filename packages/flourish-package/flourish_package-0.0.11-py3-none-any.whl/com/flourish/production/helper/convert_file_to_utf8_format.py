import s3fs
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentDirectory)
sys.path.append(parentDirectory)

def convert(fileNameWithS3Location, fileEncoding):
    fileName = fileNameWithS3Location[:fileNameWithS3Location.rfind(".")]
    fileExtension = fileNameWithS3Location[fileNameWithS3Location.rfind("."):]
    targetFileNameWithS3Location = fileName+'_utf8'+fileExtension
    BLOCKSIZE = 1048576
    s3 = s3fs.S3FileSystem(anon=False)
    with s3.open(fileNameWithS3Location, "r", encoding=fileEncoding) as sourceFile:
        with s3.open(targetFileNameWithS3Location, "w", encoding="utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)