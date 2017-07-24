"""Tests code format.

http://pep8.readthedocs.io/en/latest/advanced.html
https://stackoverflow.com/questions/29163117/running-pep8-checks-from-python
https://gist.github.com/jalp/8644578

"""
import unittest
import pycodestyle
import subprocess
import re

class TestCodeFormat(unittest.TestCase):

    def __get_staged_files(self):
        """Get all files staged for the current commit."""
        # get output of git status
        git = subprocess.Popen(['git', 'status', '--porcelain'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,error = git.communicate()
        # parse output for file names
        modified_re = re.compile('^\s+[AM]+\s+(.*\.py)', re.MULTILINE)
        staged_files = modified_re.findall(out.decode('utf-8'))
        return staged_files

    def test_pep8_conformance(self):
        """Test that staged code conforms to PEP8."""
        style = pycodestyle.StyleGuide(quiet=True)
        result = style.check_files(self.__get_staged_files())
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


if __name__ == '__main__':
        unittest.main()
