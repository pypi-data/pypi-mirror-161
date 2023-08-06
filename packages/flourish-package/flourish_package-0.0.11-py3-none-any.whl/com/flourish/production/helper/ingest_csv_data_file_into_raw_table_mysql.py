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
from helper import get_master_data_file_from_s3_as_data_frame

def ingestDataIntoRawTable(fileNameWithS3Location, fileEncoding, schemaName, tableName):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, '', fileEncoding, 0)
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataIntoRawTableImproved(fileNameWithS3Location, fileEncoding, schemaName, tableName, file_details_id):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, '', fileEncoding, 0)
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommonImproved(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file, file_details_id)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataWithDelimiterIntoRawTable(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows, schemaName, tableName, columns_to_remove=None):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows)

    data_from_file.columns = data_from_file.columns.str.lower()
    if columns_to_remove is not None:
        for column_to_remove in columns_to_remove:
            if column_to_remove in data_from_file.columns:
                data_from_file.drop(column_to_remove, inplace=True, axis=1)
    
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataWithDelimiterIntoRawTableImproved(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows, schemaName, tableName, file_details_id, columns_to_remove=None):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows)

    data_from_file.columns = data_from_file.columns.str.lower()
    if columns_to_remove is not None:
        for column_to_remove in columns_to_remove:
            if column_to_remove in data_from_file.columns:
                data_from_file.drop(column_to_remove, inplace=True, axis=1)
    
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommonImproved(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file, file_details_id)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file):
    result = "SUCCESS"
    try:
        executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(fileEncoding) or not fileEncoding) else fileEncoding))
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataIntoRawTableCommonImproved(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file, file_details_id):
    result = "SUCCESS"
    try:
        executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        source_file_column_to_table_column_mapping = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_source_file_column_to_table_column_mapping_from_s3_with_condition("file_details_id", file_details_id)
        source_file_column_to_table_column_mapping.sort_values('source_file_column_order')

        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        data_from_file = helper_methods.change_datatype_of_columns_in_source_file_based_on_source_file_to_column_mapping_table(data_from_file, source_file_column_to_table_column_mapping)
        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(fileEncoding) or not fileEncoding) else fileEncoding))
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataIntoRawTableCommonWithReportingPeriod(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file, reportingPeriod):
    result = "SUCCESS"
    try:
        executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["reporting_period"] = reportingPeriod
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(fileEncoding) or not fileEncoding) else fileEncoding))
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataWithDelimiterIntoRawTableWithReportingPeriod(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows, schemaName, tableName, reportingPeriod, columns_to_remove=None):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows)

    data_from_file.columns = data_from_file.columns.str.lower()
    if columns_to_remove is not None:
        for column_to_remove in columns_to_remove:
            if column_to_remove in data_from_file.columns:
                data_from_file.drop(column_to_remove, inplace=True, axis=1)
    
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommonWithReportingPeriod(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file, reportingPeriod)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result

def ingestDataWithDelimiterIntoRawTableWithBlankColumnsInTheEnd(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows, schemaName, tableName, blankColumnsToAddInTheEnd, columns_to_remove=None):
    result = "SUCCESS"
    data_from_file = helper_methods.create_data_frame_from_csv(fileNameWithS3Location, fileDelimiter, fileEncoding, numberOfFooterRows)

    data_from_file.columns = data_from_file.columns.str.lower()
    if columns_to_remove is not None:
        for column_to_remove in columns_to_remove:
            if column_to_remove in data_from_file.columns:
                data_from_file.drop(column_to_remove, inplace=True, axis=1)

    for blankColumnToAdd in blankColumnsToAddInTheEnd:
        data_from_file[blankColumnToAdd] = null
    
    if len(data_from_file.columns) > 0:
        result = ingestDataIntoRawTableCommon(fileNameWithS3Location, fileEncoding, schemaName, tableName, data_from_file)
    else:
        print('____________________ NO DATA IN FILE TO INGEST ____________________')
    return result
