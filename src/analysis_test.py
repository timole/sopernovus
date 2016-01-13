import unittest

import data_helper
import analysis

_TEST_DATA_FILE = "lupapiste-usage-test.csv"

class TestApplicationSummary(unittest.TestCase):

    def setUp(self):
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.apps = analysis.summarize_applications(self.df)
        print self.apps

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 3)

    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['comments'].item(), 4)
        self.assertEqual(apps[apps['applicationId'] == 101]['comments'].item(), 0)

        self.assertEqual(apps[apps['applicationId'] == 100]['comments-applicant'].item(), 2)
        self.assertEqual(apps[apps['applicationId'] == 100]['comments-authority'].item(), 2)


if __name__ == '__main__':
    unittest.main()
