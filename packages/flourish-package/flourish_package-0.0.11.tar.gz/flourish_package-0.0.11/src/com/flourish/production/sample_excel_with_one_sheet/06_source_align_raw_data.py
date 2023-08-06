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
source_aligning_module = importlib.import_module("common.ingest.06_source_align_raw_data_"+environment.database)
source_aligning_method = getattr(source_aligning_module, "execute")

source_aligning_method('SAMPLE_EXCEL_WITH_ONE_SHEET', environment.database_schema_name, "sample_excel_with_one_sheet_example_1_raw", "sample_excel_with_one_sheet_example_1_source_aligned", environment.platform_s3_bucket_name, environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/sample_excel_with_one_sheet', 'sample_excel_with_one_sheet_example_1')