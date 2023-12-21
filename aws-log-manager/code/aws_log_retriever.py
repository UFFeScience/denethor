from aws_log_utils import *



# Define your start and end dates along with the Lambda function name
# start_date = "2023-11-27T14:25:00Z"
# end_date = "2023-12-31T23:59:59Z"
start_date = "2023-12-04T15:40:00Z"
end_date = "2023-12-31T23:59:59Z"
function_name = "tree_constructor"


# Retrieve logs from AWS Lambda organized by logStreamName
logs_by_stream = retrieve_lambda_logs(start_date, end_date, function_name)





# 
# Display the  logs
# print_logs(filtered_logs)
# print_logs(logs)
# save_logs_to_file_custom(logs, "logs_output.txt")
# save_logs_to_file_json(logs, "logs_output_json.txt")
# save_logs_to_file_custom(filtered_logs, "filtered_logs_output.txt")

file_prefix = "logs_"+ function_name
save_logs_to_single_file(logs_by_stream, file_prefix)
save_logs_to_multiple_files(logs_by_stream, file_prefix)

