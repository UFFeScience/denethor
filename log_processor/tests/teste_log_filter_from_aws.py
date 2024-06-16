import json
import boto3
from datetime import datetime, timedelta
import time


# Save logs to a single file ordered by logStreamName
def save_to_file(json_logs, file):
    # json_logs.sort(key=lambda x: (x['logStreamName'], x['timestamp']))
    with open(file=file, mode='w') as file:
        json.dump(json_logs, file, indent=2)
    
    print(f"Logs saved to {file} in json format")


client = boto3.client('logs')

request_ids = ['2c1abb96-1ce9-43e2-ba1d-ce0ef717818f', '9d4ff5e3-30e1-4d45-83d9-b273fb2dfcdd']
query = f"fields @timestamp, @requestId, @message, @logStream | filter @requestId in {request_ids}"
query2 = 'filter @requestId in ["{}"]'.format('", "'.join(request_ids))

log_group_name = '/aws/lambda/tree_constructor'
start_time=1707761189969
end_time=1707761197835

start_query_response = client.start_query(
  logGroupName=log_group_name,
  startTime=start_time,
  endTime=end_time,
  queryString=query2,
)

query_id = start_query_response['queryId']

response = None

while response == None or response['status'] == 'Running':
  print('Aguardando a consulta ser concluída ...')
  time.sleep(1)
  response = client.get_query_results(
    queryId=query_id
  )

results = response['results']

print(results)

save_to_file(results, 'executions/logs/teste.json')






# filter = '{$.requestId = ' + reqs[0] + ' || $.requestId = ' + reqs[1] + '}'
# filter = '{$.requestId=2c1abb96-1ce9-43e2-ba1d-ce0ef717818f}'

# response = client.filter_log_events(
#     logGroupName=log_group,
#     startTime=start_timestamp_ms,
#     endTime=end_timestamp_ms,
#     filterPattern=filter
# )

# logs = response['events']

# if logs == None:
#     raise ValueError("No log records were found!")

# print(logs)