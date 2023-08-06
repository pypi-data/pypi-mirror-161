import pandas
from pandas.api.types import is_datetime64_any_dtype
import numpy

def check_if_data_type_of_columns_in_source_file_is_correct(source_data_frame, source_file_column_to_table_column_mapping_data_frame):
    source_file_column_to_table_column_mapping_data_frame.sort_values('source_file_column_order')

    for row in source_file_column_to_table_column_mapping_data_frame.itertuples():
        if(row.table_column_type).lower() in ['smallint', 'int2', 'integer', 'int', 'int4', 'bigint', 'int8']:
            if source_data_frame.iloc[:, int(row.source_file_column_order)-1].isnull().sum() != len(source_data_frame) and len(source_data_frame[source_data_frame.iloc[:, int(row.source_file_column_order)-1] == '']) != len(source_data_frame) and source_data_frame.dtypes.iloc[int(row.source_file_column_order)-1] not in [numpy.int8, numpy.int32, numpy.int64]:
                print('NOT ok for column: ', row.table_column_name)
        elif (row.table_column_type).lower() in ['decimal', 'numeric', 'real', 'float4', 'double precision', 'float8', 'float']:
            if source_data_frame.dtypes.iloc[int(row.source_file_column_order)-1] not in [numpy.float16, numpy.float32, numpy.float64, numpy.float128]:
                print('NOT ok for column:: ', row.table_column_name)
        elif (row.table_column_type).lower() in ['date', 'timestamp']:
            if not is_datetime64_any_dtype(source_data_frame.dtypes.iloc[int(row.source_file_column_order)-1]):
                source_data_frame.iloc[:, int(row.source_file_column_order)-1] = pandas.to_datetime(source_data_frame.iloc[:, int(row.source_file_column_order)-1], format='%Y%m%d')
                print('NOT ok for column::: ', row.table_column_name)
        elif(row.table_column_type).lower() in ['boolean', 'bool']:
            if source_data_frame.dtypes.iloc[int(row.source_file_column_order)-1] != numpy.bool:
                print('NOT ok for column:::: ', row.table_column_name)
    return source_data_frame