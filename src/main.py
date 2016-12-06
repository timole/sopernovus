#!/usr/bin/python

import sys, re, pdb
import logging
import argparse

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib, datetime

import utils, data_helper, analysis, user_analysis

def parse_args():
    parser = argparse.ArgumentParser(description='SOPERNOVUS analysator')
    parser.add_argument('-iu', '--input-file-usage', help='Input CSV file for usage data', required=True)
    parser.add_argument('-io', '--input-file-operative', help='Input CSV file for operative data', required=False)
    parser.add_argument('-oa', '--output-file-applications', help='Output CSV file for applications', required=False, default = None)
    parser.add_argument('-ou', '--output-file-users', help='Output CSV file for users', required=False, default = None)
    parser.add_argument('-oap', '--output-file-applications-prediction', help='Output CSV file for app prediction', required=False, default = None)
    args = vars(parser.parse_args())
    return args

def print_stats(startTime):
    print("Succesfully parsed {} apps".format(len(appsSummary)))
    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime
    print("Analysis took {} minutes:".format(round(elapsedTime.total_seconds() / 60, 1)))

def create_application_summary(outputFileName):
    logger = logging.getLogger(__name__)

    # exported to global scope for debugging purposes
    global appsSummary
    appsSummary =  analysis.summarize_applications(df, odf)

    logger.info("N of applications = {}".format(len(appsSummary)))
    print(appsSummary)

    if outputFileName is not None:
        appsSummary.to_csv(outputFileName, sep=';', encoding='utf-8')
    else:
        print appsSummary

def create_user_summary(outputFileName):
    logger = logging.getLogger(__name__)

    # exported to global scope for debugging purposes
    global usersSummary
    usersSummary =  user_analysis.summarize_users(df)

    logger.info("N of users = {}".format(len(usersSummary)))
    print(usersSummary)

    if outputFileName is not None:
        usersSummary.to_csv(outputFileName, sep=';', encoding='utf-8')
    else:
        print usersSummary

def create_prediction_summary(outputFileName):
    logger = logging.getLogger(__name__)

    # exported to global scope for debugging purposes
    global predictionSummary
    predictionSummary =  analysis.summarize_applications(df)

    logger.info("N of applications = {}".format(len(predictionSummary)))
    print(predictionSummary)

    if outputFileName is not None:
        predictionSummary.to_csv(outputFileName, sep=';', encoding='utf-8')
    else:
        print predictionSummary


def main():
    args = parse_args()
    inputFileNameUsage = args['input_file_usage']
    inputFileNameOperative = args['input_file_operative']
    outputApplicationsFileName = args['output_file_applications']
    outputUsersFileName = args['output_file_users']
    predictionOutputFileName = args['output_file_applications_prediction']

    utils.log_config()    
    logger = logging.getLogger(__name__)

    startTime = datetime.datetime.now()

    # exported to global scope for debugging purposes
    global df
    df = data_helper.import_data(inputFileNameUsage)

    global odf

    if inputFileNameOperative:
        odf = data_helper.import_operative_data(inputFileNameOperative)
    else:
        odf = None

    logger.info("N of events: {}, from {} to {} ".format(len(df), df['datetime'].min(), df['datetime'].max()))

    create_user_summary(outputUsersFileName)
    create_application_summary(outputApplicationsFileName)
#    create_prediction_summary(predictionOutputFileName)

    print_stats(startTime)

if __name__ == "__main__":
    main()
