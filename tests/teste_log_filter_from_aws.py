import json, sys, os, time
import boto3
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from denethor.provenance import log_retriever_manager as alr


# Save logs to a single file ordered by logStreamName
def save_to_file(json_logs, file):
    # json_logs.sort(key=lambda x: (x['logStreamName'], x['timestamp']))
    with open(file=file, mode='w') as file:
        json.dump(json_logs, file, indent=2)
    
    print(f"Logs saved to {file} in json format")


client = boto3.client('logs')

request_ids = ['f3cf4bec-e84f-495e-bac9-c5b69defe4c8', '26b852e3-1a65-4c50-8816-e0c6fcf2ec75']
query = f"fields @timestamp, @requestId, @message, @logStream | filter @requestId in {request_ids}"
query2 = 'filter @requestId in ["{}"]'.format('", "'.join(request_ids))

log_group_name = '/aws/lambda/tree_constructor_256'
start_time=1741205743183
end_time=1741205745993

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

save_to_file(results, f".tmp/logs/teste_1_{start_time}.json")



logs = alr.get_all_log_events(log_group_name, start_time, end_time)

print(logs)

save_to_file(logs, f".tmp/logs/teste_2_{start_time}.json")





