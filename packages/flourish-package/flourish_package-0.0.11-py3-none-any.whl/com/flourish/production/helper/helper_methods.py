import pandas
import s3fs
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_string_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype
import numpy
import boto3

def edit_column_names_of_dataframe_by_removing_special_characters(data_frame):
    data_frame.columns = data_frame.columns.str.slice(start=0, stop=120)
    data_frame.columns = data_frame.columns.str.replace(' ', '_')
    data_frame.columns = data_frame.columns.str.replace('/', '_or_')
    data_frame.columns = data_frame.columns.str.replace('&', 'and')
    data_frame.columns = data_frame.columns.str.replace('=', '_eq_')
    data_frame.columns = data_frame.columns.str.replace('-', '_')
    data_frame.columns = data_frame.columns.str.replace('.', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace('%', 'percentage', regex=False)
    data_frame.columns = data_frame.columns.str.replace('(', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace(')', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace(',', '_')
    data_frame.columns = data_frame.columns.str.replace('?', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace('\'', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace(':', '_', regex=False)
    data_frame.columns = data_frame.columns.str.replace('\\n', '_', regex=True)
    data_frame.columns = data_frame.columns.str.replace('\\t', '_', regex=True)
    data_frame.columns = data_frame.columns.str.lower()
    return data_frame

def edit_column_names_by_removing_special_characters(data_frame_columns):
    data_frame_columns = data_frame_columns.str.slice(start=0, stop=120)
    data_frame_columns = data_frame_columns.str.replace(' ', '_')
    data_frame_columns = data_frame_columns.str.replace('/', '_or_')
    data_frame_columns = data_frame_columns.str.replace('&', 'and')
    data_frame_columns = data_frame_columns.str.replace('=', '_eq_')
    data_frame_columns = data_frame_columns.str.replace('-', '_')
    data_frame_columns = data_frame_columns.str.replace('.', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace('%', 'percentage', regex=False)
    data_frame_columns = data_frame_columns.str.replace('(', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace(')', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace(',', '_')
    data_frame_columns = data_frame_columns.str.replace('?', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace('\'', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace(':', '_', regex=False)
    data_frame_columns = data_frame_columns.str.replace('\\n', '_', regex=True)
    data_frame_columns = data_frame_columns.str.replace('\\t', '_', regex=True)
    data_frame_columns = data_frame_columns.str.lower()
    return data_frame_columns

def edit_table_name_by_removing_special_characters(table_name):
    table_name = table_name.replace(' ', '_')
    table_name = table_name.replace('/', '_or_')
    table_name = table_name.replace('&', 'and')
    table_name = table_name.replace('=', '_eq_')
    table_name = table_name.replace('-', '_')
    table_name = table_name.replace('.', '_', regex=False)
    table_name = table_name.replace('%', 'percentage', regex=False)
    table_name = table_name.replace('(', '_', regex=False)
    table_name = table_name.replace(')', '_', regex=False)
    table_name = table_name.replace(',', '_')
    table_name = table_name.replace('?', '_', regex=False)
    table_name = table_name.replace('\'', '_', regex=False)
    table_name = table_name.replace(':', '_', regex=False)
    table_name = table_name.replace('\\n', '_', regex=True)
    table_name = table_name.replace('\\t', '_', regex=True)
    table_name = table_name.lower()
    return table_name

def format_date_column_in_dataframe_to_yyyymmddhh24miss(data_frame):
    for column in data_frame.columns:
        if is_datetime64_any_dtype(data_frame[column]):
            data_frame.style.format({column: lambda t: t.strftime("%Y-%m-%d %H:%M:%S")})
    return data_frame

def strip_leading_and_trailing_spaces_from_all_columns_of_a_data_frame(data_frame):
    for column in data_frame.columns:
        if is_string_dtype(data_frame[column]):
            data_frame[column] = data_frame[column].str.strip()
    return data_frame

def convert_float_column_with_integers_and_nans_to_integer_column(data_frame):
    for column in data_frame.columns:
        if is_float_dtype(data_frame[column]):
            temp_df = data_frame[column].fillna(0)
            if(numpy.array_equal(temp_df, temp_df.astype(int))):
                data_frame[column] = data_frame[column].fillna(0)
                data_frame[column] = data_frame[column].astype('Int64')
    return data_frame

def remove_database_audit_columns_from_dataframe(data_from_database, extra_columns_to_remove=None):
    data_from_database.columns = data_from_database.columns.str.lower()
    if 'row_start_date' in data_from_database.columns:
        data_from_database.drop('row_start_date', inplace=True, axis=1)
    if 'row_end_date' in data_from_database.columns:
        data_from_database.drop('row_end_date', inplace=True, axis=1)
    if 'row_status_code' in data_from_database.columns:
        data_from_database.drop('row_status_code', inplace=True, axis=1)
    if 'load_timestamp' in data_from_database.columns:
        data_from_database.drop('load_timestamp', inplace=True, axis=1)
    if extra_columns_to_remove is not None:
        for column_to_remove in extra_columns_to_remove:
            if column_to_remove in data_from_database.columns:
                data_from_database.drop(column_to_remove, inplace=True, axis=1)

    return data_from_database

def convert_excel_file_with_multiple_sheets_to_multiple_csv_files_and_store_in_s3(source_bucket, location_inside_source_bucket, source_file_name, destination_bucket, location_inside_destination_bucket):
    excel = pandas.ExcelFile('s3://'+source_bucket+'/'+location_inside_source_bucket+'/'+source_file_name)
    excel_sheet_names = excel.sheet_names

    if len(excel_sheet_names) == 1:
        data_from_excel = pandas.read_excel('s3://'+source_bucket+'/'+location_inside_source_bucket+'/'+source_file_name)
        data_from_excel = edit_column_names_of_dataframe_by_removing_special_characters(data_from_excel)
        data_from_excel = format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_excel)
        data_from_excel = data_from_excel.replace(numpy.nan, '', regex=True)
        print('********** data_from_excel: ', len(data_from_excel))
        s3 = s3fs.S3FileSystem(anon=False)
        dataFileName = destination_bucket+'/'+location_inside_destination_bucket+'/'+source_file_name[:source_file_name.rfind(".")]+'.csv'
        with s3.open(dataFileName, 'w') as f:
            data_from_excel.to_csv(f, index=False, line_terminator='\n')
    else:
        for sheet_name in sheet_names:
            data_from_excel = pandas.read_excel('s3://'+source_bucket+'/'+location_inside_source_bucket+'/'+source_file_name, sheet_name=sheet_name)
            data_from_excel = edit_column_names_of_dataframe_by_removing_special_characters(data_from_excel)
            data_from_excel = format_date_column_in_dataframe_to_yyyymmddhh24miss(data_from_excel)
            data_from_excel = data_from_excel.replace(numpy.nan, '', regex=True)
            print('********** data_from_excel: ', len(data_from_excel))
            s3 = s3fs.S3FileSystem(anon=False)
            dataFileName = destination_bucket+'/'+location_inside_destination_bucket+'/'+source_file_name[:source_file_name.rfind(".")]+'_'+sheet_name.lower()+'.csv'
            with s3.open(dataFileName, 'w') as f:
                data_from_excel.to_csv(f, index=False, line_terminator='\n')

def get_regular_expression_from_expression_type(expression_type, delimiter):
    if expression_type == 'ALPHANUMERIC':
        return '[^\W_]+'
    elif expression_type == 'NUMERIC':
        return '\d+'
    elif expression_type == 'ALPHABET':
        return '[a-zA-Z]'
    else:
        return '[^'+delimiter+']+'

def getNumberOfRowsInExcelFile(fileLocationInS3, fileName, sheetName, headerStartRow, columnSpan):
    data_from_excel = pandas.read_excel(fileLocationInS3+'/'+fileName, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, usecols=getColumnSpan(columnSpan))
    print('********** Number of rows in excel: ', len(data_from_excel))
    return len(data_from_excel)

def getNumberOfRowsInCSVFile(fileLocationInS3, fileName, fileEncoding):
    data_from_file = create_data_frame_from_csv(fileLocationInS3+'/'+fileName, '', fileEncoding, 0)
    if len(data_from_file.columns) > 0:
        print('********** Number of rows in csv: ', len(data_from_file))
        return len(data_from_file)
    else:
        print("____________________ data_from_file is null")
        return 0

def getNumberOfRowsInCSVFileWithGivenDelimiter(fileLocationInS3, fileName, fileDelimiter, fileEncoding):
    data_from_file = create_data_frame_from_csv(fileLocationInS3+'/'+fileName, fileDelimiter, fileEncoding, 0)
    if len(data_from_file.columns) > 0:
        print('********** Number of rows in csv: ', len(data_from_file))
        return len(data_from_file)
    else:
        print("____________________ data_from_file is null")
        return 0

def removeBucketNameFromFileLocation(fileLocationInS3):
    parts = fileLocationInS3.split("/", 3)
    if len(parts) <= 3:
        return -1
    return fileLocationInS3[len(fileLocationInS3)-len(parts[-1])-len("/")+1:]

def getBucketNameFromFileLocation(fileLocationInS3):
    parts = fileLocationInS3.split("/", 3)
    if len(parts) <= 3:
        return -1
    return fileLocationInS3[:len(fileLocationInS3)-len(parts[-1])-len("/")].replace("s3://", "")

def getExcelFileSize(fileLocationInS3, fileName):
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=getBucketNameFromFileLocation(fileLocationInS3), Key=removeBucketNameFromFileLocation(fileLocationInS3)+"/"+fileName)
    return response['ContentLength']

def getFileSize(fileLocationInS3, fileName):
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=getBucketNameFromFileLocation(fileLocationInS3), Key=removeBucketNameFromFileLocation(fileLocationInS3)+"/"+fileName)
    return response['ContentLength']

def getColumnSpan(columnSpan):
    if(columnSpan == 'None'):
        return None
    else:
        return columnSpan

def drop_columns_ending_with_suffix(data_frame_columns, suffix):
    columns = list(data_frame_columns)
    columns_to_delete = []
    for column in columns:
        if column.endswith(suffix):
            columns_to_delete.append(column)
    return columns_to_delete

def change_column_names_by_removing_suffix(data_frame_columns, suffix):
    columns = list(data_frame_columns)
    columns_to_rename = {}
    for column in columns:
        if column.endswith(suffix):
            columns_to_rename[column] = column[:-len(suffix)]
    return columns_to_rename

def create_data_frame_from_csv(fileLocation, fileDelimiter, fileEncoding, numberOfFooterRows):
    try:
        return pandas.read_csv(fileLocation, sep=(',' if (pandas.isna(fileDelimiter) or not fileDelimiter) else fileDelimiter), skipfooter=numberOfFooterRows, engine='python', encoding=('utf-8' if (pandas.isna(fileEncoding) or not fileEncoding) else fileEncoding))
    except Exception as e:
        print('Exception in method: create_data_frame_from_csv____________________________________________________________________')
        print(e)
        return pandas.DataFrame()

def create_data_frame_from_excel(fileLocation, sheetName, columnSpan, headerStartRow, dataStartRowIndex, numberOfFooterRows):
    try:
        if(headerStartRow == None):
            return pandas.read_excel(fileLocation, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, usecols=getColumnSpan(columnSpan), skipfooter=numberOfFooterRows)
        else:
            return pandas.read_excel(fileLocation, sheet_name=(0 if (pandas.isna(sheetName) or not sheetName) else sheetName), header=headerStartRow, usecols=getColumnSpan(columnSpan), skiprows=range(headerStartRow+1,dataStartRowIndex), skipfooter=numberOfFooterRows)
    except Exception as e:
        print('Exception in method: create_data_frame_from_excel____________________________________________________________________')
        print(e)
        return pandas.DataFrame()

def change_datatype_of_columns_based_on_master_configuration(dataframe_to_change_column_type, column_type_master_configurations):
    try:
        column_type_master_configurations = column_type_master_configurations.reset_index()
        for index, row in column_type_master_configurations.iterrows():
            if(not pandas.isna(row["source_aligned_table_column_type"]) and row["source_aligned_table_column_type"] and row["source_aligned_table_column_type"] != row["table_column_type"]):
                if(row["source_aligned_table_column_type"] in ['date']):
                    dataframe_to_change_column_type[row["table_column_name"]] = pandas.to_datetime(dataframe_to_change_column_type[row["table_column_name"]]).dt.date
                elif(row["source_aligned_table_column_type"] in ['datetime', 'timestamp']):
                    dataframe_to_change_column_type[row["table_column_name"]] = pandas.to_datetime(dataframe_to_change_column_type[row["table_column_name"]])
    except Exception as e:
        print('Exception in method: change_datatype_of_columns_based_on_master_configuration____________________________________________________________________')
        print(e)
    return dataframe_to_change_column_type

def change_datatype_of_columns_based_on_source_file_to_column_mapping_table(dataframe_to_change_column_type, column_type_master_configurations):
    try:
        column_type_master_configurations = column_type_master_configurations.reset_index()
        for index, row in column_type_master_configurations.iterrows():
            if(row['table_column_type'] in ['date']):
                if is_datetime64_any_dtype(dataframe_to_change_column_type[row['table_column_name']]):
                    print(row['table_column_name']+' is of type date')
                if is_string_dtype(dataframe_to_change_column_type[row['table_column_name']]):
                    print(row['table_column_name']+' is of type string')
                try:
                    dataframe_to_change_column_type[row['table_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['table_column_name']], dayfirst=True, format='%d/%m/%Y').dt.date
                except Exception as e:
                    print(row['table_column_name'] + ' is not in DD/MM/YYYY format')
                    try:
                        dataframe_to_change_column_type[row['table_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['table_column_name']]).dt.date
                    except Exception as e:
                        print(row['table_column_name'] + ' is not in any date format')
            elif(row['table_column_type'] in ['datetime', 'timestamp']):
                dataframe_to_change_column_type[row['table_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['table_column_name']])
    except Exception as e:
        print('Exception in method: change_datatype_of_columns_based_on_source_file_to_column_mapping_table____________________________________________________________________')
        print(e)
    return dataframe_to_change_column_type

def change_datatype_of_columns_in_source_file_based_on_source_file_to_column_mapping_table(dataframe_to_change_column_type, column_type_master_configurations):
    try:
        column_type_master_configurations = column_type_master_configurations.reset_index()
        for index, row in column_type_master_configurations.iterrows():
            if(row['table_column_type'].lower() in (column_type.lower() for column_type in ['date'])):
                if is_datetime64_any_dtype(dataframe_to_change_column_type[row['source_file_column_name']]):
                    print(row['source_file_column_name']+' is of type date')
                elif is_string_dtype(dataframe_to_change_column_type[row['source_file_column_name']]):
                    print(row['source_file_column_name']+' is of type string')
                    print(len(dataframe_to_change_column_type[row['source_file_column_name']]))
                    try:
                        dataframe_to_change_column_type[row['source_file_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['source_file_column_name']], dayfirst=True, format='%d/%m/%Y').dt.date
                    except Exception as e:
                        print(row['source_file_column_name'] + ' is not in DD/MM/YYYY format')
                        try:
                            dataframe_to_change_column_type[row['source_file_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['source_file_column_name']]).dt.date
                        except Exception as e:
                            print(row['source_file_column_name'] + ' is not in any date format')
                else:
                    print(row['source_file_column_name' + ' is not date or string so making the whole column null.'])
                    dataframe_to_change_column_type[row['source_file_column_name']] = numpy.NaN
            elif(row['table_column_type'].lower() in (column_type.lower() for column_type in ['datetime', 'timestamp'])):
                if is_datetime64_any_dtype(dataframe_to_change_column_type[row['source_file_column_name']]):
                    print(row['source_file_column_name']+' is of type date')
                elif is_string_dtype(dataframe_to_change_column_type[row['source_file_column_name']]):
                    print(row['source_file_column_name']+' is of type string')
                    print(len(dataframe_to_change_column_type[row['source_file_column_name']]))
                    try:
                        dataframe_to_change_column_type[row['source_file_column_name']] = pandas.to_datetime(dataframe_to_change_column_type[row['source_file_column_name']])
                    except Exception as e:
                        print(row['source_file_column_name'] + ' is not in any date format')
                else:
                    print(row['source_file_column_name' + ' is not date or string so making the whole column null.'])
                    dataframe_to_change_column_type[row['source_file_column_name']] = numpy.NaN
    except Exception as e:
        print('Exception in method: change_datatype_of_columns_in_source_file_based_on_source_file_to_column_mapping_table____________________________________________________________________')
        print(e)
    return dataframe_to_change_column_type