import re
import boto3
import fnmatch
def test_list_files():

    DATA_FORMAT = 'nexus' # newick ou nexus

    input_bucket = 'mribeiro-tree-files'
    input_files = ["ORTHOMCL1","ORTHOMCL256","ORTHOMCL320","ORTHOMCL337"]

    # Connect to the S3 service
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=input_bucket, Prefix='', StartAfter='', Delimiter='/')
    response_files = response['Contents']
    
    all_matching_files = []  # para armazenar todos os objetos correspondentes

    
    for base_file_name in input_files:
        pattern = r'.*{}(_Inner\d+|)\.{}$'.format(base_file_name, DATA_FORMAT)
        matching_files = [item['Key'] for item in response_files if re.match(pattern, item['Key'])]
        all_matching_files.extend(matching_files)
        print(f'pattern: {pattern} | matching_files: {matching_files}')
    
    
    # for s3_file in response['Contents']:
    for s3_file_key in all_matching_files:
        # key representa o path + nome do arquivo do s3
        print(f'downloading file from s3: {s3_file_key}')

    # Verify if the returned list is equal to the expected list
    expected_files = ['tree_ORTHOMCL1.nexus', 'tree_ORTHOMCL256.nexus', 'tree_ORTHOMCL320.nexus', 'tree_ORTHOMCL337.nexus']
    assert all_matching_files == expected_files, "The list of files is not equal to the expected list"

test_list_files()