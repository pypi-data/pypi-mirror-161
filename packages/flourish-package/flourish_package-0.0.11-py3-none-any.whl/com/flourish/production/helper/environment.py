import pyodbc

database = 'mysql' #'redshift' works too. We need to figure out how do we want to implement other databases
database_schema_name = 'flourish'
platform_maximum_date_value = '2037-12-31 23:59:59'
platform_s3_bucket_name = 'flourish-com-au-test'
folder_inside_platform_s3_bucket_for_raw_source_files = 'raw'
folder_inside_platform_s3_bucket_for_processed_files = 'processed'
database_connection_string = 'mysql+pymysql://flourish_admin:flourish_sk_135(&%@stree-production.c5j8svbtgyi5.ap-south-1.rds.amazonaws.com:3306/flourish'
reporting_period = '2022-06-30'
wealth_fund_name = 'Wealth Personal Superannuation and Pension Fund'
wealth_fund_code = 'WEALTH'
wealth_fund_abn = 92381911598
amp_old_fund_name = 'Super Directions Fund'
amp_new_fund_name = 'AMP Super Fund'
amp_fund_code = 'SDF'
amp_fund_abn = 78421957449

rse_name = 'Super Directions Fund'

"""
msSqlDbConnection = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};' #NOTE: The driver version could be different and might need to be changed in different scenarios
    'Server=replace_with_url_of_the_database;'
    'Database=replace_with_name_of_the_database;'
    'UID=replace_with_database_username;'
    'PWD=replace_with_database_password;'
)
"""