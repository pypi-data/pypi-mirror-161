from datetime import datetime
import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDirectory)
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from rules import check_column_not_null
from rules import check_datatype_of_all_columns
from rules import check_datatype_of_column
from rules import check_datatype_precision_of_column
from rules import check_key_column_uniqueness
from rules import check_sum_of_column
from rules import row_count_in_footer
from rules import column_count
from rules import file_size_variance
from rules import row_count_variance
from rules import row_count

def execute(schema, run_details, rule_mapping):
    result = 'SUCCESS'
    resultConsolidated = 'SUCCESS'

    executionDate = datetime.now().strftime("%Y-%m-%d")
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")

    master_ingestion_data_quality_rules = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_data_quality_rules_from_s3_with_condition(
        "id", rule_mapping.rule_id
    )

    for rule in master_ingestion_data_quality_rules.itertuples():
        if rule.to_apply_on == 'FILE':
            if "ROW_COUNT_VARIANCE_GREATER_THAN" in rule.code:
                result = row_count_variance.execute(rule_mapping, rule)
            elif "FILE_SIZE_VARIANCE_GREATER_THAN" in rule.code:
                result = file_size_variance.execute(rule_mapping, rule)
            elif "ROW_COUNT" in rule.code:
                result = row_count.execute(rule_mapping, rule)
            elif "ROW_COUNT_IN_FOOTER" in rule.code:
                result = row_count_in_footer.execute(schema, run_details, rule_mapping, rule)
            elif "COLUMN_COUNT" in rule.code:
                result = column_count.execute(rule_mapping, rule)
            elif "DATATYPE_ALL_COLUMNS" in rule.code:
                result = check_datatype_of_all_columns.execute(run_details, rule_mapping, rule)
            elif "KEY_CHECK" in rule.code:
                result = check_key_column_uniqueness.execute(rule_mapping, rule)
        elif rule.to_apply_on == 'COLUMN':
            if "DATATYPE" == rule.code:
                result = check_datatype_of_column.execute(schema, run_details, rule_mapping, rule)
            elif "NOTNULL" == rule.code:
                result = check_column_not_null.execute(schema, run_details, rule_mapping, rule)
            elif "DATATYPE_PRECISION" == rule.code:
                result = check_datatype_precision_of_column.execute(schema, run_details, rule_mapping, rule)
            elif "CHECK_SUM" == rule.code or "CHECKSUM" == rule.code:
                result = check_sum_of_column.execute(schema, run_details, rule_mapping, rule)
        if resultConsolidated == 'SUCCESS':
            resultConsolidated = result
    return resultConsolidated

def execute_rule(schema, run_details, rule_mapping, rule):
    result = 'SUCCESS'
    resultConsolidated = 'SUCCESS'

    executionDate = datetime.now().strftime("%Y-%m-%d")
    executionDateWithTimeWithDashes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    executionDateWithTime = executionDateWithTimeWithDashes.replace("-", "").replace(":", "").replace(" ", "")

    master_ingestion_data_quality_rules = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_data_quality_rules_from_s3_with_condition(
        "id", rule_mapping.rule_id
    )

    for rule in master_ingestion_data_quality_rules.itertuples():
        if rule.to_apply_on == 'FILE':
            if "ROW_COUNT_VARIANCE_GREATER_THAN" in rule.code:
                result = row_count_variance.execute(schema, run_details, rule_mapping, rule)
            elif "FILE_SIZE_VARIANCE_GREATER_THAN" in rule.code:
                result = file_size_variance.execute(schema, run_details, rule_mapping, rule)
            elif "ROW_COUNT" in rule.code:
                result = row_count.execute(schema, run_details, rule_mapping, rule)
            elif "ROW_COUNT_IN_FOOTER" in rule.code:
                result = row_count_in_footer.execute(schema, run_details, rule_mapping, rule)
            elif "COLUMN_COUNT" in rule.code:
                result = column_count.execute(schema, run_details, rule_mapping, rule)
            elif "DATATYPE_ALL_COLUMNS" in rule.code:
                result = check_datatype_of_all_columns.execute(schema, run_details, rule_mapping, rule)
            elif "KEY_CHECK" in rule.code:
                result = check_key_column_uniqueness.execute(schema, run_details, rule_mapping, rule)
        elif rule.to_apply_on == 'COLUMN':
            if "DATATYPE" == rule.code:
                result = check_datatype_of_column.execute(schema, run_details, rule_mapping, rule)
            elif "NOTNULL" == rule.code:
                result = check_column_not_null.execute(schema, run_details, rule_mapping, rule)
            elif "DATATYPE_PRECISION" == rule.code:
                result = check_datatype_precision_of_column.execute(schema, run_details, rule_mapping, rule)
            elif "CHECK_SUM" == rule.code or "CHECKSUM" == rule.code:
                result = check_sum_of_column.execute(schema, run_details, rule_mapping, rule)
        if resultConsolidated == 'SUCCESS':
            resultConsolidated = result
    return resultConsolidated