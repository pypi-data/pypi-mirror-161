import pandas
from sqlalchemy import create_engine
import s3fs
from datetime import datetime
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
from helper import helper_methods
#from com.flourish.production.helper import helper_methods
from helper import environment
from helper import get_master_data_file_from_s3_as_data_frame
from helper import db_operations
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_bool_dtype

def execute(source, schemaName, rawTableName, sourceAlignedTableName, bucketName, destinationFolderInsideBucket, destinationFileNameWithoutExtension):
    updateRunDetails = execute_common(source, schemaName, rawTableName, sourceAlignedTableName, bucketName, destinationFolderInsideBucket, destinationFileNameWithoutExtension)

    if "id" in updateRunDetails:
        db_operations.update_run_details(
            schemaName,
            updateRunDetails
        )

def execute_for_multiple_files(source, schemaName, rawTableName, sourceAlignedTableName, bucketName, destinationFolderInsideBucket, destinationFileNameWithoutExtension):
    updateRunDetails = execute_common(source, schemaName, rawTableName, sourceAlignedTableName, bucketName, destinationFolderInsideBucket, destinationFileNameWithoutExtension)

    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "table_name",
        rawTableName
    )

    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_statuses_using_file_details_id(schemaName, row.id, 'RTLS')

        runDetails = runDetails.reset_index() #Super Important

        for index, runDetail in runDetails.iterrows():
            updateRunDetails["id"] = runDetail.id
            db_operations.update_run_details(
                schemaName,
                updateRunDetails
            )

