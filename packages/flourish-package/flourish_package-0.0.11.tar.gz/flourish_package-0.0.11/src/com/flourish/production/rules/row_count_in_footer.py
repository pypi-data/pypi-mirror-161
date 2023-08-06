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

        #Step 3: Using the file_details_id, get the file_name_in_received_folder
        file_name_in_received_folder = run_details.file_name_in_received_folder

        source_file_column_to_table_column_mapping = helper_methods.create_data_frame_from_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv', '', row.file_encoding, 0)
        
        if(source_file_column_to_table_column_mapping.dtypes["file_details_id"] in ['int64', 'float64']):
            columns_in_table = source_file_column_to_table_column_mapping.query("file_details_id == "+str(file_details_id)).sort_values('source_file_column_order')
        else:
            columns_in_table = source_file_column_to_table_column_mapping.query("file_details_id == '"+str(file_details_id)+"'").sort_values('source_file_column_order')
        
        column_names_in_table = columns_in_table.table_column_name
        
        footer_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_footer_row_details_from_s3_with_condition("file_details_id", file_details_id)
        print('Number of Footer Components in Table: ', row.table_name, ' is/are: ', len(footer_details))

        rule_execution_details = {}
        rule_execution_details["file_load_details_id"] = run_details.id
        rule_execution_details["rule_id"] = rule.id
        rule_execution_details["status_code"] = 'S'
        rule_execution_details["status_description"] = ''
        try:
            #Step 4: Using the received_location_pattern, file_name_in_received_folder, sheet_name, header_row_index, data_column_span, get the data of the file in a dataframe
            if("XLS" in file_extension):
                rule_execution_details["status_description"] = 'This rule is not applicable for Excel files (as of now)'
                print('This rule is not applicable for Excel files (as of now)')
            else:
                with open(row.received_location_pattern+'/'+file_name_in_received_folder, 'rb') as file:
                    file.seek(-2, os.SEEK_END)
                    while file.read(1) != b'\n':
                        file.seek(-2, os.SEEK_CUR)
                    footer = file.readline().decode()
                    footer = footer.replace("\n", "")
                    footer = footer.replace("\t", "")
                    footer = footer.replace("\r", "")
                    footer_components = footer.split(',' if(pandas.isna(row.file_delimiter) or not row.file_delimiter) else row.file_delimiter)
                    print('Footer Components: ', footer_components)

                for footer_detail in footer_details.itertuples():
                    if footer_detail.footer_index_meaning == 'ROW_COUNT' or footer_detail.footer_index_meaning == 'ROWCOUNT':
                        if not pandas.isna(footer_detail.related_file_header_column) and footer_detail.related_file_header_column:
                            row_count_value = footer_components[footer_detail.footer_index] if len(footer_components) > footer_detail.footer_index else -1
                            row_count_column_name = footer_detail.related_file_header_column
                            print('Rowcount value from footer for column: ', footer_detail.related_file_header_column, ' is: ', row_count_value)

                            if float(row_count_value) >= 0:
                                data_from_file = helper_methods.create_data_frame_from_csv(row.received_location_pattern+'/'+file_name_in_received_folder, row.file_delimiter, row.file_encoding, row.number_of_footer_rows)
                                if len(data_from_file.columns) > 0:
                                    data_from_file.columns = column_names_in_table

                                    #Step 5: Finding sum of the row count column
                                    column_sum = data_from_file[row_count_column_name].sum()
                                    print('Sum of all rows for column: ', row_count_column_name, ' is: ', column_sum)

                                    if column_sum == row_count_value:
                                        rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' Rowcount value in footer for column: ' + row_count_column_name + ' is equal to sum of all the rows for the column in the file.'
                                        print('Rowcount value in footer for column: ' + row_count_column_name + ' is equal to sum of all the rows for the column in the file.')
                                    else:
                                        rule_execution_details["status_code"] = 'F'
                                        rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' Rowcount value in footer for column: ' + row_count_column_name + ' is NOT equal to sum of all the rows for the column in the file.'
                                        print('Rowcount value in footer for column: ' + row_count_column_name + ' is NOT equal to sum of all the rows for the column in the file.')
                                        result = 'FAILURE'
                                
                                else:
                                    rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' There are NO ROWS in the file.'
                                    print('There are NO ROWS in the file.')
                            else:
                                rule_execution_details["status_code"] = 'F'
                                rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' Rowcount value NOT present for column: ' + row_count_column_name + ' in the file footer.'
                                print('Rowcount value NOT present for column: ' + row_count_column_name + ' in the file footer.')
                                result = 'FAILURE'
                        else:
                            rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' Rowcount value not present in the footer master.'
                            print('Rowcount value not present in the footer master.')
        except Exception as e:
            result = 'FAILURE'
            rule_execution_details["status_code"] = 'F'
            rule_execution_details["status_description"] = rule_execution_details["status_description"] + ' ' + str(e)
            print(e)
        finally:
            db_operations.insert_rule_check_details_for_run(schema, rule_execution_details)
    return result
