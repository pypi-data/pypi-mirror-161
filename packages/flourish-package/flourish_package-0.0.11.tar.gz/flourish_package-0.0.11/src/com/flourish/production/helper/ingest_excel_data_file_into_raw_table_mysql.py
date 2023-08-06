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

def ingestDataIntoRawTable(fileNameWithS3Location, sheetName, headerStartRow, columnSpan, schemaName, tableName):
    
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print('__________________________________________________')
    print(fileNameWithS3Location)
    print(sheetName)
    print(headerStartRow)
    print(columnSpan)
    print('__________________________________________________')

    result = "SUCCESS"

    try:
        data_from_file = pandas.read_excel(fileNameWithS3Location, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, usecols=helper_methods.getColumnSpan(columnSpan))
        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        #data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        data_from_file.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location[:fileNameWithS3Location.rfind(".")]+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding='utf-8')
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataIntoRawTableImproved(fileNameWithS3Location, sheetName, headerStartRow, columnSpan, schemaName, tableName, file_details_id):
   
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print('__________________________________________________')
    print(fileNameWithS3Location)
    print(sheetName)
    print(headerStartRow)
    print(columnSpan)
    print('__________________________________________________')

    result = "SUCCESS" 
    
    try:
        source_file_column_to_table_column_mapping = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_source_file_column_to_table_column_mapping_from_s3_with_condition("file_details_id", file_details_id)
        source_file_column_to_table_column_mapping.sort_values('source_file_column_order')

        data_from_file = pandas.read_excel(fileNameWithS3Location, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, usecols=helper_methods.getColumnSpan(columnSpan))
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        data_from_file = helper_methods.change_datatype_of_columns_in_source_file_based_on_source_file_to_column_mapping_table(data_from_file, source_file_column_to_table_column_mapping)
        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        #data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)

        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        data_from_file.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location[:fileNameWithS3Location.rfind(".")]+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding='utf-8')
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataIntoRawTableWithReportingPeriod(fileNameWithS3Location, sheetName, headerStartRow, dataStartRow, columnSpan, schemaName, tableName, reportingPeriod):

    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print('__________________________________________________')
    print(fileNameWithS3Location)
    print(sheetName)
    print(headerStartRow)
    print(columnSpan)
    print('__________________________________________________')

    result = "SUCCESS"

    try:
        data_from_file = pandas.read_excel(fileNameWithS3Location, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, skiprows=range(headerStartRow+1, dataStartRow), usecols=helper_methods.getColumnSpan(columnSpan))
        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        #data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
        data_from_file['reporting_period'] = reportingPeriod
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        data_from_file.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location[:fileNameWithS3Location.rfind(".")]+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding='utf-8')
        
        data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result

def ingestDataIntoRawTableForReporting(master_ingestion_raw_source_file_detail, runDetail, reportingMetaData):

    fileNameWithS3Location = master_ingestion_raw_source_file_detail.received_location_pattern+'/'+runDetail.file_name_in_received_folder
    sheetName = master_ingestion_raw_source_file_detail.sheet_name
    headerStartRow = master_ingestion_raw_source_file_detail.header_row_index
    dataStartRow = master_ingestion_raw_source_file_detail.data_start_row_index
    columnSpan = master_ingestion_raw_source_file_detail.data_column_span
    schemaName = master_ingestion_raw_source_file_detail.schema_name
    tableName = master_ingestion_raw_source_file_detail.table_name

    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print('__________________________________________________')
    print(fileNameWithS3Location)
    print(sheetName)
    print(headerStartRow)
    print(columnSpan)
    print('__________________________________________________')

    result = "SUCCESS"

    try:
        source_file_column_to_table_column_mapping = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_source_file_column_to_table_column_mapping_from_s3_with_condition("file_details_id", master_ingestion_raw_source_file_detail.id)
        source_file_column_to_table_column_mapping.sort_values('source_file_column_order')
        key_columns_in_table = source_file_column_to_table_column_mapping.query("is_key_column == 'Y'")
        print('********** key columns for table: ', master_ingestion_raw_source_file_detail.table_name, ' is/are: ', key_columns_in_table.table_column_name.tolist())

        data_from_file = pandas.read_excel(fileNameWithS3Location, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, skiprows=range(headerStartRow+1, dataStartRow), usecols=helper_methods.getColumnSpan(columnSpan))
        data_from_file = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_file)
        data_from_file = helper_methods.change_datatype_of_columns_in_source_file_based_on_source_file_to_column_mapping_table(data_from_file, source_file_column_to_table_column_mapping)
        data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
        data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
        #data_from_file = helper_methods.strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_from_file)
        #data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
        data_from_file['reporting_period'] = reportingMetaData['reportingPeriod']
        data_from_file['report_file_name'] = reportingMetaData['reportFileName']
        data_from_file['report_remarks'] = reportingMetaData['reportRemarks']
        data_from_file['comments'] = reportingMetaData['comments']
        print('********** data_from_file: ', len(data_from_file))
        data_from_file["load_timestamp"] = executionDateWithTimeWithDashes

        data_from_file.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

        dBConnectionEngine = create_engine(environment.database_connection_string)

        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = fileNameWithS3Location[:fileNameWithS3Location.rfind(".")]+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file.to_csv(f, index=False, header=False, line_terminator='\n', encoding='utf-8')
        
        if(len(data_from_file) > 0):
            data_from_file.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    except Exception as e:
        print('Error while ingesting data into the raw table')
        print(e)
        result = "FAILURE"
    finally:
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    return result
