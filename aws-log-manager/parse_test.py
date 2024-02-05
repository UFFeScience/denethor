import unittest
import re
from utils.log_parser import parse_log

class TestLogParser(unittest.TestCase):

    CONFIG = { 
        "basicLogTypes": {
            "START": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": "", "separator": " "},
                {"searchKey": "Version", "fieldName": "version", "dataType": ""}
            ],
            "END": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""}
            ],
            "REPORT": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""},
                {"searchKey": "Billed Duration", "fieldName": "billed_duration", "dataType": ""},
                {"searchKey": "Memory Size", "fieldName": "memory_size", "dataType": ""},
                {"searchKey": "Max Memory Used", "fieldName": "max_memory_used", "dataType": ""},
                {"searchKey": "Init Duration", "fieldName": "init_duration", "dataType": ""}
            ],
            "FILE_DOWNLOAD": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "FileName", "fieldName": "file_name", "dataType": ""},
                {"searchKey": "Bucket", "fieldName": "bucket", "dataType": ""},
                {"searchKey": "FilePath", "fieldName": "file_path", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""},
                {"searchKey": "FileSize", "fieldName": "file_size", "dataType": ""}
            ],
            "FILE_UPLOAD": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "FileName", "fieldName": "file_name", "dataType": ""},
                {"searchKey": "Bucket", "fieldName": "bucket", "dataType": ""},
                {"searchKey": "FilePath", "fieldName": "file_path", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""},
                {"searchKey": "FileSize", "fieldName": "file_size", "dataType": ""}
            ],
            "CONSUMED_FILES_INFO": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "NumFiles", "fieldName": "num_files", "dataType": ""},
                {"searchKey": "TotalFileSize", "fieldName": "total_files_size", "dataType": ""}, #ajustar searchKey
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""}
            ],
            "PRODUCED_FILES_INFO": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "NumFiles", "fieldName": "num_files", "dataType": ""},
                {"searchKey": "TotalFilesSize", "fieldName": "total_files_size", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""}
            ],
            "SUBTREE_FILES_CREATE": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""}
            ],
                "MAF_DATABASE_CREATE": [
                {"searchKey": "RequestId", "fieldName": "request_id", "dataType": ""},
                {"searchKey": "MaxMaf", "fieldName": "max_maf", "dataType": ""},
                {"searchKey": "MafDatabase", "fieldName": "maf_database", "dataType": ""},
                {"searchKey": "Duration", "fieldName": "duration", "dataType": ""}
            ]
        }
    }

    def test_parse_log_start(self):

        log_message = 'START RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c Version: $LATEST\n'
        expected_output = {
            'logType': 'START',
            'attributes': {
                'request_id': '4f7f240b-e714-464c-b043-c31deef80e6c',
                'version': '$LATEST'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)
    
    def test_parse_log_end(self):
        log_message = 'END RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\n'
        expected_output = {
            'logType': 'END',
            'attributes': {
                'request_id': '4f7f240b-e714-464c-b043-c31deef80e6c'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)

    def test_parse_log_report(self):
        log_message = 'REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\tInit Duration: 918.52 ms\t\n'
        expected_output = {
            'logType': 'REPORT',
            'attributes': {
                'request_id': '4f7f240b-e714-464c-b043-c31deef80e6c',
                'duration': '1010.14 ms',
                'billed_duration': '1011 ms',
                'memory_size': '128 MB',
                'max_memory_used': '115 MB',
                'init_duration': '918.52 ms'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)

    def test_parse_log_report_sem_init_duration(self):
        log_message = 'REPORT RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\tDuration: 1010.14 ms\tBilled Duration: 1011 ms\tMemory Size: 128 MB\tMax Memory Used: 115 MB\t\n'
        expected_output = {
            'logType': 'REPORT',
            'attributes': {
                'request_id': '4f7f240b-e714-464c-b043-c31deef80e6c',
                'duration': '1010.14 ms',
                'billed_duration': '1011 ms',
                'memory_size': '128 MB',
                'max_memory_used': '115 MB',
                'init_duration': None
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)

    def test_parse_log_file_download(self):
        log_message = 'FILE_DOWNLOAD RequestId: c3df54b6-1da5-48b2-bec4-093b55c96692\t FileName: ORTHOMCL1\t Bucket: mribeiro-bucket-input\t FilePath: data/testset/ORTHOMCL1\t Duration: 407.83485699999744 ms\t FileSize: 1640 bytes\n'
        expected_output = {
            'logType': 'FILE_DOWNLOAD',
            'attributes': {
                'request_id': 'c3df54b6-1da5-48b2-bec4-093b55c96692',
                'file_name': 'ORTHOMCL1',
                'bucket': 'mribeiro-bucket-input',
                'file_path': 'data/testset/ORTHOMCL1',
                'duration': '407.83485699999744 ms',
                'file_size': '1640 bytes'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)

    def test_parse_log_file_upload(self):
        log_message = 'FILE_UPLOAD RequestId: 4f7f240b-e714-464c-b043-c31deef80e6c\t FileName: tree_ORTHOMCL1.nexus\t Bucket: mribeiro-bucket-output-tree\t FilePath: tree_ORTHOMCL1.nexus\t Duration: 292.6312569999965 ms\t FileSize: 339 bytes\n'
        expected_output = {
            'logType': 'FILE_UPLOAD',
            'attributes': {
                'request_id': '4f7f240b-e714-464c-b043-c31deef80e6c',
                'file_name': 'tree_ORTHOMCL1.nexus',
                'bucket': 'mribeiro-bucket-output-tree',
                'file_path': 'tree_ORTHOMCL1.nexus',
                'duration': '292.6312569999965 ms',
                'file_size': '339 bytes'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)

    def test_parse_log_consumed_files_info(self):
        log_message = 'CONSUMED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 100 files\t TotalFileSize: 36777 bytes\t Duration: 6933.13087699994 ms\n'
        expected_output = {
            'logType': 'CONSUMED_FILES_INFO',
            'attributes': {
                'request_id': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
                'num_files': '100 files',
                'total_files_size': '36777 bytes',
                'duration': '6933.13087699994 ms'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_produced_files_info(self):
        log_message = 'PRODUCED_FILES_INFO RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t NumFiles: 335 files\t TotalFilesSize: 83697 bytes\t Duration: 17168.395734999875 ms\n'
        expected_output = {
            'logType': 'PRODUCED_FILES_INFO',
            'attributes': {
                'request_id': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
                'num_files': '335 files',
                'total_files_size': '83697 bytes',
                'duration': '17168.395734999875 ms'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_subtree_files_create(self):
        log_message = 'SUBTREE_FILES_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t Duration: 795.8109850000028 ms\n'
        expected_output = {
            'logType': 'SUBTREE_FILES_CREATE',
            'attributes': {
                'request_id': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
                'duration': '795.8109850000028 ms'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)
        
    def test_parse_log_maf_database_create(self):
        log_message = 'MAF_DATABASE_CREATE RequestId: 3fcca4a3-e9e6-44aa-883f-647a0386a31a\t MaxMaf: 5\t Duration: 485681.23013399995 ms\t MafDatabase: {"1": {}, "2": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner2.nexus", "tree_ORTHOMCL1977_Inner1.nexus"]}, "3": {}, "5": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner3.nexus"], "tree_ORTHOMCL1977_Inner3.nexus": ["tree_ORTHOMCL1_Inner3.nexus"]}}\n'
        expected_output = {
            'logType': 'MAF_DATABASE_CREATE',
            'attributes': {
                'request_id': '3fcca4a3-e9e6-44aa-883f-647a0386a31a',
                'max_maf': '5',
                'duration': '485681.23013399995 ms',
                'maf_database': '{"1": {}, "2": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner2.nexus", "tree_ORTHOMCL1977_Inner1.nexus"]}, "3": {}, "5": {"tree_ORTHOMCL1_Inner3.nexus": ["tree_ORTHOMCL1977_Inner3.nexus"], "tree_ORTHOMCL1977_Inner3.nexus": ["tree_ORTHOMCL1_Inner3.nexus"]}}'
            }
        }
        output = parse_log(message=log_message, config_data=self.CONFIG)
        self.assertEqual(output, expected_output)
        
if __name__ == '__main__':
    unittest.main()