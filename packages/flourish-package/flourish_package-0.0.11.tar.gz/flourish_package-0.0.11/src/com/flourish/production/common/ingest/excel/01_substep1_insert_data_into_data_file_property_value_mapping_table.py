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
ingest_transaction_data_from_excel_data_file_into_transaction_tables = importlib.import_module("helper.ingest_transaction_data_from_excel_data_file_into_transaction_tables_"+environment.database)
ingest_data_into__data_file_property_value_mapping__table = getattr(ingest_transaction_data_from_excel_data_file_into_transaction_tables, "ingest_data_into__data_file_property_value_mapping__table")

def execute_for_file_name_pattern(source, fileNamePattern, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "name_pattern",
        fileNamePattern
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_status_RFMS_using_file_details_id(schema, row.id)

        if(len(runDetails) > 0):
            result = "SUCCESS"
            runDetail = runDetails.iloc[0]
            result = ingest_data_into__data_file_property_value_mapping__table(runDetail.id, row.id, row.received_location_pattern+'/'+runDetail.file_name_in_received_folder, 'EntityDetails', 'A:B', None, 0, 0)
            print('01_substep1_insert_data_into_data_file_property_value_mapping_table: '+result)
            """
            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
            updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )
            """