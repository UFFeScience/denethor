import unittest
import re
from utils.log_parser import parse_log



class TestLogParser(unittest.TestCase):

    def test_parse_log_start(self):
        log_string = 'START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n'
        expected_output = {
            'LogType': 'START',
            'RequestId': '4f7f240b-e714-464c-b043-c31deef80e6c',
            'Version': '$LATEST'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)
    
    def test_parse_log_end(self):
        log_string = 'END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n'
        expected_output = {
            'LogType': 'END',
            'RequestId': '4f7f240b-e714-464c-b043-c31deef80e6c'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)

    def test_parse_log_report(self):
        log_string = 'REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n'
        expected_output = {
            'LogType': 'REPORT',
            'RequestId': '4f7f240b-e714-464c-b043-c31deef80e6c',
            'Duration': '1010.14 ms',
            'Billed Duration': '1011 ms',
            'Memory Size': '128 MB',
            'Max Memory Used': '115 MB',
            'Init Duration': '918.52 ms'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)

    def test_parse_log_report_sem_init_duration(self):
        log_string = 'REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\t\n'
        expected_output = {
            'LogType': 'REPORT',
            'RequestId': '4f7f240b-e714-464c-b043-c31deef80e6c',
            'Duration': '1010.14 ms',
            'Billed Duration': '1011 ms',
            'Memory Size': '128 MB',
            'Max Memory Used': '115 MB',
            'Init Duration': None
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)

    def test_parse_log_file_download(self):
        log_string = 'FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n'
        expected_output = {
            'LogType': 'FILE_DOWNLOAD',
            'RequestId': 'c3df54b6-1da5-48b2-bec4-093b55c96692',
            'FileName': 'ORTHOMCL1',
            'Bucket': 'mribeiro-bucket-input',
            'FilePath': 'data/testset/ORTHOMCL1',
            'Duration': '407.83485699999744 ms',
            'FileSize': '1640 bytes'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)

    def test_parse_log_file_upload(self):
        log_string = 'FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965 ms\t FileSize: 339 bytes\n'
        expected_output = {
            'LogType': 'FILE_UPLOAD',
            'RequestId': '4f7f240b-e714-464c-b043-c31deef80e6c',
            'FileName': 'tree_ORTHOMCL1.nexus',
            'Bucket': 'mribeiro-bucket-output-tree',
            'FilePath': 'tree_ORTHOMCL1.nexus',
            'Duration': '292.6312569999965 ms',
            'FileSize': '339 bytes'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)

    def test_parse_log_consumed_files_info(self):
        log_string = 'CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFilesSize: 36777 bytes\t Duration: 6933.13087699994 ms\n'
        expected_output = {
            'LogType': 'CONSUMED_FILES_INFO',
            'RequestId': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
            'NumFiles': '100 files',
            'TotalFilesSize': '36777 bytes',
            'Duration': '6933.13087699994 ms'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_produced_files_info(self):
        log_string = 'PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n'
        expected_output = {
            'LogType': 'PRODUCED_FILES_INFO',
            'RequestId': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
            'NumFiles': '335 files',
            'TotalFilesSize': '83697 bytes',
            'Duration': '17168.395734999875 ms'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_subtree_files_create(self):
        log_string = 'SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n'
        expected_output = {
            'LogType': 'SUBTREE_FILES_CREATE',
            'RequestId': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
            'Duration': '795.8109850000028 ms'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_maf_database_create(self):
        log_string = 'MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {"1": {}, "2": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner2.nexus", "tree_ORTHOMCL1977_Inner1.nexus"]}, "3": {}, "5": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner3.nexus"], "tree_ORTHOMCL1977_Inner3.nexus": ["tree_ORTHOMCL1_Inner3.nexus"]}}\n'
        expected_output = {
            'LogType': 'MAF_DATABASE_CREATE',
            'RequestId': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
            'MaxMaf': '5',
            'Duration': '485681.23013399995 ms',
            'MafDatabase': '{"1": {}, "2": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner2.nexus", "tree_ORTHOMCL1977_Inner1.nexus"]}, "3": {}, "5": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner3.nexus"], "tree_ORTHOMCL1977_Inner3.nexus": ["tree_ORTHOMCL1_Inner3.nexus"]}}'
        }
        output = parse_log(log_string)
        self.assertEqual(output, expected_output)
        
if __name__ == '__main__':
    unittest.main()