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

def execute(source, fileName):
    drop_location_pattern_list = []
    name_pattern_list = []
    fileNameList = []
    receivedFileNameList = []
    fileSizeList = []

    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source(
        source
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        print(
            row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
            row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
            row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
            row.to_day_or_date, ', ', row.start_month 
        )

        isAlreadyPresent = False
        for i in range(len(name_pattern_list)):
            if name_pattern_list[i] == row.name_pattern and drop_location_pattern_list[i] == row.drop_location_pattern:
                fileName = fileNameList[i]
                fileSize = fileSizeList[i]
                receivedFileNameWithExtension = receivedFileNameList[i]
                numberOfRows = helper_methods.getNumberOfRowsInExcelFile(row.received_location_pattern, receivedFileNameWithExtension, row.sheet_name, row.header_row_index, row.data_column_span)
                isAlreadyPresent = True
                break
        if(isAlreadyPresent == False):
            fileSize = helper_methods.getExcelFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInExcelFile(row.drop_location_pattern, fileName, row.sheet_name, row.header_row_index, row.data_column_span)

        runDetails = {}
        runDetails["file_details_id"] = row.id
        runDetails["actual_file_name"] = fileName
        runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
        runDetails["file_size"] = fileSize
        runDetails["number_of_rows"] = numberOfRows

        try:
            if isAlreadyPresent == False:
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

            drop_location_pattern_list.append(row.drop_location_pattern)
            name_pattern_list.append(row.name_pattern)
            fileNameList.append(fileName)
            receivedFileNameList.append(receivedFileNameWithExtension)
            fileSizeList.append(fileSize)
        finally:
            db_operations.insert_run_details(
                environment.database_schema_name,
                runDetails
            )

def execute_for_file_with_one_sheet(source, fileName, tableName):
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

            fileSize = helper_methods.getExcelFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInExcelFile(row.drop_location_pattern, fileName, row.sheet_name, row.header_row_index, row.data_column_span)

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

def execute_for_file_name_pattern(source, fileNamePattern, fileName):
    drop_location_pattern_list = []
    name_pattern_list = []
    fileNameList = []
    receivedFileNameList = []
    fileSizeList = []

    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "name_pattern",
        fileNamePattern
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        print(
            row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
            row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
            row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
            row.to_day_or_date, ', ', row.start_month 
        )

        isAlreadyPresent = False
        for i in range(len(name_pattern_list)):
            if name_pattern_list[i] == row.name_pattern and drop_location_pattern_list[i] == row.drop_location_pattern:
                fileName = fileNameList[i]
                fileSize = fileSizeList[i]
                receivedFileNameWithExtension = receivedFileNameList[i]
                numberOfRows = helper_methods.getNumberOfRowsInExcelFile(row.received_location_pattern, receivedFileNameWithExtension, row.sheet_name, row.header_row_index, row.data_column_span)
                isAlreadyPresent = True
                break
        if(isAlreadyPresent == False):
            fileSize = helper_methods.getExcelFileSize(row.drop_location_pattern, fileName)

            executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
            receivedFileName = fileName[:fileName.rfind(".")]
            receivedFileExtension = fileName[fileName.rfind("."):]
            receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension
            numberOfRows = helper_methods.getNumberOfRowsInExcelFile(row.drop_location_pattern, fileName, row.sheet_name, row.header_row_index, row.data_column_span)

        runDetails = {}
        runDetails["file_details_id"] = row.id
        runDetails["actual_file_name"] = fileName
        runDetails["file_name_in_received_folder"] = receivedFileNameWithExtension
        runDetails["file_size"] = fileSize
        runDetails["number_of_rows"] = numberOfRows

        try:
            if isAlreadyPresent == False:
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

            drop_location_pattern_list.append(row.drop_location_pattern)
            name_pattern_list.append(row.name_pattern)
            fileNameList.append(fileName)
            receivedFileNameList.append(receivedFileNameWithExtension)
            fileSizeList.append(fileSize)
        finally:
            db_operations.insert_run_details(
                environment.database_schema_name,
                runDetails
            )

def execute_for_file_with_one_sheet_without_any_database_operation(source, fileName, tableName):
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

        executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")
        receivedFileName = fileName[:fileName.rfind(".")]
        receivedFileExtension = fileName[fileName.rfind("."):]
        receivedFileNameWithExtension = receivedFileName+'_'+executionDateWithTime+receivedFileExtension

        try:
            file_move_operations.move_file_from_raw_folder_into_received_folder_in_platform_s3_bucket(
                row.drop_location_pattern,
                fileName,
                row.received_location_pattern,
                receivedFileNameWithExtension
            )
        except Exception as e:
            print(e)
