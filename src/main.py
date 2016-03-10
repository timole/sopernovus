#!/usr/bin/python

import sys, re, pdb
import logging
import argparse

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib, datetime

import utils, data_helper, analysis

def parse_args():
    parser = argparse.ArgumentParser(description='SOPERNOVUS analysator')
    parser.add_argument('-i', '--input-file', help='Input CSV file', required=True)
    parser.add_argument('-o', '--output-file', help='Output CSV file', required=False, default = None)
    parser.add_argument('-p', '--prediction-output-file', help='Output CSV file for prediction', required=False, default = None)
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
    appsSummary =  analysis.summarize_applications(df)

    logger.info("N of applications = {}".format(len(appsSummary)))
    print(appsSummary)

    if outputFileName is not None:
        appsSummary.to_csv(outputFileName, sep=';', encoding='utf-8')
    else:
        print appsSummary

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
    inputFileName = args['input_file']
    outputFileName = args['output_file']
    predictionOutputFileName = args['prediction_output_file']

    utils.log_config()
    logger = logging.getLogger(__name__)

    logger.info("Data file: {}".format(inputFileName))

    startTime = datetime.datetime.now()

    # exported to global scope for debugging purposes
    global df
    df = data_helper.import_data(inputFileName)

    logger.info("N of events: {}, from {} to {} ".format(len(df), df['datetime'].min(), df['datetime'].max()))

    create_application_summary(outputFileName)
    create_prediction_summary(predictionOutputFileName)

    print_stats(startTime)

if __name__ == "__main__":
    main()
