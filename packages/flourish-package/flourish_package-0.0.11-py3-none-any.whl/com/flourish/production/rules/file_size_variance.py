import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
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

    #Step 2: Get the variance % from the code of the rule
    variance = get_variance_percentage_by_splitting_rule_code(rule)

    #Step 3: Get the size of this file
    file_size = run_details.file_size

    #Step 4: Get the size of the previous file
    last_run_details = get_run_details_of_last_successfully_loaded_file_into_raw_table(schema, file_details_id)

    rule_execution_details = {}
    rule_execution_details["file_load_details_id"] = run_details.id
    rule_execution_details["rule_id"] = rule.id
    
    last_file_size = 0
    if len(last_run_details) > 0:
        last_file_size = last_run_details.file_size
        if(abs(file_size - last_file_size)*100/last_file_size <= float(variance)):
            rule_execution_details["status_code"] = 'S'
            rule_execution_details["status_description"] = 'Variance in file size in accepted limits'
            print('Variance in file size in accepted limits')
        else:
            rule_execution_details["status_code"] = 'F'
            rule_execution_details["status_description"] = 'Variance in file size > ' + str(variance)
            print('Variance in file size > ' + str(variance))
            result = 'FAILURE'
    else:
        rule_execution_details["status_code"] = 'S'
        rule_execution_details["status_description"] = 'This is the first run'
        print('This is the first run')
    
    db_operations.insert_rule_check_details_for_run(schema, rule_execution_details)
        
    return result

def get_run_details_of_last_successfully_loaded_file_into_raw_table(schema, file_details_id):
    last_run_details = db_operations.get_most_recent_run_details_with_status_level_greater_than_equal_to_the_given_status_using_file_details_id(schema, file_details_id, 'RTLS')
    return last_run_details

def get_variance_percentage_by_splitting_rule_code(rule):
    rule_code_array = rule.code.split('_')
    return rule_code_array[len(rule_code_array)-1]
