from sqlalchemy import create_engine
from helper import environment

def truncate(schemaName, tableName):
    result = "SUCCESS"
    try:
        dBConnectionEngine = create_engine(environment.database_connection_string)
        dBConnection = dBConnectionEngine.connect()

        dBConnection.execute("""
            truncate table %s;
        """ % (schemaName+'.'+tableName))
    except Exception as e:
        print(e)
        result = str(e)
    finally:
        dBConnection.close()
        del dBConnection
        dBConnectionEngine.dispose()
        del dBConnectionEngine
        return result
