import pandas
from sqlalchemy import create_engine, null
import s3fs
from datetime import datetime
import numpy
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import helper_methods
#from com.flourish.production.helper import helper_methods
from helper import environment

def load_data_into_database_table_from_excel_file_after_source_alignment(bucketName, sourceFolderInsideBucket, sourceFileName, sourceSheetName, headerStartRow, columnSpan, destinationFolderInsideBucket, destinationFileNameWithoutExtension, schemaName, tableName):
    executionDate = datetime.now().strftime("%Y-%m-%d")
    if destinationFileNameWithoutExtension == '':
        destinationFileNameWithoutExtension = sourceFileName[:sourceFileName.rfind(".")]

    dBConnectionEngine = create_engine(environment.database_connection_string)

    data_from_file = helper_methods.create_data_frame_from_excel(
        's3://'+bucketName+'/'+sourceFolderInsideBucket+'/'+executionDate+'/'+sourceFileName, 
        sourceSheetName, columnSpan, headerStartRow, (headerStartRow+1 if headerStartRow else 1), 0
    )
    data_from_file = helper_methods.edit_column_names_of_dataframe_by_removing_special_characters(data_from_file)
    data_from_file = helper_methods.format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_file)
    data_from_file = data_from_file.replace(numpy.nan, '', regex=True)
    print('********** data_from_file: ', len(data_from_file))

    dBConnection = dBConnectionEngine.connect()
    data_from_table = pandas.read_sql('select * from '+schemaName+'.'+tableName, dBConnection)
    data_from_table = helper_methods.remove_database_audit_columns_from_dataframe(data_from_table)
    data_from_table = data_from_table.replace(numpy.nan, '', regex=True)
    print('********** data_from_table: ', len(data_from_table))

    concatenated_data = pandas.concat([data_from_file, data_from_table])
    concatenated_data = concatenated_data.reset_index(drop=True)
    print('concatenated data: ', len(concatenated_data))

    duplicate_data = concatenated_data[concatenated_data.duplicated(keep=False)]
    duplicate_data = duplicate_data.drop_duplicates(keep='first')
    duplicate_data = duplicate_data.reset_index(drop=True)
    print('duplicate data: ', len(duplicate_data))

    if len(duplicate_data) > 0:
        data_from_file_to_insert_or_update_into_table = pandas.concat([duplicate_data, data_from_file])
        data_from_file_to_insert_or_update_into_table = data_from_file_to_insert_or_update_into_table.reset_index(drop=True)
        data_from_file_to_insert_or_update_into_table = data_from_file_to_insert_or_update_into_table.drop_duplicates(keep=False)
        print('data_from_file_to_insert_or_update_into_table: ', len(data_from_file_to_insert_or_update_into_table))
    else:
        data_from_file_to_insert_or_update_into_table = data_from_file
        print('data_from_file_to_insert_or_update_into_table:: ', len(data_from_file_to_insert_or_update_into_table))

    if len(duplicate_data) > 0:
        data_in_table_to_be_updated_or_deleted = pandas.concat([duplicate_data, data_from_table])
        data_in_table_to_be_updated_or_deleted = data_in_table_to_be_updated_or_deleted.reset_index(drop=True)
        data_in_table_to_be_updated_or_deleted = data_in_table_to_be_updated_or_deleted.drop_duplicates(keep=False)
        print('data_in_table_to_be_updated_or_deleted: ', len(data_in_table_to_be_updated_or_deleted))
    else:
        data_in_table_to_be_updated_or_deleted = data_from_table
        print('data_in_table_to_be_updated_or_deleted:: ', len(data_in_table_to_be_updated_or_deleted))

    #distinct_data = concatenated_data.copy()
    #distinct_data = distinct_data.drop_duplicates(keep=False)
    #data_to_be_inserted_updated_deleted_in_table = distinct_data.groupby([distinct_data.columns[0], distinct_data.columns[1]])
    #for key, item in data_to_be_inserted_updated_deleted_in_table:
    #    print(data_to_be_inserted_updated_deleted_in_table.get_group(key))
    #data_to_be_updated_in_table = data_to_be_inserted_updated_deleted_in_table.filter(lambda x: len(x) > 1)
    #print(data_to_be_updated_in_table)
    #data_to_be_updated_in_table = data_to_be_updated_in_table.groupby([data_to_be_updated_in_table.columns[0], data_to_be_updated_in_table.columns[1]]).nth(0).reset_index()
    #print('data_to_be_updated_in_table: ', len(data_to_be_updated_in_table))

    if(len(data_from_file_to_insert_or_update_into_table) > 0):
        data_from_file_to_insert_or_update_into_table["row_start_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_from_file_to_insert_or_update_into_table["row_end_date"] = environment.platform_maximum_date_value
        data_from_file_to_insert_or_update_into_table["row_status_code"] = 1
        data_from_file_to_insert_or_update_into_table["load_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = bucketName+'/'+destinationFolderInsideBucket+'/'+executionDate+'/'+destinationFileNameWithoutExtension+'_'+datetime.now().strftime('%Y%m%d%H%M%S')+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_file_to_insert_or_update_into_table.to_csv(f, index=False, header=False, line_terminator='\n')
            
        data_from_file_to_insert_or_update_into_table.to_sql(name=tableName, con=dBConnectionEngine, schema=schemaName, if_exists='append', index=False)
    
    dBConnection.close()
    del dBConnection
    dBConnectionEngine.dispose()
    del dBConnectionEngine
