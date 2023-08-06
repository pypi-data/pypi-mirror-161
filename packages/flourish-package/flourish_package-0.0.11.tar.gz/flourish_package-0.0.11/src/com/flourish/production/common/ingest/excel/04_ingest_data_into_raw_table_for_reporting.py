import os, sys
import pandas
import datetime
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
ingestDataIntoRawTableForReporting = getattr(ingest_excel_data_file_into_raw_table, "ingestDataIntoRawTableForReporting")

def execute_for_file_name_pattern(source, fileNamePattern, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "name_pattern",
        fileNamePattern
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schema, row.id, '\'TDQFPS\',\'TDQFS\'')

        if(len(runDetails) > 0):
            runDetail = runDetails.iloc[0]

            property_value_mappings = db_operations.get_data_file_property_value_mapping_using_file_load_details_id_and_file_details_id(schema, runDetail.id, row.id)
            for property_value_mapping in property_value_mappings.itertuples():
                if(property_value_mapping.property_name == 'Reporting End Date'):
                    result = "SUCCESS"

                    if(isinstance(property_value_mapping.property_value, datetime.date)):
                        reportingPeriod = property_value_mapping.property_value
                    else:
                        try:
                            reportingPeriod = pandas.to_datetime(property_value_mapping.property_value.replace(' 00:00:00', ''), format='%d/%m/%Y')
                        except Exception as e:
                            print('reportingPeriod is not in DD/MM/YYYY format')
                            reportingPeriod = pandas.to_datetime(property_value_mapping.property_value.replace(' 00:00:00', ''), format='%Y-%m-%d')
                    reportingMetaData = {
                        'reportingPeriod': reportingPeriod,
                        'reportFileName': runDetail.file_name_in_received_folder,
                        'reportRemarks': '',
                        'comments': ''
                    }

                    result = ingestDataIntoRawTableForReporting(
                        row,
                        runDetail,
                        reportingMetaData
                    )
                
                    updateRunDetails = {}
                    updateRunDetails["id"] = runDetail.id
                    updateRunDetails["status_code"] = 'RTLS' if result == "SUCCESS" else 'RTLF'
                    updateRunDetails["status_description"] = 'File ingested into raw table successfully' if result == "SUCCESS" else 'File ingestion into raw table unsuccessful'
                    db_operations.update_run_details(
                        schema,
                        updateRunDetails
                    )
