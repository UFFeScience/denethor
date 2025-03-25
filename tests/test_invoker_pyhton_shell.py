import unittest
import json
import subprocess

class TestInvokerPython(unittest.TestCase):

    def test_command_construction(self):
        instance_id = "i-1234567890abcdef0"
        key_path = "/path/to/private/key.pem"
        module_identifier = "test_activity"
        module_path = "/home/marcello/Documents/denethor/tests"
        target_method = "handler"
        payload = {
            "execution_tag": "test_execution",
            "provider": "aws",
            "activity": "test_activity",
            "input_data": ["file1", "file2"],
            "env_properties": {
                "bucket": {
                    "name": "test-bucket",
                    "key.input_files": "input/key",
                    "key.test_activity": "output/key"
                },
                "aws": {
                    "data_format": "newick",
                    "path.tmp": "/tmp",
                    "path.input_files": "/input",
                    "path.test_activity": "/output",
                    "path.clustalw": "/clustalw"
                }
            }
        }

        # Convert payload to JSON
        payload_json = json.dumps(payload)

        # Construct the command to execute the target method
        command = f"python3 -c 'import sys; sys.path.append(\"{module_path}\"); import {module_identifier}; {module_identifier}.{target_method}({payload_json}, None)'"
        
        # Execute the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command was successful and output contains expected text
        self.assertEqual(result.returncode, 0)
        self.assertIn("Handler called successfully with the following parameters:", result.stdout)
        self.assertIn(f"Payload: {payload}", result.stdout)
        self.assertIn("Context: None", result.stdout)

if __name__ == "__main__":
    unittest.main()