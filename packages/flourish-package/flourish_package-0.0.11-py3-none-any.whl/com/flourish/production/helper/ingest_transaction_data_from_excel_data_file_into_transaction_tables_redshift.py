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

def ingest_data_into__data_file_property_value_mapping__table(file_load_details_id, file_details_id, fileNameWithS3Location, sheetName, columnSpan, headerStartRow, dataStartRowIndex, numberOfFooterRows):
    result = "SUCCESS"
    columnNameArray = ['property_name', 'property_value']
    data_from_file = helper_methods.create_data_frame_from_excel(fileNameWithS3Location, sheetName, columnSpan, headerStartRow, dataStartRowIndex, numberOfFooterRows)
    
    if len(data_from_file.columns) > 0:
        executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_from_file.columns = columnNameArray
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
        data_from_file.insert(0, 'file_load_details_id', file_load_details_id)
        data_from_file.insert(1, 'file_details_id', file_details_id)
        data_from_file['created_on'] = executionDateWithTimeWithDashes
        print('********** data_from_file: ', len(data_from_file))

        try:
            dBConnectionEngine = create_engine(environment.database_connection_string)
            dBConnection = dBConnectionEngine.connect()

            s3 = s3fs.S3FileSystem(anon=False)
            dataFileName = fileNameWithS3Location+'.csv'
            with s3.open(dataFileName, 'w') as f:
                data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding='utf-8')
            
            dBConnection.execute("""
                COPY %s
                from '%s'
                iam_role 'replace_with_the_correct_iam_role'
                FILLRECORD
                ACCEPTINVCHARS AS '-'
                csv;
            """ % (environment.database_schema_name+'.data_file_property_value_mapping', dataFileName))
        except Exception as e:
            result = 'Error while ingesting data into data_file_property_value_mapping table'
            print('Error while ingesting data into data_file_property_value_mapping table')
            print(e)
        finally:
            dBConnection.close()
            del dBConnection
            dBConnectionEngine.dispose()
            del dBConnectionEngine
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result
