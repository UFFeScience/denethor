########################################################################
# FOR LOCAL TESTING!!!!
# Comment the following lines to run the workflow as usual
########################################################################

# from datetime import datetime, timezone

# # Define the start and end time parameters for log retrieval in aws cloudwatch

# BRAZIL_TZ = "-03:00"
# UTC_TZ = "-00:00"
# start_time_human = "2024-10-25T16:07:57" + UTC_TZ #005 nova config
# end_time_human   = "2024-10-25T16:08:35" + UTC_TZ

# # Convert the human-readable time to milliseconds
# start_time_ms = du.convert_str_to_ms(start_time_human)
# end_time_ms = du.convert_str_to_ms(end_time_human)

# # Adds a margin of 10 seconds before and after the interval to ensure that all logs are captured
# start_time_ms -= 10000
# end_time_ms += 10000

# # execution_tag = du.generate_workflow_execution_tag(start_time_ms)
# # execution_env = du.get_env_config_by_name("local", env_configs)
# # import denethor.utils.log_handler as dlh
# # logger = dlh.get_logger(execution_tag, execution_env)
# # du.log_env_info(execution_env, logger)

# # Setting the active steps for testing
# # ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
# activities = ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
# # activities = ["maf_database_aggregator"]

# for step in workflow_steps:
#     if step['action'] == action and step['activity'] in activities:
#         step['active'] = True
#     else:
#         step['active'] = False

########################################################################