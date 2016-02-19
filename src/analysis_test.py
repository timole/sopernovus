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

        self.assertEqual(apps[apps['applicationId'] == 100]['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 101]['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 102]['comments'].item(), 4)

        self.assertEqual(apps[apps['applicationId'] == 100]['commentsApplicant'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 100]['commentsAuthority'].item(), 0)
        
        self.assertEqual(apps[apps['applicationId'] == 102]['commentsApplicant'].item(), 1)
        self.assertEqual(apps[apps['applicationId'] == 102]['commentsAuthority'].item(), 3)

    def test_number_of_update_docs(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 101]['updateDocs'].item(), 7)

    def test_count_session_length_by_role(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 101]['sessionLength'].item(), 11)
        self.assertEqual(apps[apps['applicationId'] == 101]['sessionLengthApplicant'].item(), 11)
        self.assertEqual(apps[apps['applicationId'] == 101]['sessionLengthAuthority'].item(), 0)

    def test_is_submitted(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['isSubmitted'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 101]['isSubmitted'].item(), False)

    def test_is_cancelled(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 102]['isCancelled'].item(), False)
        self.assertEqual(apps[apps['applicationId'] == 103]['isCancelled'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 104]['isCancelled'].item(), True)

    def test_has_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 100]['hasVerdict'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 101]['hasVerdict'].item(), False)


if __name__ == '__main__':
    unittest.main()
