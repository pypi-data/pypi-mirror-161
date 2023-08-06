import pandas
from sqlalchemy import create_engine
import s3fs
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDirectory)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helper import environment

dBConnectionEngine = create_engine(environment.database_connection_string)

def copy_data_from_master_ingestion_raw_source_file_details_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_raw_source_file_details where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_raw_source_file_details: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_raw_source_file_name_details_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_raw_source_file_name_details where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_raw_source_file_name_details: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_name_details.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_raw_source_file_footer_row_details_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_raw_source_file_footer_row_details where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_raw_source_file_footer_row_details: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_footer_row_details.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_source_file_column_to_table_column_mapping_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select max(id) id, file_details_id, table_column_name, table_column_type, source_aligned_table_column_type, source_file_column_name, source_file_column_type, is_key_column, source_file_column_order from '+environment.database_schema_name+'.master_ingestion_source_file_column_to_table_column_mapping group by file_details_id, table_column_name, table_column_type, source_aligned_table_column_type, source_file_column_name, source_file_column_type, is_key_column, source_file_column_order', dBConnection)

    print('********** rows in master_ingestion_source_file_column_to_table_column_mapping: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_data_quality_rules_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_data_quality_rules where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_data_quality_rules: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_data_quality_rules.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection    

def copy_data_from_master_ingestion_raw_source_file_data_quality_rules_mapping_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_raw_source_file_data_quality_rules_mapping where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_raw_source_file_data_quality_rules_mapping: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_data_quality_rules_mapping.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_status_code_level_mapping_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_status_code_level_mapping', dBConnection)

    print('********** rows in master_ingestion_status_code_level_mapping: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_status_code_level_mapping.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

def copy_data_from_master_ingestion_source_file_column_to_valid_value_mapping_into_s3():
    dBConnection = dBConnectionEngine.connect()
    data_from_database = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_source_file_column_to_valid_value_mapping where status = \'A\'', dBConnection)

    print('********** rows in master_ingestion_source_file_column_to_valid_value_mapping: ', len(data_from_database))

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_valid_value_mapping.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_database.to_csv(f, index=False, line_terminator='\n')

    dBConnection.close()
    del dBConnection

copy_data_from_master_ingestion_raw_source_file_details_into_s3()
copy_data_from_master_ingestion_raw_source_file_name_details_into_s3()
copy_data_from_master_ingestion_raw_source_file_footer_row_details_into_s3()
copy_data_from_master_ingestion_source_file_column_to_table_column_mapping_into_s3()
copy_data_from_master_ingestion_data_quality_rules_into_s3()
copy_data_from_master_ingestion_raw_source_file_data_quality_rules_mapping_into_s3()
copy_data_from_master_ingestion_status_code_level_mapping_into_s3()
copy_data_from_master_ingestion_source_file_column_to_valid_value_mapping_into_s3()

dBConnectionEngine.dispose()
del dBConnectionEngine