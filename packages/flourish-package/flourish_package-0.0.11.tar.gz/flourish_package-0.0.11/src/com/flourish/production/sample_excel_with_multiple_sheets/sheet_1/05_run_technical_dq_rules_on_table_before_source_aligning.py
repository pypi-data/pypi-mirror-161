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
run_dq_rules_on_table_before_source_aligning_module = importlib.import_module("common.ingest.05_run_technical_dq_rules_on_table_before_source_aligning")
run_dq_rules_on_table_before_source_aligning_method = getattr(run_dq_rules_on_table_before_source_aligning_module, "execute")

run_dq_rules_on_table_before_source_aligning_method('SAMPLE_EXCEL_WITH_MULTIPLE_SHEETS', environment.database_schema_name, "sample_excel_with_multiple_sheets_example_1_sheet_1_raw")