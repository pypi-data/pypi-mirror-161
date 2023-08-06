import os, sys

import pandas
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import create_table_in_database_using_csv_data_file_structure_without_columns_for_source_alignment
from helper import db_operations
from helper import copy_data_from_raw_table_to_history_table
from math import isnan

def execute(source, schema, tableName):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "table_name",
        tableName
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_status_RFMS_using_file_details_id(schema, row.id)

        if(len(runDetails) > 0):
            row_ = runDetails.iloc[0]

            result = copy_data_from_raw_table_to_history_table.copy(schema, row.table_name)

            runDetails = {}
            runDetails["id"] = row_.id
            if(result == "SUCCESS"):
                runDetails["status_code"] = 'RTTHTS'
                runDetails["status_description"] = 'Data copied from raw table to raw_history table successfully'
                db_operations.update_run_details(
                    schema,
                    runDetails
                )

                result = create_table_in_database_using_csv_data_file_structure_without_columns_for_source_alignment.create_table(
                    row.id,
                    row.received_location_pattern,
                    row_.file_name_in_received_folder,
                    ',' if(pandas.isna(row.file_delimiter) or not row.file_delimiter) else row.file_delimiter,
                    row.file_encoding,
                    row.number_of_footer_rows,
                    schema,
                    row.table_name,
                    False
                )

                runDetails = {}
                runDetails["id"] = row_.id
                if(result == "SUCCESS"):
                    runDetails["status_code"] = 'RTDCS'
                    runDetails["status_description"] = 'Raw table dropped and recreated successfully'
                else:
                    runDetails["status_code"] = 'RTDCF'
                    runDetails["status_description"] = result
                db_operations.update_run_details(
                    schema,
                    runDetails
                )
            else:
                runDetails["status_code"] = 'RTTHTF'
                runDetails["status_description"] = result
                db_operations.update_run_details(
                    schema,
                    runDetails
                )
