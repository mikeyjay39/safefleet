import logfile_analyze
import unittest


class testing(unittest.TestCase):
    logfile_analyze.log_meta = {'logfile1': 1000, 'logfile2': 500,
                                'logfile3': 500}

    def test_values(self):
        self.assertEqual(logfile_analyze.human_readable_size(1500), '1.5 KB')

if __name__ == '__main__':
    unittest.main()
