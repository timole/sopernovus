import unittest

import data_helper
import analysis
import pdb

_TEST_DATA_FILE = "lupapiste-usage-test.csv"

class TestApplicationSummary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.apps = analysis.summarize_applications(self.df, None)

        # print apps once for debugging
        print "Application summary based on test data:"
        print self.apps

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 5)

    def test_operation_type(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['_operationId'].item(), "asuinrakennus")
        self.assertEqual(apps[apps['applicationId'] == 'LP-103']['_operationId'].item(), "muu-maisema-toimenpide")

    def test_municipality(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['_municipalityId'].item(), 1056)

    def test_number_of_events(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['events'].item(), 129)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['events'].item(), 5)


    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['comments'].item(), 4)

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['commentsApplicant'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['commentsAuthority'].item(), 0)
        
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['commentsApplicant'].item(), 1)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['commentsAuthority'].item(), 3)

    def test_number_of_update_docs(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['updateDocs'].item(), 7)

    def test_count_session_length(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['sessionLength'].item(), 2)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['sessionLengthApplicant'].item(), 2)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['sessionLengthAuthority'].item(), 0)

    def test_is_submitted(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['isSubmitted'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['isSubmitted'].item(), False)

    def test_is_cancelled(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['isCancelled'].item(), False)
        self.assertEqual(apps[apps['applicationId'] == 'LP-103']['isCancelled'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 'LP-104']['isCancelled'].item(), True)

    def test_has_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['hasVerdict'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['hasVerdict'].item(), False)

    def test_days_from_submission_to_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['daysFromSubmissionToVerdict'].item(), 31)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['daysFromSubmissionToVerdict'].item(), None)

if __name__ == '__main__':
    unittest.main()
