import pandas
from sqlalchemy import create_engine
from helper import environment

dBConnectionEngine = create_engine(environment.database_connection_string)

def insert_run_details(schema, runDetails):
    
    insertStatement = 'insert into '+schema+'.data_ingestion_raw_source_file_load_details (file_details_id, actual_file_name, file_name_in_received_folder, file_size, number_of_rows, status_code, status_description) values ('+str(runDetails["file_details_id"])+', \''+runDetails["actual_file_name"]+'\', \''+runDetails["file_name_in_received_folder"]+'\', '+str(runDetails["file_size"])+', '+str(runDetails["number_of_rows"])+', \''+runDetails["status_code"]+'\', \''+runDetails["status_description"]+'\')'
    
    dBConnection = dBConnectionEngine.connect()
    dBConnection.execute("""
        %s;
    """ % (insertStatement))

    dBConnection.close()
    del dBConnection

def update_run_details(schema, runDetails):
    
    updateStatement = 'update '+schema+'.data_ingestion_raw_source_file_load_details set status_code = \''+runDetails["status_code"]+'\', status_description = \''+runDetails["status_description"]+'\' where id = '+str(runDetails["id"])
    
    dBConnection = dBConnectionEngine.connect()
    dBConnection.execute("""
        %s;
    """ % (updateStatement))

    dBConnection.close()
    del dBConnection

def get_run_details_with_status_RFMS_using_file_details_id(schema, file_details_id):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_ingestion_raw_source_file_load_details where file_details_id = '+str(file_details_id)+' and status_code = \'RFMS\' order by move_date', dBConnection)

    dBConnection.close()
    del dBConnection

    return data_from_database

def get_run_details_with_given_status_using_file_details_id(schema, file_details_id, status_code):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_ingestion_raw_source_file_load_details where file_details_id = '+str(file_details_id)+' and status_code = \''+status_code+'\' order by move_date', dBConnection)

    dBConnection.close()
    del dBConnection

    return data_from_database

def get_run_details_with_given_statuses_using_file_details_id(schema, file_details_id, comma_separated_status_codes):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_ingestion_raw_source_file_load_details where file_details_id = '+str(file_details_id)+' and status_code in ('+comma_separated_status_codes+') order by move_date', dBConnection)

    dBConnection.close()
    del dBConnection

    return data_from_database

def get_most_recent_run_details_with_status_level_greater_than_equal_to_the_given_status_using_file_details_id(schema, file_details_id, status_code):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_ingestion_raw_source_file_load_details where file_details_id = '+str(file_details_id)+' and status_code in (select status_code from '+schema+'.master_ingestion_status_code_level_mapping where status_level >= (select status_level from '+schema+'.master_ingestion_status_code_level_mapping where status_code = \''+status_code+'\')) order by move_date desc', dBConnection)

    dBConnection.close()
    del dBConnection

    if len(data_from_database) == 0:
        return pandas.DataFrame()
    else:
        return data_from_database.iloc[0]

def get_run_details_using_id(schema, id):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_ingestion_raw_source_file_load_details where id = '+str(id), dBConnection)

    dBConnection.close()
    del dBConnection

    return data_from_database

def get_data_file_property_value_mapping_using_file_load_details_id_and_file_details_id(schema, file_load_details_id, file_details_id):
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+schema+'.data_file_property_value_mapping where file_load_details_id = '+str(file_load_details_id)+' and file_details_id = '+str(file_details_id), dBConnection)

    dBConnection.close()
    del dBConnection

    return data_from_database

def insert_rule_check_details_for_run(schema, rule_execution_details):
    
    insertStatement = 'insert into '+schema+'.data_ingestion_raw_source_file_load_rule_execution_details (file_load_details_id, rule_id, status_code, status_description) values ('+str(rule_execution_details["file_load_details_id"])+', '+str(rule_execution_details["rule_id"])+', \''+str(rule_execution_details["status_code"])+'\', \''+str((rule_execution_details["status_description"]).replace("'", "''"))+'\')'
    
    dBConnection = dBConnectionEngine.connect()
    dBConnection.execute("""
        %s;
    """ % (insertStatement))

    dBConnection.close()
    del dBConnection

#run_copy_command renamed to load_into_redshift
def load_into_redshift(schema, table_name, s3_location, delimiter, number_of_header_rows_to_ignore):
    dBConnection = dBConnectionEngine.connect()
    dBConnection.execute("""
        COPY %s
        FROM '%s'
        IAM_ROLE 'replace_with_the_right_iam_role'
        DELIMITER '%s'
        IGNOREHEADER %
        FILLRECORD
        ACCEPTINVCHARS AS '-'
        DATEFORMAT 'auto'
        REMOVEQUOTES;
    """ % (schema+'.'+table_name, s3_location, delimiter, number_of_header_rows_to_ignore))

    dBConnection.close()
    del dBConnection

def execute_procedure_with_no_parameters(schema, procedure_name):
    dBConnection = dBConnectionEngine.connect()
    try:
        cursor = dBConnection.cursor()
        cursor.execute('call '+schema+'.'+procedure_name+'()')
        #cursor.callproc(+schema+'.'+procedure_name)
    except Exception as e:
        print(e)
        if cursor:
            cursor.close()
    else:
        cursor.close()
        dBConnection.commit()
    dBConnection.close()
    del dBConnection

def truncate_table(schema, table_name):
    dBConnection = dBConnectionEngine.connect()
    dBConnection.execute("""
        truncate %s;
    """ % (schema+'.'+table_name))

    dBConnection.close()
    del dBConnection
