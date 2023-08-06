import pandas
from helper import environment

def get_master_ingestion_raw_source_file_details_from_s3():
    master_ingestion_raw_source_file_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv')
    #master_ingestion_raw_source_file_details = master_ingestion_raw_source_file_details.replace(numpy.nan, '', regex=True)
    print('********** master_ingestion_raw_source_file_details: ', len(master_ingestion_raw_source_file_details))
    return master_ingestion_raw_source_file_details

def get_master_ingestion_raw_source_file_details_from_s3_for_source(source):
    master_ingestion_raw_source_file_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv')
    #master_ingestion_raw_source_file_details = master_ingestion_raw_source_file_details.replace(numpy.nan, '', regex=True)
    master_ingestion_raw_source_file_details.query("source == '"+source+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_details for source: ', source, ' is: ', len(master_ingestion_raw_source_file_details))
    return master_ingestion_raw_source_file_details

def get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(source, extraConditionColumn, extraConditionValue):
    master_ingestion_raw_source_file_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv')
    #master_ingestion_raw_source_file_details = master_ingestion_raw_source_file_details.replace(numpy.nan, '', regex=True)
    master_ingestion_raw_source_file_details.query("source == '"+source+"'", inplace=True)
    if isinstance(extraConditionValue, (float, int)):
        if(master_ingestion_raw_source_file_details.dtypes[extraConditionColumn] in ['int64', 'float64']):
            master_ingestion_raw_source_file_details.query(extraConditionColumn+" == "+str(extraConditionValue), inplace=True)
        else:
            master_ingestion_raw_source_file_details.query(extraConditionColumn+" == '"+str(extraConditionValue)+"'", inplace=True)
    else:
        master_ingestion_raw_source_file_details.query(extraConditionColumn+" == '"+str(extraConditionValue)+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_details for source: ', source, ' and '+(extraConditionColumn+" == '"+str(extraConditionValue)+"'")+' is: ', len(master_ingestion_raw_source_file_details))
    return master_ingestion_raw_source_file_details

def get_master_ingestion_raw_source_file_details_from_s3_for_source_with_conditions(source, extraConditionsKeyValue):
    master_ingestion_raw_source_file_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv')
    #master_ingestion_raw_source_file_details = master_ingestion_raw_source_file_details.replace(numpy.nan, '', regex=True)
    master_ingestion_raw_source_file_details.query("source == '"+source+"'", inplace=True)
    if(len(extraConditionsKeyValue) > 0):
        for key in extraConditionsKeyValue:
            if isinstance(extraConditionsKeyValue[key], (float, int)):
                if(master_ingestion_raw_source_file_details.dtypes[key] in ['int64', 'float64']):
                    master_ingestion_raw_source_file_details.query(key+" == "+str(extraConditionsKeyValue[key]), inplace=True)
                else:
                    master_ingestion_raw_source_file_details.query(key+" == '"+str(extraConditionsKeyValue[key])+"'", inplace=True)
            else:
                master_ingestion_raw_source_file_details.query(key+" == '"+str(extraConditionsKeyValue[key])+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_details for source: ', source, ' and '+str(extraConditionsKeyValue)+' is: ', len(master_ingestion_raw_source_file_details))
    return master_ingestion_raw_source_file_details

def get_master_ingestion_raw_source_file_details_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_raw_source_file_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_details.csv')
    #master_ingestion_raw_source_file_details = master_ingestion_raw_source_file_details.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_raw_source_file_details.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_raw_source_file_details.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_raw_source_file_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_raw_source_file_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_details for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_raw_source_file_details))
    return master_ingestion_raw_source_file_details

def get_master_ingestion_data_quality_rules_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_data_quality_rules = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_data_quality_rules.csv')
    #master_ingestion_data_quality_rules = master_ingestion_data_quality_rules.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_data_quality_rules.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_data_quality_rules.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_data_quality_rules.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_data_quality_rules.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_data_quality_rules for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_data_quality_rules))
    return master_ingestion_data_quality_rules

def get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_raw_source_file_data_quality_rules_mapping = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_data_quality_rules_mapping.csv')
    #master_ingestion_raw_source_file_data_quality_rules_mapping = master_ingestion_raw_source_file_data_quality_rules_mapping.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_raw_source_file_data_quality_rules_mapping.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_raw_source_file_data_quality_rules_mapping.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_raw_source_file_data_quality_rules_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_raw_source_file_data_quality_rules_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_data_quality_rules_mapping for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_raw_source_file_data_quality_rules_mapping))
    return master_ingestion_raw_source_file_data_quality_rules_mapping

def get_master_ingestion_raw_source_file_name_details_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_raw_source_file_name_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_raw_source_file_name_details.csv')
    #master_ingestion_raw_source_file_name_details = master_ingestion_raw_source_file_name_details.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_raw_source_file_name_details.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_raw_source_file_name_details.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_raw_source_file_name_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_raw_source_file_name_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_raw_source_file_name_details for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_raw_source_file_name_details))
    return master_ingestion_raw_source_file_name_details

def get_master_ingestion_source_file_column_to_table_column_mapping_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_source_file_column_to_table_column_mapping = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv')
    #master_ingestion_source_file_column_to_table_column_mapping = master_ingestion_source_file_column_to_table_column_mapping.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_source_file_column_to_table_column_mapping.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_source_file_column_to_table_column_mapping for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_source_file_column_to_table_column_mapping))
    return master_ingestion_source_file_column_to_table_column_mapping

def get_record_count_from_master_ingestion_source_file_column_to_table_column_mapping_for_condition(conditionColumn, conditionValue):
    master_ingestion_source_file_column_to_table_column_mapping = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv')
    #master_ingestion_source_file_column_to_table_column_mapping = master_ingestion_source_file_column_to_table_column_mapping.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_source_file_column_to_table_column_mapping.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_source_file_column_to_table_column_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_source_file_column_to_table_column_mapping for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_source_file_column_to_table_column_mapping))
    return len(master_ingestion_source_file_column_to_table_column_mapping)

def get_master_ingestion_source_file_column_to_valid_value_mapping_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_source_file_column_to_valid_value_mapping = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_valid_value_mapping.csv')
    #master_ingestion_source_file_column_to_valid_value_mapping = master_ingestion_source_file_column_to_valid_value_mapping.replace(numpy.nan, '', regex=True)
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_source_file_column_to_valid_value_mapping.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_source_file_column_to_valid_value_mapping.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_source_file_column_to_valid_value_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_source_file_column_to_valid_value_mapping.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_source_file_column_to_valid_value_mapping for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_source_file_column_to_valid_value_mapping))
    return master_ingestion_source_file_column_to_valid_value_mapping

def get_master_ingestion_source_file_footer_row_details_from_s3_with_condition(conditionColumn, conditionValue):
    master_ingestion_source_file_footer_row_details = pandas.read_csv('s3://'+environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_footer_row_details.csv')
    if isinstance(conditionValue, (float, int)):
        if(master_ingestion_source_file_footer_row_details.dtypes[conditionColumn] in ['int64', 'float64']):
            master_ingestion_source_file_footer_row_details.query(conditionColumn+" == "+str(conditionValue), inplace=True)
        else:
            master_ingestion_source_file_footer_row_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    else:
        master_ingestion_source_file_footer_row_details.query(conditionColumn+" == '"+str(conditionValue)+"'", inplace=True)
    print('********** master_ingestion_source_file_footer_row_details for '+(conditionColumn+" == '"+str(conditionValue)+"'")+' is: ', len(master_ingestion_source_file_footer_row_details))
    return master_ingestion_source_file_footer_row_details