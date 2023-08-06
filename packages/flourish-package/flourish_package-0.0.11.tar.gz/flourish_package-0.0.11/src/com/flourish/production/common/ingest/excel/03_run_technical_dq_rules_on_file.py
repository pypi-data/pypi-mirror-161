import os, sys
currentDirectory = os.path.dirname(os.path.realpath(__file__))
directoryOneLevelAbove = os.path.dirname(currentDirectory)
sys.path.append(directoryOneLevelAbove)
directoryTwoLevelsAbove = os.path.dirname(directoryOneLevelAbove)
sys.path.append(directoryTwoLevelsAbove)
directoryThreeLevelsAbove = os.path.dirname(directoryTwoLevelsAbove)
sys.path.append(directoryThreeLevelsAbove)
from helper import get_master_data_file_from_s3_as_data_frame
from helper import db_operations
from rules import rule_executer

def execute(source, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source(
        source
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_status_using_file_details_id(schema, row.id, 'RTDCS')

        if(len(runDetails) > 0):
            runDetail = runDetails.iloc[0]

            get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition(
                "file_details_id", row.id
            )

            #A consolidated status of all the rules that are checked in the below FOR loop to update the run details with the right status i.e. if all rules passed TDQFS, all mandatory rules passed TDQFPS or at least one mandatory rule failed TDQFF.
            consolidatedStatusCode = 'TDQFS'
            consolidatedStatusDescription = 'All rules for the file passed'

            for rule_mapping in get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition.itertuples():
                master_ingestion_data_quality_rules = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_data_quality_rules_from_s3_with_condition(
                    "id", rule_mapping.rule_id
                )

                for rule in master_ingestion_data_quality_rules.itertuples():
                    #Status of execution of a specific rule and updating the consolidated status correctly. Also, need to take into account if the rule was mandatory or not.
                    resultOfRule = rule_executer.execute_rule(schema, runDetail, rule_mapping, rule)
                    if(resultOfRule != 'SUCCESS'):
                        if(rule.is_mandatory == 'Y'):
                            consolidatedStatusCode = 'TDQFF'
                            consolidatedStatusDescription = 'At least one mandatory rule for the file failed'
                        else:
                            if(consolidatedStatusCode != 'TDQFF'):
                                consolidatedStatusCode = 'TDQFPS'
                                consolidatedStatusDescription = 'One or more non-mandatory rules for the file failed but all mandatory rules for the file passed'

            #Update the status of the run in the run details table using the consolidated status
            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = consolidatedStatusCode
            updateRunDetails["status_description"] = consolidatedStatusDescription
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )

def execute_for_file_with_one_sheet(source, schema, tableName):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "table_name",
        tableName
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_status_using_file_details_id(schema, row.id, 'RTDCS')

        if(len(runDetails) > 0):
            runDetail = runDetails.iloc[0]

            get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition(
                "file_details_id", row.id
            )

            #A consolidated status of all the rules that are checked in the below FOR loop to update the run details with the right status i.e. if all rules passed TDQFS, all mandatory rules passed TDQFPS or at least one mandatory rule failed TDQFF.
            consolidatedStatusCode = 'TDQFS'
            consolidatedStatusDescription = 'All rules for the file passed'

            for rule_mapping in get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition.itertuples():
                master_ingestion_data_quality_rules = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_data_quality_rules_from_s3_with_condition(
                    "id", rule_mapping.rule_id
                )

                for rule in master_ingestion_data_quality_rules.itertuples():
                    #Status of execution of a specific rule and updating the consolidated status correctly. Also, need to take into account if the rule was mandatory or not.
                    resultOfRule = rule_executer.execute_rule(schema, runDetail, rule_mapping, rule)
                    if(resultOfRule != 'SUCCESS'):
                        if(rule.is_mandatory == 'Y'):
                            consolidatedStatusCode = 'TDQFF'
                            consolidatedStatusDescription = 'At least one mandatory rule for the file failed'
                        else:
                            if(consolidatedStatusCode != 'TDQFF'):
                                consolidatedStatusCode = 'TDQFPS'
                                consolidatedStatusDescription = 'One or more non-mandatory rules for the file failed but all mandatory rules for the file passed'

            #Update the status of the run in the run details table using the consolidated status
            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = consolidatedStatusCode
            updateRunDetails["status_description"] = consolidatedStatusDescription
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )

def execute_for_file_name_pattern(source, fileNamePattern, schema):
    master_ingestion_raw_source_file_details = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_details_from_s3_for_source_with_condition(
        source,
        "name_pattern",
        fileNamePattern
    )
    for row in master_ingestion_raw_source_file_details.itertuples():
        runDetails = db_operations.get_run_details_with_given_status_using_file_details_id(schema, row.id, 'RTDCS')

        if(len(runDetails) > 0):
            runDetail = runDetails.iloc[0]

            get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition(
                "file_details_id", row.id
            )

            #A consolidated status of all the rules that are checked in the below FOR loop to update the run details with the right status i.e. if all rules passed TDQFS, all mandatory rules passed TDQFPS or at least one mandatory rule failed TDQFF.
            consolidatedStatusCode = 'TDQFS'
            consolidatedStatusDescription = 'All rules for the file passed'

            for rule_mapping in get_master_ingestion_raw_source_file_data_quality_rules_mapping_from_s3_with_condition.itertuples():
                master_ingestion_data_quality_rules = get_master_data_file_from_s3_as_data_frame.get_master_ingestion_data_quality_rules_from_s3_with_condition(
                    "id", rule_mapping.rule_id
                )

                for rule in master_ingestion_data_quality_rules.itertuples():
                    #Status of execution of a specific rule and updating the consolidated status correctly. Also, need to take into account if the rule was mandatory or not.
                    resultOfRule = rule_executer.execute_rule(schema, runDetail, rule_mapping, rule)
                    if(resultOfRule != 'SUCCESS'):
                        if(rule.is_mandatory == 'Y'):
                            consolidatedStatusCode = 'TDQFF'
                            consolidatedStatusDescription = 'At least one mandatory rule for the file failed'
                        else:
                            if(consolidatedStatusCode != 'TDQFF'):
                                consolidatedStatusCode = 'TDQFPS'
                                consolidatedStatusDescription = 'One or more non-mandatory rules for the file failed but all mandatory rules for the file passed'

            #Update the status of the run in the run details table using the consolidated status
            updateRunDetails = {}
            updateRunDetails["id"] = runDetail.id
            updateRunDetails["status_code"] = consolidatedStatusCode
            updateRunDetails["status_description"] = consolidatedStatusDescription
            db_operations.update_run_details(
                schema,
                updateRunDetails
            )
