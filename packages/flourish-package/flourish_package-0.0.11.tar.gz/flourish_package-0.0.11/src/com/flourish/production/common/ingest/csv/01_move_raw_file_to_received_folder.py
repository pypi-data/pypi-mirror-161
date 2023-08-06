import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import file_move_operations
from helper import db_operations
from helper import helper_methods
from helper import environment
from datetime import datetime
from helper import s3_move_files_for_processing

def execute(source, fileName, tableName):
    if fileName:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            tableName
        )
        if(len(master_ingestion_raw_source_file_details) > 0):
            row = master_ingestion_raw_source_file_details.iloc[0]
            print(
                row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
                row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
                row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
                row.to_day_or_date, ', ', row.start_month 
            )

            fileSize = helper_methods.getFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInCSVFile(row.drop_location_pattern, fileName, row.file_encoding)

            runDetails = {}
            runDetails["file_details_id"] = row.id
            runDetails["actual_file_name"] = fileName
            runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
            runDetails["file_size"] = fileSize
            runDetails["number_of_rows"] = numberOfRows

            try:
                file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                    row.drop_location_pattern,
                    fileName,
                    row.received_location_pattern,
                    receivedFileNameWithExtension
                )
            except Exception as e:
                runDetails["status_code"] = 'RFMF'
                runDetails["status_description"] = str(e)
            else:
                runDetails["status_code"] = 'RFMS'
                runDetails["status_description"] = 'File moved from raw to received successfully'
            finally:
                db_operations.insert_run_details(
                    environment.database_schema_name,
                    runDetails
                )

def execute_with_delimiter(source, fileName, fileDelimiter, tableName):
    if fileName:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            tableName
        )
        if(len(master_ingestion_raw_source_file_details) > 0):
            row = master_ingestion_raw_source_file_details.iloc[0]
            print(
                row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
                row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
                row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
                row.to_day_or_date, ', ', row.start_month 
            )

            fileSize = helper_methods.getFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInCSVFileWithGivenDelimiter(row.drop_location_pattern, fileName, fileDelimiter, row.file_encoding)

            runDetails = {}
            runDetails["file_details_id"] = row.id
            runDetails["actual_file_name"] = fileName
            runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
            runDetails["file_size"] = fileSize
            runDetails["number_of_rows"] = numberOfRows

            try:
                file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                    row.drop_location_pattern,
                    fileName,
                    row.received_location_pattern,
                    receivedFileNameWithExtension
                )
            except Exception as e:
                runDetails["status_code"] = 'RFMF'
                runDetails["status_description"] = str(e)
            else:
                runDetails["status_code"] = 'RFMS'
                runDetails["status_description"] = 'File moved from raw to received successfully'
            finally:
                db_operations.insert_run_details(
                    environment.database_schema_name,
                    runDetails
                )

def execute_with_file_location_file_name_prefix_and_file_type(source, bucketName, fileLocationInsideBucket, fileNamePrefix, fileType, tableName):
    fileName = s3_move_files_for_processing.s3ReturnOldestFile(bucketName, fileLocationInsideBucket, fileNamePrefix, fileType)
    if fileName:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            tableName
        )
        if(len(master_ingestion_raw_source_file_details) > 0):
            row = master_ingestion_raw_source_file_details.iloc[0]
            print(
                row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
                row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
                row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
                row.to_day_or_date, ', ', row.start_month 
            )

            fileSize = helper_methods.getFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInCSVFile(row.drop_location_pattern, fileName, row.file_encoding)

            runDetails = {}
            runDetails["file_details_id"] = row.id
            runDetails["actual_file_name"] = fileName
            runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
            runDetails["file_size"] = fileSize
            runDetails["number_of_rows"] = numberOfRows

            try:
                file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                    row.drop_location_pattern,
                    fileName,
                    row.received_location_pattern,
                    receivedFileNameWithExtension
                )
            except Exception as e:
                runDetails["status_code"] = 'RFMF'
                runDetails["status_description"] = str(e)
            else:
                runDetails["status_code"] = 'RFMS'
                runDetails["status_description"] = 'File moved from raw to received successfully'
            finally:
                db_operations.insert_run_details(
                    environment.database_schema_name,
                    runDetails
                )

def execute_with_delimiter_file_location_file_name_prefix_and_file_type(source, fileDelimiter, bucketName, fileLocationInsideBucket, fileNamePrefix, fileType, tableName):
    fileName = s3_move_files_for_processing.s3ReturnOldestFile(bucketName, fileLocationInsideBucket, fileNamePrefix, fileType)
    if fileName:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            tableName
        )
        if(len(master_ingestion_raw_source_file_details) > 0):
            row = master_ingestion_raw_source_file_details.iloc[0]
            print(
                row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
                row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
                row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
                row.to_day_or_date, ', ', row.start_month 
            )

            fileSize = helper_methods.getFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInCSVFileWithGivenDelimiter(row.drop_location_pattern, fileName, fileDelimiter, row.file_encoding)

            runDetails = {}
            runDetails["file_details_id"] = row.id
            runDetails["actual_file_name"] = fileName
            runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
            runDetails["file_size"] = fileSize
            runDetails["number_of_rows"] = numberOfRows

            try:
                file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                    row.drop_location_pattern,
                    fileName,
                    row.received_location_pattern,
                    receivedFileNameWithExtension
                )
            except Exception as e:
                runDetails["status_code"] = 'RFMF'
                runDetails["status_description"] = str(e)
            else:
                runDetails["status_code"] = 'RFMS'
                runDetails["status_description"] = 'File moved from raw to received successfully'
            finally:
                db_operations.insert_run_details(
                    environment.database_schema_name,
                    runDetails
                )

def execute_with_delimiter_without_any_database_operation(source, fileName, fileDelimiter, tableName):
    if fileName:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            tableName
        )
        if(len(master_ingestion_raw_source_file_details) > 0):
            row = master_ingestion_raw_source_file_details.iloc[0]
            print(
                row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
                row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
                row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
                row.to_day_or_date, ', ', row.start_month 
            )

            fileSize = helper_methods.getFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInCSVFileWithGivenDelimiter(row.drop_location_pattern, fileName, fileDelimiter, row.file_encoding)

            runDetails = {}
            runDetails["file_details_id"] = row.id
            runDetails["actual_file_name"] = fileName
            runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
            runDetails["file_size"] = fileSize
            runDetails["number_of_rows"] = numberOfRows

            try:
                file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                    row.drop_location_pattern,
                    fileName,
                    row.received_location_pattern,
                    receivedFileNameWithExtension
                )
            except Exception as e:
                print(e)
