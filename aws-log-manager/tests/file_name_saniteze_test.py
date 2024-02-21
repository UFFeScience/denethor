import unittest
import re

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', filename)

class TestFilenameSanitization(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("valid_filename.txt"), "valid_filename.txt")
        self.assertEqual(sanitize_filename("folder/invalid**filename.txt"), "folder/invalid__filename.txt")
        self.assertEqual(sanitize_filename("another\\invalid:filename.txt"), "another_invalid_filename.txt")
        self.assertEqual(sanitize_filename("yet another*invalid|filename.txt"), "yet_another_invalid_filename.txt")
        self.assertEqual(sanitize_filename("yet another\invalid|filename.txt"), "yet_another_invalid_filename.txt")
        self.assertEqual(sanitize_filename("filename_with:colon.txt"), "filename_with_colon.txt")
        self.assertEqual(sanitize_filename("filename_with?question_mark.txt"), "filename_with_question_mark.txt")
        self.assertEqual(sanitize_filename("filename_with*asterisk.txt"), "filename_with_asterisk.txt")
        self.assertEqual(sanitize_filename("filename_with|pipe.txt"), "filename_with_pipe.txt")
        self.assertEqual(sanitize_filename("filename_with<less_than.txt"), "filename_with_less_than.txt")
        self.assertEqual(sanitize_filename("filename_with>greater_than.txt"), "filename_with_greater_than.txt")
        self.assertEqual(sanitize_filename("filename_with\"double_quotes.txt"), "filename_with_double_quotes.txt")
        # self.assertEqual(sanitize_filename("filename_with/single_quote.txt"), "filename_with_single_quote.txt")
if __name__ == '__main__':
    unittest.main()