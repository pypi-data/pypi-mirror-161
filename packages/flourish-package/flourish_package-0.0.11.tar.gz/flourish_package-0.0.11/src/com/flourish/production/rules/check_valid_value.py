import pandas
import os, sys
from smart_open import open
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import db_operations
from helper import helper_methods
from helper import environment

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
        #file_name_pattern = row.file_name_pattern
        #file_name_delimiter = row.file_name_delimiter
        schema_name = row.schema_name
        #table_name = row.table_name
        received_location_pattern = row.received_location_pattern
        file_extension = row.file_extension
        sheet_name = row.sheet_name
        header_row_index = row.header_row_index
        data_column_span = row.data_column_span

        #Step 3: Using the file_details_id, get the file_name_in_received_folder
        file_name_in_received_folder = run_details.file_name_in_received_folder

        #Step 4: Using the received_location_pattern, file_name_in_received_folder, sheet_name, header_row_index, data_column_span, get the data of the file in a dataframe
        if("XLS" in file_extension):
            data_from_file = pandas.read_excel(received_location_pattern+'/'+file_name_in_received_folder, sheet_name=(0 if (pandas.isna(sheet_name) or not sheet_name) else sheet_name), header=header_row_index, usecols=helper_methods.getColumnSpan(data_column_span))
        else:
            data_from_file = helper_methods.create_data_frame_from_csv(received_location_pattern+'/'+file_name_in_received_folder, row.file_delimiter, row.file_encoding, row.number_of_footer_rows)

        #Step 5: Match the data type of each column with the details in the master_ingestion_source_file_column_to_table_column_mapping table
        source_file_column_to_table_column_mapping = helper_methods.create_data_frame_from_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv', '', row.file_encoding, 0)
        if(source_file_column_to_table_column_mapping.dtypes["file_details_id"] in ['int64', 'float64']):
            source_file_column_to_table_column_mapping.query("file_details_id == "+str(file_details_id), inplace=True)
        else:
            source_file_column_to_table_column_mapping.query("file_details_id == '"+str(file_details_id)+"'", inplace=True)
        source_file_column_to_table_column_mapping.query("id == "+str(rule_mapping.column_id), inplace=True)

        #Step 6: Using column_id from rule_mapping, get the valid values
        valid_values_for_column = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_source_file_column_to_valid_value_mapping_from_s3_with_condition('column_id', rule_mapping.column_id)
        valid_values = valid_values_for_column.loc[:, "valid_value"]

        result = check_if_only_valid_values_are_present_for_a_column_in_source_file(schema, run_details, rule, data_from_file, source_file_column_to_table_column_mapping, valid_values)
    
    return result

def check_if_only_valid_values_are_present_for_a_column_in_source_file(schema, run_details, rule, source_data_frame, source_file_column_to_table_column_mapping_data_frame, valid_values):
    result = 'SUCCESS'

    try:
        for row in source_file_column_to_table_column_mapping_data_frame.itertuples():
            if len(source_data_frame.columns) > 0:
                values = source_data_frame.loc[:, row.source_file_column_name]
                #values = source_data_frame[row.source_file_column_name]
                values_set = set(values)
                print('All distinct values for column: ', row.source_file_column_name, ' in the file are: ', values_set)
                valid_values_set = set(valid_values)
                print('All valid values for column: ', row.source_file_column_name, ' are: ', valid_values_set)

                difference = values_set - valid_values_set

                rule_execution_details = {}
                rule_execution_details["file_load_details_id"] = run_details.id
                rule_execution_details["rule_id"] = rule.id
                if len(difference) > 0:
                    rule_execution_details["status_code"] = 'F'
                    rule_execution_details["status_description"] = 'There is/are one/more value/s which is/are NOT present in the list of valid values in the metadata'
                    print('There is/are one/more value/s which is/are NOT present in the list of valid values in the metadata')
                    result = 'FAILURE'
                else:
                    rule_execution_details["status_code"] = 'S'
                    rule_execution_details["status_description"] = 'All values are present in the list of valid values'
                    print('All values are present in the list of valid values')
            else:
                rule_execution_details["status_code"] = 'S'
                rule_execution_details["status_description"] = 'There are NO rows in the file'
                print('There are NO rows in the file')
    except Exception as e:
        rule_execution_details["status_code"] = 'F'
        rule_execution_details["status_description"] = str(e)
        print(e)
        result = 'FAILURE'
    finally:
        db_operations.insert_rule_check_details_for_run(schema, rule_execution_details)
        return result