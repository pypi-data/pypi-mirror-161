import pandas
from sqlalchemy import create_engine
import s3fs
import numpy
from helper import environment

dBConnectionEngine = create_engine(environment.database_connection_string)

dBConnection = dBConnectionEngine.connect()
data_from_table = pandas.read_sql('select * from '+environment.database_schema_name+'.master_ingestion_source_file_column_to_table_column_mapping', dBConnection)
data_from_table = data_from_table.replace(numpy.nan, '', regex=True)

print('********** data_from_table: ', len(data_from_table))

s3 = s3fs.S3FileSystem(anon=False)
dataFileName = environment.platform_s3_bucket_name+'/processed/'+environment.database_schema_name+'/master_ingestion_source_file_column_to_table_column_mapping.csv'
with s3.open(dataFileName, 'w') as f:
    data_from_table.to_csv(f, index=False, line_terminator='\n')

dBConnection.close()
del dBConnection
dBConnectionEngine.dispose()
del dBConnectionEngine