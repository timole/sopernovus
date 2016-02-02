import unittest

import data_helper
import analysis

_TEST_DATA_FILE = "lupapiste-usage-test.csv"

class TestApplicationSummary(unittest.TestCase):

    def setUp(self):
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.apps = analysis.summarize_applications(self.df)

        # print apps once for debugging
        print "####################################################################"
        print self.apps

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 5)

    def test_number_of_events(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['events'].item(), 129)
        self.assertEqual(apps[apps['applicationId'] == 102]['events'].item(), 5)


    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['comments'].item(), 7)
        self.assertEqual(apps[apps['applicationId'] == 101]['comments'].item(), 0)

        self.assertEqual(apps[apps['applicationId'] == 100]['comments-applicant'].item(), 7)
        self.assertEqual(apps[apps['applicationId'] == 100]['comments-authority'].item(), 0)

    def test_count_session_length_by_role(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 101]['session-length'].item(), 11)
        self.assertEqual(apps[apps['applicationId'] == 101]['session-length-applicant'].item(), 11)
        self.assertEqual(apps[apps['applicationId'] == 101]['session-length-authority'].item(), 0)

    def test_is_submitted(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['is-submitted'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 101]['is-submitted'].item(), False)

    def test_is_cancelled(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 102]['is-cancelled'].item(), False)
        self.assertEqual(apps[apps['applicationId'] == 103]['is-cancelled'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 104]['is-cancelled'].item(), True)

    def test_has_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['has-verdict'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 101]['has-verdict'].item(), False)


if __name__ == '__main__':
    unittest.main()
