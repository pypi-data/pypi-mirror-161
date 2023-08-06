import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import db_operations

def execute(schema, run_details, rule_mapping, rule):
    print('****************************************RUN DETAILS****************************************')
    print('Run Id: ', run_details.id, ', File Details Id: ', run_details.file_details_id, ', Actual File Name: ', run_details.actual_file_name, ', File Name in Received Folder: ', run_details.file_name_in_received_folder, ', File Size: ', run_details.file_size, ', Number of Rows in File: ', run_details.number_of_rows, ', Run Status: ', run_details.status_code)
    print('****************************************RULE DETAILS****************************************')
    print('Rule Id: ', rule.id, ', Rule Code: ', rule.code, ', Rule Description: ', rule.description, ', Rule to Apply on: ', rule.to_apply_on, ', Is Rule Mandatory: ', rule.is_mandatory)
    print('****************************************RULE FILE MAPPING DETAILS****************************************')
    print('Rule File Mapping Id: ', rule_mapping.id, ', Rule Id: ', rule_mapping.rule_id, ', File Details Id: ', rule_mapping.file_details_id, ', Column to Apply Rule on: ', rule_mapping.column_id)
    print('******************************************************************************************')

    #Step 1: Get the file_details_id
    file_details_id = rule_mapping.file_details_id

    result = "SUCCESS"

    #Step 2: Using the file_details_id, get the received_location_pattern, file_name_in_received_folder, sheet_name, header_row_index, data_column_span and other columns that are necessary to create the dataframe on which the rule will be executed.
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_with_condition(
        'id',
        file_details_id
    )
    if(len(master_ingestion_raw_source_file_details) > 0):
        row = master_ingestion_raw_source_file_details.iloc[0]
        file_name_delimiter = row.name_delimiter

        #Step 3: Using the file_details_id, name_delimiter and actual_file_name from run_details, get the sequence number of this file
        file_sequence = get_file_sequence_by_splitting_file_name(file_details_id, file_name_delimiter, run_details.actual_file_name)

        #Step 4: Using the file_details_id, name_delimiter and actual_file_name of the last run from the last run_details, get the sequence number of the last file
        last_actual_file_name = get_actual_file_name_of_last_successfully_loaded_file_into_raw_table(schema, file_details_id)
        last_sequence = get_file_sequence_by_splitting_file_name(file_details_id, file_name_delimiter, last_actual_file_name)

        rule_execution_details = {}
        rule_execution_details["file_load_details_id"] = run_details.id
        rule_execution_details["rule_id"] = rule.id
        if(last_sequence == -1 or file_sequence == last_sequence+1):
            rule_execution_details["status_code"] = 'S'
            rule_execution_details["status_description"] = 'File sequence one more than the last file'
        else:
            rule_execution_details["status_code"] = 'SF'
            rule_execution_details["status_description"] = 'File sequence NOT one more than the last file'
            result = 'FAILURE'
        db_operations.insert_rule_check_details_for_run(schema, rule_execution_details)
    return result

def get_file_sequence_by_splitting_file_name(file_details_id, file_name_delimiter, actual_file_name):
    file_name_parts_array = actual_file_name.split(file_name_delimiter)
    i=0
    master_ingestion_raw_source_file_name_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_name_details_from_s3_with_condition(
        'file_details_id', 
        file_details_id
    )
    master_ingestion_raw_source_file_name_details.sort_values('index_in_file_name')
    for row in master_ingestion_raw_source_file_name_details.itertuples():
        if row.meaning == 'SEQUENCE' and len(file_name_parts_array) > i and isinstance(file_name_parts_array[i], int):
            return file_name_parts_array[i]
        else:
            i = i+1
    return -1

def get_actual_file_name_of_last_successfully_loaded_file_into_raw_table(schema, file_details_id):
    lastRunDetails = db_operations.get_most_recent_run_details_with_status_level_greater_than_equal_to_the_given_status_using_file_details_id(schema, file_details_id, 'RTLS')
    if(lastRunDetails != ''):
        return lastRunDetails.actual_file_name
    return ''
