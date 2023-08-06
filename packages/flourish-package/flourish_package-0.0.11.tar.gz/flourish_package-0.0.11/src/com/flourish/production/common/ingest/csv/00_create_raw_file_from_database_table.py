import pyodbc
import pandas
import s3fs
from datetime import datetime
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import helper_methods
#from com.flourish.production.helper import helper_methods
from helper import environment

def execute(table_name_with_schema, table_name):
    msSqlDbConnection = environment.msSqlDbConnection

    #data_from_mssql = pandas.read_sql(sql='select * from '+table_name_with_schema, con=msSqlDbConnection, parse_dates=[replace_with_comma_separated_column_names_that_need_to_be_parsed_as_date])
    data_from_mssql = pandas.read_sql(sql='select * from '+table_name_with_schema, con=msSqlDbConnection)
    data_from_mssql.columns = data_from_mssql.columns.lower()
    print('********** date_from_mssql: ', len(data_from_mssql))

    executionDateWithTime = datetime.now().strftime('%Y%m%d%H%M%S')

    s3 = s3fs.S3FileSystem(anon=False)
    dataFileName = environment.platform_s3_bucket_name+'/'+environment.folder_inside_platform_s3_bucket_for_raw_source_files+'/profisee/'+table_name+'_'+executionDateWithTime+'.csv'
    with s3.open(dataFileName, 'w') as f:
        data_from_mssql.to_csv(f, index=False, line_terminator='\n')

    msSqlDbConnection.close()
    del msSqlDbConnection   