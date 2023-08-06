import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame

def execute(source, schema, raw_table_name):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source(
        source
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        print(
            row.id, ', ', row.drop_location_pattern, ', ', row.received_location_pattern, ', ', row.source, ', ', row.file_type, ', ',
            row.file_extension, ', ', row.name_pattern, ', ', row.name_delimiter, ', ', row.sheet_name, ', ', row.header_row_index, ', ',
            row.data_column_span, ', ', row.schema_name, ', ', row.table_name, ', ', row.frequency, ', ', row.from_day_or_date, ', ',
            row.to_day_or_date, ', ', row.start_month 
        )