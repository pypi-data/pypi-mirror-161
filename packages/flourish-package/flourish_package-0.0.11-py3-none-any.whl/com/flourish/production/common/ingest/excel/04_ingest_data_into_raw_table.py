import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import environment
from helper import db_operations

import importlib
ingest_excel_data_file_into_raw_table = importlib.import_module("helper.ingest_excel_data_file_into_raw_table_"+environment.database)
ingestDataIntoRawTable = getattr(ingest_excel_data_file_into_raw_table, "ingestDataIntoRawTable")

def execute(source, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source(
        source
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schema, row.id, '\'TDQFPS\',\'TDQFS\'')

        if(len(runDetails) > 0):
            result = "SUCCESS"
            runDetail = runDetails.iloc[0]

            result = ingestDataIntoRawTable(
                row.received_location_pattern+'/'+runDetail.file_name_in_received_folder,
                row.sheet_name,
                row.header_row_index,
                row.data_column_span,
                row.schema_name,
                row.table_name
            )

            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
            updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )

def execute_for_file_with_one_sheet(source, schema, tableName):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "table_name",
        tableName
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schema, row.id, '\'TDQFPS\',\'TDQFS\'')

        if(len(runDetails) > 0):
            result = "SUCCESS"
            runDetail = runDetails.iloc[0]
            result = ingestDataIntoRawTable(
                row.received_location_pattern+'/'+runDetail.file_name_in_received_folder,
                row.sheet_name,
                row.header_row_index,
                row.data_column_span,
                row.schema_name,
                row.table_name
            )

            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
            updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )

def execute_for_file_name_pattern(source, fileNamePattern, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "name_pattern",
        fileNamePattern
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schema, row.id, '\'TDQFPS\',\'TDQFS\'')

        if(len(runDetails) > 0):
            result = "SUCCESS"
            runDetail = runDetails.iloc[0]
            result = ingestDataIntoRawTable(
                row.received_location_pattern+'/'+runDetail.file_name_in_received_folder,
                row.sheet_name,
                row.header_row_index,
                row.data_column_span,
                row.schema_name,
                row.table_name
            )

            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
            updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )
