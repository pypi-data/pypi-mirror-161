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
create_raw_table_module = importlib.import_module("common.ingest.csv.02_create_raw_table")
create_raw_table_method = getattr(create_raw_table_module, "execute")

create_raw_table_method('SAMPLE_CSV', environment.database_schema_name, "sample_csv_example_1_raw")