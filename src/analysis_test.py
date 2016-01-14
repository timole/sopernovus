import unittest

import data_helper
import analysis

_TEST_DATA_FILE = "lupapiste-usage-test.csv"

class TestApplicationSummary(unittest.TestCase):

    def setUp(self):
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.apps = analysis.summarize_applications(self.df)

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 3)

    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['comments'].item(), 7)
        self.assertEqual(apps[apps['applicationId'] == 101]['comments'].item(), 0)

        self.assertEqual(apps[apps['applicationId'] == 100]['comments-applicant'].item(), 7)
        self.assertEqual(apps[apps['applicationId'] == 100]['comments-authority'].item(), 0)

    def test_count_session_length_by_role(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 101]['session-length'].item(), 6)
        self.assertEqual(apps[apps['applicationId'] == 101]['session-length-applicant'].item(), 6)
        self.assertEqual(apps[apps['applicationId'] == 101]['session-length-authority'].item(), 0)

if __name__ == '__main__':
    unittest.main()
