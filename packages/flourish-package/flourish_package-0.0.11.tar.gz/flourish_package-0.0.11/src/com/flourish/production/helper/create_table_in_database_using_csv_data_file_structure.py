import pandas
from sqlalchemy import create_engine
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import helper_methods
#from com.flourish.production.helper import helper_methods
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_bool_dtype
import math
from helper import environment

file_column_to_table_column_mapping_table_name = 'master_ingestion_source_file_column_to_table_column_mapping'

def create(fileDetailsId, locationInsideBucket, fileName, fileEncoding, rawTableName):
    data_from_file = helper_methods.create_data_frame_from_csv(locationInsideBucket+'/'+fileName, '', fileEncoding, 0)
    if len(data_from_file.columns) > 0:
        dBConnectionEngine = create_engine(environment.database_connection_string)
        dBConnection = dBConnectionEngine.connect()

        file_column_names = data_from_file.columns
        data_from_file.columns = helper_methods.edit_column_names_by_removing_special_characters(data_from_file.columns)
        print(data_from_file.columns)

        insertQueryStructure = 'insert into '+environment.database_schema_name+'.'+file_column_to_table_column_mapping_table_name+' (file_details_id, table_column_name, table_column_type, source_file_column_name, source_file_column_type, is_key_column, source_file_column_order) values ('+str(fileDetailsId)+', \'#table_column_name#\', \'#table_column_type#\', \'#source_file_column_name#\', \'#source_file_column_type#\', \'\', \'#source_file_column_order#\');'

        tableStructure = ''
        finalInsertQuery = ''
        columnOrder = 0

        for column in data_from_file.columns:
            insertQuery = insertQueryStructure
            insertQuery = insertQuery.replace("#table_column_name#", column[0:120]) #This needs to be configurable based on the database we are using since this is a database constraint and is different for different databases.
            insertQuery = insertQuery.replace("#source_file_column_name#", file_column_names[columnOrder])

            columnOrder = columnOrder + 1
            insertQuery = insertQuery.replace("#source_file_column_order#", str(columnOrder))
            if is_datetime64_any_dtype(data_from_file[column]):
                time_dataframe = pandas.DataFrame()
                time_dataframe['time'] = data_from_file[column].map(lambda a: getTime(a))
                time_dataframe = time_dataframe.drop_duplicates(keep = 'first')
                time_dataframe = time_dataframe.reset_index(drop=True)
                #print('time_dataframe: ', len(time_dataframe))
                if len(time_dataframe) == 0 or (len(time_dataframe) == 1 and time_dataframe['time'].iloc[0] == '00:00:00'):
                    tableStructure = tableStructure + column[0:120] + 'date, '
                    insertQuery =  insertQuery.replace("#table_column_type#", 'date')
                    insertQuery =  insertQuery.replace("#source_file_column_type#", 'date')
                else:
                    tableStructure = tableStructure + column[0:120] + 'timestamp, '
                    insertQuery =  insertQuery.replace("#table_column_type#", 'timestamp')
                    insertQuery =  insertQuery.replace("#source_file_column_type#", 'datetime')
            elif is_float_dtype(data_from_file[column]):
                before_decimal_dataframe = pandas.DataFrame()
                before_decimal_dataframe['before_decimal'] = data_from_file[column].map(lambda a: 0 if math.isnan(a) else len(str(int(a)+1)))
                before_decimal_length = before_decimal_dataframe['before_decimal'].max()
                after_decimal_dataframe = pandas.DataFrame()
                after_decimal_dataframe['after_decimal'] = data_from_file[column].map(lambda a: 0 if math.isnan(a) else len(str(a)[str(a).rfind(".")+1:]))
                after_decimal_length = after_decimal_dataframe['after_decimal'].max()
                if after_decimal_length == 0:
                    if(before_decimal_length > 9):
                        tableStructure = tableStructure + column[0:120] + ' bigint, '
                        insertQuery = insertQuery.replace("#table_column_type#", 'bigint')
                    else:
                        tableStructure = tableStructure + column[0:120] + ' integer, '
                        insertQuery = insertQuery.replace("#table_column_type#", 'integer')
                    insertQuery = insertQuery.replace("#source_file_column_type#", 'integer')
                else:
                    tableStructure = tableStructure + column[0:120] + ' numeric('+str(before_decimal_length+3+after_decimal_length+2)+','+str(after_decimal_length+2)+'), '
                    insertQuery = insertQuery.replace("#table_column_type#", 'numeric('+str(before_decimal_length+3+after_decimal_length+2)+','+str(after_decimal_length+2)+')')
                    insertQuery = insertQuery.replace("#source_file_column_type#", 'decimal')
            elif is_integer_dtype(data_from_file[column]):
                number_dataframe = pandas.DataFrame()
                number_dataframe['number'] = data_from_file[column].map(lambda a: 0 if math.isnan(a) else len(str(a)))
                number_length = number_dataframe['number'].max()
                if(number_length > 9):
                    tableStructure = tableStructure + column[0:120] + ' bigint, '
                    insertQuery = insertQuery.replace("#table_column_type#", 'bigint')
                else:
                    tableStructure = tableStructure + column[0:120] + ' integer, '
                    insertQuery = insertQuery.replace("#table_column_type#", 'integer')
                insertQuery = insertQuery.replace("#source_file_column_type#", 'integer')
            elif is_bool_dtype(data_from_file[column]):
                tableStructure = tableStructure + column[0:120] + ' boolean, '
                insertQuery = insertQuery.replace("#table_column_type#", 'boolean')
                insertQuery = insertQuery.replace("#source_file_column_type#", 'boolean')
            else:
                string_dataframe = pandas.DataFrame()
                string_dataframe['string'] = data_from_file[column].map(lambda a: len(str(a)))
                string_length = 0
                if math.isnan(string_dataframe['string'].max()) == False:
                    string_length = string_dataframe['string'].max()
                if string_length > 0:
                    tableStructure = tableStructure + column[0:120] + ' varchar('+str(string_length+100)+'), '
                    insertQuery = insertQuery.replace("#table_column_type#", 'varchar('+str(string_length+100)+')')
                else:
                    tableStructure = tableStructure + column[0:120] + ' varchar, '
                    insertQuery = insertQuery.replace("#table_column_type#", 'varchar')
                insertQuery = insertQuery.replace("#source_file_column_type#", 'varchar')

            finalInsertQuery = finalInsertQuery + insertQuery

        #tableStructure = tableStructure[:tableStructure.rfind(",")]
        tableStructure = tableStructure + 'row_start_date timestamp, row_end_date timestamp, row_status_code integer, load_timestamp timestamp default current_timestamp '
        #print(tableStructure)

        dBConnection.execute("""
                drop table if exists %s;
                create table %s (
                    %s
                );
                %s
            """ % (environment.database_schema_name+'.'+rawTableName, environment.database_schema_name+'.'+rawTableName, tableStructure, finalInsertQuery))
        
        dBConnection.close()
        del dBConnection
        dBConnectionEngine.dispose()
        del dBConnectionEngine
    else:
        print('____________________ data_from_file is null')

def getTime(dateObject):
    if pandas.notnull(dateObject):
        return dateObject.time()
    else:
        return '00:00:00'
