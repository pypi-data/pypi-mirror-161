from sqlalchemy import create_engine
from helper import environment

def create(rawTableName):
    table_to_create = rawTableName.replace("_raw", "_source_aligned")

    dBConnectionEngine = create_engine(environment.database_connection_string)
    dBConnection = dBConnectionEngine.connect()

    table_to_create_with_schema = environment.database_schema_name+'.'+table_to_create
    dBConnection.execute("""
        drop table if exists %s;
        create table %s as select * from %s where 1=2;
        alter table %s add column row_start_date timestamp;
        alter table %s add column row_end_date timestamp;
        alter table %s add column row_status_code integer;
    """ % (table_to_create_with_schema, table_to_create_with_schema, environment.database_schema_name+'.'+rawTableName, table_to_create_with_schema, table_to_create_with_schema, table_to_create_with_schema))

    dBConnection.close()
    del dBConnection
    dBConnectionEngine.dispose()
    del dBConnectionEngine
