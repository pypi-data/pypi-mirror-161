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
run_dq_rules_module = importlib.import_module("common.ingest.excel.03_run_technical_dq_rules_on_file")
run_dq_rules_method = getattr(run_dq_rules_module, "execute_for_file_name_pattern")

run_dq_rules_method('SAMPLE_EXCEL_WITH_MULTIPLE_SHEETS', "sample_excel_with_multiple_sheets_example_1_#####8#####.xlsx", environment.database_schema_name)