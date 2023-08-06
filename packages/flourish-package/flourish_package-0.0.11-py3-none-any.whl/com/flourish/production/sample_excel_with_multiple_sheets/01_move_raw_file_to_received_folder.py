import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import s3_move_files_for_processing
from helper import environment

import importlib
move_raw_file_module = importlib.import_module("common.ingest.excel.01_move_raw_file_to_received_folder")
move_raw_file_method = getattr(move_raw_file_module, "execute_for_file_name_pattern")

fileName = s3_move_files_for_processing.s3ReturnOldestFileMatchingTheGivenPattern(environment.platform_s3_bucket_name, environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/sample_excel_with_multiple_sheets/', "sample_excel_with_multiple_sheets_example_1_\d{14}", ".xlsx")

move_raw_file_method('SAMPLE_EXCEL_WITH_MULTIPLE_SHEETS', "sample_excel_with_multiple_sheets_example_1_#####8#####.xlsx", fileName)