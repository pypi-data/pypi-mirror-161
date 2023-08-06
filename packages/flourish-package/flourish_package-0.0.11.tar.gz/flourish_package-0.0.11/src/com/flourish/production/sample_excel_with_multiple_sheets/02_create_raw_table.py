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
create_raw_table_module = importlib.import_module("common.ingest.excel.02_create_raw_table")
create_raw_table_method = getattr(create_raw_table_module, "execute_for_file_name_pattern")

create_raw_table_method('SAMPLE_EXCEL_WITH_MULTIPLE_SHEETS', "sample_excel_with_multiple_sheets_example_1_#####8#####.xlsx", environment.database_schema_name)