import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import environment

import importlib
ingest_data_into_raw_table_module = importlib.import_module("common.ingest.excel.04_ingest_data_into_raw_table")
ingest_data_into_raw_table_method = getattr(ingest_data_into_raw_table_module, "execute_for_file_with_one_sheet")

ingest_data_into_raw_table_method('SAMPLE_EXCEL_WITH_ONE_SHEET', environment.database_schema_name, "sample_excel_with_one_sheet_example_1_raw")