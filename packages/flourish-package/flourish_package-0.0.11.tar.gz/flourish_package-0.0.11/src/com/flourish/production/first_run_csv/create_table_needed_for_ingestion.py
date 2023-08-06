import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import create_table_in_database_using_csv_data_file_structure_without_columns_for_source_alignment
from helper import create_raw_history_table_in_database_using_raw_table_details
from helper import create_source_aligned_table_in_database_using_raw_table_details
from helper import create_source_aligned_history_table_in_database_using_raw_table_details
from helper import environment

master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
    "SAMPLE_CSV", 
    "table_name", 
    "sample_csv_example_1_raw"
)

if(len(master_ingestion_raw_source_file_details) > 0):
    row = master_ingestion_raw_source_file_details.iloc[0]

    """
    fileName = 'sample_csv_example_1_20220730002400.csv'
    create_table_in_database_using_csv_data_file_structure_without_columns_for_source_alignment.create_table(
        row.id, 
        row.drop_location_pattern, 
        fileName, 
        row.file_delimiter, 
        row.file_encoding, 
        row.number_of_footer_rows, 
        environment.database_schema_name, 
        row.table_name, 
        False
    )
    """
    """
    create_raw_history_table_in_database_using_raw_table_details.create(
        row.table_name
    )
    """
    """
    create_source_aligned_table_in_database_using_raw_table_details.create(
        row.table_name
    )
    """
    """
    create_source_aligned_history_table_in_database_using_raw_table_details.create(
        row.table_name
    )
    """