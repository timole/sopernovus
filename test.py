import unittest

from utils import utils
from utils import data_helper
from analysis import users
from analysis import applications
import pdb
import logging
import numpy as np
import pandas as pd

_TEST_DATA_FILE = "lupapiste-usage-test.csv"
_OPERATIVE_TEST_DATA_FILE = "lupapiste-operative-test.csv"

class TestApplicationSummary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pd.set_option('display.width', 240)
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.odf = data_helper.import_operative_data("data/" + _OPERATIVE_TEST_DATA_FILE)
        self.apps = applications.summarize_applications(self.df, self.odf, False)

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 5)

    def test_operation_type(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['operationId'].item(), "asuinrakennus")
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['operationId'].item(), "pientalo")
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['operationId'].item(), "muu-maisema-toimenpide")

    def test_municipality(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['municipalityId'].item(), 90)

    def test_number_of_events(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['events'].item(), 136)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['events'].item(), 81)


    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['comments'].item(), 7)

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['commentsApplicant'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['commentsAuthority'].item(), 0)
        
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['commentsApplicant'].item(), 4)
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

        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['isCancelled'].item(), True)

    def test_has_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['hasVerdict'].item(), True)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['hasVerdict'].item(), False)

    def test_days_from_submission_to_verdict(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['daysFromSubmissionToVerdict'].item(), 32)
        self.assertEqual(apps[apps['applicationId'] == 'LP-101']['daysFromSubmissionToVerdict'].item(), None)

    def test_lead_times(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['leadTime'].item(), 50)

    def test_flow_efficiency(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['flowEfficiency'].item(), 10)
        self.assertEqual(apps[apps['applicationId'] == 'LP-900']['flowEfficiency'].item(), 100)
        self.assertEqual(apps[apps['applicationId'] == 'LP-901']['flowEfficiency'].item(), 50)

    def test_count_unique_action(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['n-create-doc'].item(), 2)

    def test_applicants(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-900']['applicantId'].item(), 101302)
        self.assertEqual(apps[apps['applicationId'] == 'LP-900']['applicants'].item(), 2)

    def test_authorities(self):
        apps = self.apps
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['authorityId'].item(), 102986)
        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['authorities'].item(), 1)

class TestPredictiveApplicationSummary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pd.set_option('display.width', 240)
        #TODO relative path to something better?
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.odf = data_helper.import_operative_data("data/" + _OPERATIVE_TEST_DATA_FILE)
        self.apps = applications.summarize_applications(self.df, self.odf, True)

    def test_number_of_applications(self):
        self.assertEqual(len(self.apps), 2)
        
    def test_number_of_comments(self):
        apps = self.apps

        self.assertEqual(apps[apps['applicationId'] == 'LP-100']['comments'].item(), 0)
        self.assertEqual(apps[apps['applicationId'] == 'LP-102']['comments'].item(), 5)


class TestUsersSummary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.df = data_helper.import_data("data/" + _TEST_DATA_FILE)
        self.users = users.summarize_users(self.df)

    def test_number_of_users(self):
        self.assertEqual(len(self.users), 6)

    def test_user_applications(self):
        users = self.users

        self.assertEqual(users[users['userId'] == 101302]['applicantRoles'].item(), 3)
        self.assertEqual(users[users['userId'] == 101346]['authorityRoles'].item(), 1)


if __name__ == '__main__':
    utils.log_config()
    logger = logging.getLogger(__name__)
    logger.info("Run unit tests")
    unittest.main()

