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
ingest_data_into_raw_table_module = importlib.import_module("common.ingest.csv.04_ingest_data_into_raw_table")
ingest_data_into_raw_table_method = getattr(ingest_data_into_raw_table_module, "execute")

ingest_data_into_raw_table_method('SAMPLE_CSV', environment.database_schema_name, "sample_csv_example_1_raw")