from sqlalchemy import create_engine
from helper import environment

def copy(schemaName, tableName):
    result = "SUCCESS"
    try:
        dBConnectionEngine = create_engine(environment.database_connection_string)
        dBConnection = dBConnectionEngine.connect()
        dBConnection.execute("""
            insert into %s select a.*, current_timestamp from %s a;
        """ % (schemaName+'.'+tableName+'_history', schemaName+'.'+tableName))
        result = "SUCCESS"
    except Exception as e:
        print('Error while copying data from raw table to history table')
        print(e)
        result = str(e)
    else:
        result = "SUCCESS"
    finally:
        dBConnection.close()
        del dBConnection
        dBConnectionEngine.dispose()
        del dBConnectionEngine
        return result