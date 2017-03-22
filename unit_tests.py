import logfile_analyze
import unittest


class testing(unittest.TestCase):
    def test_values(self):
        self.assertEqual(logfile_analyze.human_readable_size(1500), '1.5 KB')

if __name__ == '__main__':
    unittest.main()
