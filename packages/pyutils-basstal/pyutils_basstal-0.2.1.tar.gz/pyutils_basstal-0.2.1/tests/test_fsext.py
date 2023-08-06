import unittest
import pyutils.fsext as fs
import os


class TestFsext(unittest.TestCase):
    def test_to_base64(self):
        cwd = os.getcwd()
        if not cwd.endswith('tests'):
            os.chdir('tests')
        self.assertEqual(fs.to_base64('abs'), '')
        self.assertNotEqual(fs.to_base64('./data/to_base64.png'), '')
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, 'to_base64')
        content = fs.to_base64('./data/to_base64.png', output_file)
        with open(output_file, 'r+', encoding='utf-8') as f:
            self.assertEqual(f.readline(), content)
