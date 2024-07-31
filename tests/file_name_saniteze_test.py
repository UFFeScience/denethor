import unittest
import re

def sanitize_file_name(file_name):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', file_name)

class Testfile_nameSanitization(unittest.TestCase):
    def test_sanitize_file_name(self):
        self.assertEqual(sanitize_file_name("valid_file_name.txt"), "valid_file_name.txt")
        self.assertEqual(sanitize_file_name("folder/invalid**file_name.txt"), "folder/invalid__file_name.txt")
        self.assertEqual(sanitize_file_name("another\\invalid:file_name.txt"), "another_invalid_file_name.txt")
        self.assertEqual(sanitize_file_name("yet another*invalid|file_name.txt"), "yet_another_invalid_file_name.txt")
        self.assertEqual(sanitize_file_name("yet another\invalid|file_name.txt"), "yet_another_invalid_file_name.txt")
        self.assertEqual(sanitize_file_name("file_name_with:colon.txt"), "file_name_with_colon.txt")
        self.assertEqual(sanitize_file_name("file_name_with?question_mark.txt"), "file_name_with_question_mark.txt")
        self.assertEqual(sanitize_file_name("file_name_with*asterisk.txt"), "file_name_with_asterisk.txt")
        self.assertEqual(sanitize_file_name("file_name_with|pipe.txt"), "file_name_with_pipe.txt")
        self.assertEqual(sanitize_file_name("file_name_with<less_than.txt"), "file_name_with_less_than.txt")
        self.assertEqual(sanitize_file_name("file_name_with>greater_than.txt"), "file_name_with_greater_than.txt")
        self.assertEqual(sanitize_file_name("file_name_with\"double_quotes.txt"), "file_name_with_double_quotes.txt")
        # self.assertEqual(sanitize_file_name("file_name_with/single_quote.txt"), "file_name_with_single_quote.txt")
if __name__ == '__main__':
    unittest.main()