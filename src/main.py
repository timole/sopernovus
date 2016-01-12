#!/usr/bin/python

import sys, re, pdb
import logging

import numpy as np, pandas as pd

import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

import utils, data_helper, analysis

def main():
    if(len(sys.argv) < 3):
        print "Usage: main.py <inputfile> <outputfile>"
        sys.exit()

    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]

    utils.log_config()
    logger = logging.getLogger(__name__)

    logger.info("Data file: {}".format(inputFileName))

    # exported to global scope for debugging purposes
    global df

    df = data_helper.import_data(inputFileName)

    logger.info("N of events: {}, from {} to {} ".format(len(df), df['datetime'].min(), df['datetime'].max()))

    # exported to global scope for debugging purposes
    global apps
    apps =  analysis.summarize_applications(df)

    logger.info("N of applications = {}".format(len(apps)))

    print(apps)

    apps.to_csv(outputFileName, sep=';', encoding='utf-8')
    print("Succesfully wrote {} apps to file {}".format(len(apps), outputFileName))


if __name__ == "__main__":
    main()