def execute_common(source, schemaName, rawTableName, sourceAlignedTableName, bucketName, destinationFolderInsideBucket, destinationFileNameWithoutExtension):
    executionDate = datetime.now().strftime("%Y-%m-%d")
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    updateRunDetails = {}
    try:
        master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
            source,
            "table_name",
            rawTableName
        )

        if(len(master_ingestion_raw_source_file_details) > 0):
            
            master_ingestion_raw_source_file_detail = master_ingestion_raw_source_file_details.iloc[0]

            runDetails = db_operations.get_run_details_with_given_status_using_file_details_id(schemaName, master_ingestion_raw_source_file_detail.id, 'RTLS')

            if(len(runDetails) > 0):
                runDetail = runDetails.iloc[0]
                
                updateRunDetails["id"] = runDetail.id

                dBConnectionEngine = create_engine(environment.database_connection_string)
                dBConnection = dBConnectionEngine.connect()

                source_file_column_to_table_column_mapping = helper_methods.create_data_frame_from_csv('s3://'+bucketName+'/processed/'+schemaName+'/master_ingestion_source_file_column_to_table_column_mapping.csv', '', master_ingestion_raw_source_file_detail.file_encoding, 0)
                #source_file_column_to_table_column_mapping = source_file_column_to_table_column_mapping.replace(numpy.nan, '', regex=True)
                source_file_column_to_table_column_mapping = source_file_column_to_table_column_mapping.query("file_details_id == "+str(master_ingestion_raw_source_file_detail.id))
                source_file_column_to_table_column_mapping.sort_values('source_file_column_order')
                key_columns_in_table = source_file_column_to_table_column_mapping.query("file_details_id == "+str(master_ingestion_raw_source_file_detail.id)+" and is_key_column == 'Y'")
                print('********** key columns for table: ', rawTableName, ' is/are: ', key_columns_in_table.table_column_name.tolist())

                data_from_raw_table = pandas.read_sql('select * from '+schemaName+'.'+rawTableName, dBConnection)
                data_from_raw_table = helper_methods.remove_database_audit_columns_from_dataframe(data_from_raw_table)
                data_from_raw_table = helper_methods.change_datatype_of_columns_based_on_master_configuration(data_from_raw_table, source_file_column_to_table_column_mapping)
                #data_from_raw_table.set_index(key_columns_in_table.table_column_name.tolist(), inplace=True, verify_integrity=True)
                #data_from_raw_table = data_from_raw_table.replace(numpy.nan, '', regex=True)
                print('********** data_from_raw_table: ', len(data_from_raw_table))

                for column in data_from_raw_table.columns:
                    if is_integer_dtype(data_from_raw_table[column]):
                        data_from_raw_table[column] = data_from_raw_table[column].astype('Int64')
                    elif is_bool_dtype(data_from_raw_table[column]):
                        data_from_raw_table[column] = data_from_raw_table[column].astype('boolean')

                if(len(key_columns_in_table) > 0):
                    data_from_source_aligned_table = pandas.read_sql('select * from '+schemaName+'.'+sourceAlignedTableName+' where row_status_code = 1', dBConnection)
                    #data_from_source_aligned_table = helper_methods.remove_database_audit_columns_from_dataframe(data_from_source_aligned_table)
                    data_from_source_aligned_table = helper_methods.convert_float_column_with_integers_and_nans_to_integer_column(data_from_source_aligned_table)
                    #data_from_source_aligned_table.set_index(key_columns_in_table.table_column_name.tolist(), inplace=True, verify_integrity=True)
                    #data_from_source_aligned_table = data_from_source_aligned_table.replace(numpy.nan, '', regex=True)
                    print('********** data_from_source_aligned_table: ', len(data_from_source_aligned_table))

                    for column in data_from_source_aligned_table.columns:
                        if is_integer_dtype(data_from_source_aligned_table[column]):
                            data_from_source_aligned_table[column] = data_from_source_aligned_table[column].astype('Int64')
                        elif is_bool_dtype(data_from_source_aligned_table[column]):
                            data_from_source_aligned_table[column] = data_from_source_aligned_table[column].astype('boolean')

                    mergedDf1 = data_from_raw_table.merge(data_from_source_aligned_table.drop_duplicates(), on=key_columns_in_table.table_column_name.tolist(), how='outer', indicator=True)

                    columns_in_raw_table = data_from_raw_table.columns
                    columns_in_source_aligned_table = data_from_source_aligned_table.columns

                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned = pandas.DataFrame(mergedDf1[mergedDf1['_merge'] == 'left_only'])
                    #print(to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.columns)
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.drop(helper_methods.drop_columns_ending_with_suffix(to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.columns, '_y'), axis=1, inplace=True)
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.drop(['_merge'], axis=1, inplace=True)
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.rename(columns=helper_methods.change_column_names_by_removing_suffix(to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.columns, '_x'), inplace=True)
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned = to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.loc[:, columns_in_raw_table.values.tolist()]
                    #print(to_insert_df_since_present_in_raw_but_not_present_in_source_aligned.columns)
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned["load_timestamp"] = executionDateWithTimeWithDashes
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned["row_start_date"] = executionDateWithTimeWithDashes
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned["row_end_date"] = environment.platform_maximum_date_value
                    to_insert_df_since_present_in_raw_but_not_present_in_source_aligned["row_status_code"] = 1
                    print('Rows to insert since they are present only in raw and not in source aligned')
                    print(len(to_insert_df_since_present_in_raw_but_not_present_in_source_aligned))

                    to_delete_df_since_present_in_source_aligned_but_not_present_in_raw = pandas.DataFrame(mergedDf1[mergedDf1['_merge'] == 'right_only'])
                    to_delete_df_since_present_in_source_aligned_but_not_present_in_raw.drop(helper_methods.drop_columns_ending_with_suffix(to_delete_df_since_present_in_source_aligned_but_not_present_in_raw.columns, '_x'), axis=1, inplace=True)
                    to_delete_df_since_present_in_source_aligned_but_not_present_in_raw.drop(['_merge'], axis=1, inplace=True)
                    to_delete_df_since_present_in_source_aligned_but_not_present_in_raw.rename(columns=helper_methods.change_column_names_by_removing_suffix(to_delete_df_since_present_in_source_aligned_but_not_present_in_raw.columns, '_y'), inplace=True)
                    #No need to update the row_status_code to 0 since this record is still the most recent record
                    #but we did not get anything related to this record in the current file that is being processed.
                    #Currently, we are updating the row_end_date (the date after which a record is not valid in the 
                    #source system) with the current timestamp but this does not consider the lag between when the
                    #record became inactive in the source system and the time when we process the file from the source.
                    #Gradually, we need to plan to get te data from the source systems at a faster cadence.
                    to_delete_df_since_present_in_source_aligned_but_not_present_in_raw["row_end_date"] = executionDateWithTimeWithDashes
                    #to_delete_df_since_present_in_source_aligned_but_not_present_in_raw["row_status_code"] = 0
                    print('Rows where row_end_date needs to be updated since they are present only in source aligned and not in raw')
                    print(len(to_delete_df_since_present_in_source_aligned_but_not_present_in_raw))

                    concatenated_df_raw_and_source_aligned = pandas.concat([data_from_source_aligned_table, data_from_raw_table])
                    grouped_df_on_all_columns_from_concatenated_df = concatenated_df_raw_and_source_aligned.fillna(0).groupby(list(data_from_raw_table.columns))
                    to_do_nothing_df_idx = [x[0] for x in grouped_df_on_all_columns_from_concatenated_df.groups.values() if len(x) > 1]
                    #print(to_do_nothing_df_idx)
                    to_do_nothing_df_as_no_difference_between_raw_and_source_aligned_records = pandas.DataFrame(data_from_source_aligned_table.iloc[to_do_nothing_df_idx])
                    print('Rows where nothing needs to be done since nothing is different between raw and source aligned.')
                    print(len(to_do_nothing_df_as_no_difference_between_raw_and_source_aligned_records))

                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table = pandas.DataFrame(mergedDf1[mergedDf1['_merge'] == 'both'])
                    #print(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.columns)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.drop(helper_methods.drop_columns_ending_with_suffix(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.columns, '_x'), axis=1, inplace=True)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.drop(['_merge'], axis=1, inplace=True)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.rename(columns=helper_methods.change_column_names_by_removing_suffix(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.columns, '_y'), inplace=True)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table = to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.loc[:, columns_in_source_aligned_table.values.tolist()]
                    #print(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.columns)
                    #print(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table.set_index(key_columns_in_table.table_column_name.tolist(), inplace=True, verify_integrity=True)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table_without_audit_columns = pandas.DataFrame(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table)
                    to_update_status_to_inactive_df_since_newer_row_present_in_raw_table_without_audit_columns = helper_methods.remove_database_audit_columns_from_dataframe(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table_without_audit_columns)

                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table = pandas.DataFrame(mergedDf1[mergedDf1['_merge'] == 'both'])
                    #print(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.columns)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.drop(helper_methods.drop_columns_ending_with_suffix(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.columns, '_y'), axis=1, inplace=True)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.drop(['_merge'], axis=1, inplace=True)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.rename(columns=helper_methods.change_column_names_by_removing_suffix(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.columns, '_x'), inplace=True)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table = to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.loc[:, columns_in_raw_table.values.tolist()]
                    #print(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.columns)
                    #print(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table.set_index(key_columns_in_table.table_column_name.tolist(), inplace=True, verify_integrity=True)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table_without_audit_columns = pandas.DataFrame(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table)
                    to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table_without_audit_columns = helper_methods.remove_database_audit_columns_from_dataframe(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table_without_audit_columns)

                    comparison_df = (to_update_status_to_inactive_df_since_newer_row_present_in_raw_table_without_audit_columns.drop('check_sum', axis=1, errors='ignore').fillna(0)==to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table_without_audit_columns.drop('check_sum', axis=1, errors='ignore').fillna(0)).all(axis=1)

                    to_update_status_to_inactive_df = pandas.DataFrame(to_update_status_to_inactive_df_since_newer_row_present_in_raw_table[~comparison_df])
                    to_update_status_to_inactive_df.reset_index(inplace=True)
                    to_update_status_to_inactive_df = to_update_status_to_inactive_df.loc[:, columns_in_source_aligned_table.values.tolist()]
                    to_update_status_to_inactive_df["row_end_date"] = executionDateWithTimeWithDashes
                    to_update_status_to_inactive_df["row_status_code"] = 0
                    print('Rows to update status to inactive. These are records that are present in source aligned but we have got a newer record in the raw file.')
                    print(len(to_update_status_to_inactive_df))

                    to_insert_with_active_status_df = pandas.DataFrame(to_insert_with_active_status_df_since_old_row_present_in_source_aligned_table[~comparison_df])
                    to_insert_with_active_status_df.reset_index(inplace=True)
                    to_insert_with_active_status_df = to_insert_with_active_status_df.loc[:, columns_in_raw_table.values.tolist()]
                    to_insert_with_active_status_df["load_timestamp"] = executionDateWithTimeWithDashes
                    to_insert_with_active_status_df["row_start_date"] = executionDateWithTimeWithDashes
                    to_insert_with_active_status_df["row_end_date"] = environment.platform_maximum_date_value
                    to_insert_with_active_status_df["row_status_code"] = 1
                    print('Rows to insert with active status. These are records that have come in the raw file but where an older version is present in the source aligned table.')
                    print(len(to_insert_with_active_status_df))

                    final_data_to_insert = pandas.concat([to_insert_df_since_present_in_raw_but_not_present_in_source_aligned, to_delete_df_since_present_in_source_aligned_but_not_present_in_raw, to_insert_with_active_status_df, to_update_status_to_inactive_df, to_do_nothing_df_as_no_difference_between_raw_and_source_aligned_records])

                    if(len(final_data_to_insert) > 0):
                        s3 = s3fs.S3FileSystem(anon=False)
                        dataFileName = bucketName + '/' + destinationFolderInsideBucket + '/' + executionDate + '/' + destinationFileNameWithoutExtension + '_' + datetime.now().strftime('%Y%m%d%H%M%S') +'.csv'
                        with s3.open(dataFileName, 'w', encoding="utf-8") as f:
                            final_data_to_insert.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(master_ingestion_raw_source_file_detail.file_encoding) or not master_ingestion_raw_source_file_detail.file_encoding) else master_ingestion_raw_source_file_detail.file_encoding))

                        dBConnection.execute("""
                            insert into %s select a.*, current_timestamp from %s a;
                            delete from %s where row_status_code = 1;
                            COPY %s
                            from 's3://%s'
                            iam_role 'replace_with_the_iam_role_that_has_permission_to_execute_the_copy_command'
                            FILLRECORD
                            csv;
                        """ % (schemaName+'.'+sourceAlignedTableName+'_history', schemaName+'.'+sourceAlignedTableName, schemaName+'.'+sourceAlignedTableName, schemaName+'.'+sourceAlignedTableName, dataFileName))
                else:
                    print("No key columns so all the rows in the source aligned table will be changed to row_status_code = 0 and all the rows from the raw table will be inserted into source aligned table with ACTIVE status.")
                    data_from_raw_table["row_start_date"] = executionDateWithTimeWithDashes
                    data_from_raw_table["row_end_date"] = environment.platform_maximum_date_value
                    data_from_raw_table["row_status_code"] = 1
                    data_from_raw_table.insert(len(data_from_raw_table.columns)-3, "load_timestamp", executionDateWithTimeWithDashes)
                    
                    #print(data_from_raw_table.columns)

                    final_data_to_insert = pandas.concat([data_from_raw_table])
                    final_data_to_insert["load_timestamp"] = executionDateWithTimeWithDashes

                    #print(final_data_to_insert.columns)

                    if(len(final_data_to_insert) > 0):
                        s3 = s3fs.S3FileSystem(anon=False)
                        dataFileName = bucketName + '/' + destinationFolderInsideBucket + '/' + executionDate + '/' + destinationFileNameWithoutExtension + '_' + datetime.now().strftime('%Y%m%d%H%M%S') +'.csv'
                        with s3.open(dataFileName, 'w', encoding="utf-8") as f:
                            final_data_to_insert.to_csv(f, index=False, header=False, line_terminator='\n', encoding=('utf-8' if (pandas.isna(master_ingestion_raw_source_file_detail.file_encoding) or not master_ingestion_raw_source_file_detail.file_encoding) else master_ingestion_raw_source_file_detail.file_encoding))

                        dBConnection.execute("""
                            insert into %s select a.*, current_timestamp from %s a;
                            update %s set row_status_code = 0, row_end_date = '%s' where row_status_code = 1;
                            COPY %s
                            from 's3://%s'
                            iam_role 'replace_with_the_iam_role_that_has_permission_to_execute_the_copy_command'
                            FILLRECORD
                            csv;
                        """ % (schemaName+'.'+sourceAlignedTableName+'_history', schemaName+'.'+sourceAlignedTableName, schemaName+'.'+sourceAlignedTableName, executionDateWithTimeWithDashes, schemaName+'.'+sourceAlignedTableName, dataFileName))

                dBConnection.close()
                del dBConnection
                dBConnectionEngine.dispose()
                del dBConnectionEngine

                updateRunDetails["status_code"] = 'SAS'
                updateRunDetails["status_description"] = 'Source alignment successful'
    except Exception as e:
        print(e)
        updateRunDetails["status_code"] = 'SAF'
        updateRunDetails["status_description"] = 'Source alignment unsuccessful'
    finally:
        return updateRunDetails