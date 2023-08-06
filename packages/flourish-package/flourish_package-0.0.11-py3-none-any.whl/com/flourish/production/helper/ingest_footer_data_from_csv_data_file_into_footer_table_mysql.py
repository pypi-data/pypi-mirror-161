import pandas
from sqlalchemy import create_engine, null
import s3fs
from datetime import datetime
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import helper_methods
#from com.flourish.production.helper import helper_methods
from helper import environment

def ingestDataIntoRawTable(fileNameWithS3Location, fileEncoding, schemaName, tableName):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, '', fileEncoding, 0)
    if(len(data_from_file.columns) > 0):
        result = ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataWithDelimiterIntoRawTable(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows, schemaName, tableName):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows)
    if(len(data_from_file.columns) > 0):
        result = ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file):
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print('__________________________________________________')
    print(fileNameWithS3Location)
    print('__________________________________________________')

    data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
    data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
    #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
    print('********** data_from_file: ', len(data_from_file))
    data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

    try:
        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(fileEncoding) or not fileEncoding) else fileEncoding))
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        #Need to update the data_ingestion_raw_source_file_load_details table
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
