import pandas
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
from helper import convert_file_to_utf8_format

import importlib
ingest_csv_data_file_into_raw_table = importlib.import_module("helper.ingest_csv_data_file_into_raw_table_"+environment.database)
ingestDataWithDelimiterIntoRawTableWithReportingPeriod = getattr(ingest_csv_data_file_into_raw_table, "ingestDataWithDelimiterIntoRawTableWithReportingPeriod")

def execute(source, schema, tableName, reportingPeriod):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "table_name",
        tableName
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schema, row.id, '\'TDQFPS\',\'TDQFS\'')

        if(len(runDetails) > 0):
            runDetail = runDetails.iloc[0]

            if(not pandas.isna(row.file_encoding) and row.file_encoding and not row.file_encoding is 'utf-8'):
                convert_file_to_utf8_format.convert(row.received_location_pattern+'/'+runDetail.file_name_in_received_folder, row.file_encoding)

                fileName = runDetail.file_name_in_received_folder[:runDetail.file_name_in_received_folder.rfind(".")]
                fileExtension = runDetail.file_name_in_received_folder[runDetail.file_name_in_received_folder.rfind("."):]
                targetFileName = fileName+'_utf8'+fileExtension

                result = ingestDataWithDelimiterIntoRawTableWithReportingPeriod(
                    row.received_location_pattern+'/'+targetFileName,
                    ',' if(pandas.isna(row.file_delimiter) or not row.file_delimiter) else row.file_delimiter,
                    row.file_encoding,
                    row.number_of_footer_rows,
                    row.schema_name,
                    row.table_name,
                    reportingPeriod
                )
            else:
                result = ingestDataWithDelimiterIntoRawTableWithReportingPeriod(
                    row.received_location_pattern+'/'+runDetail.file_name_in_received_folder,
                    ',' if(pandas.isna(row.file_delimiter) or not row.file_delimiter) else row.file_delimiter,
                    row.file_encoding,
                    row.number_of_footer_rows,
                    row.schema_name,
                    row.table_name,
                    reportingPeriod
                )

            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
            updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )
