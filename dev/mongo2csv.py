#!/usr/bin/python

import sys, re, pdb
import logging
import argparse

import numpy as np, pandas as pd
import time, datetime, calendar

from pymongo import MongoClient

def parse_args():
    defaultConnString = "mongodb://localhost:27017/"
    parser = argparse.ArgumentParser(description='SOPERNOVSA')
    parser.add_argument('-c', '--connection' , help='Database connection string url, default: ' + defaultConnString, required = False, default = defaultConnString)
    parser.add_argument('-d', '--db' , help='Database name', required = True)
    parser.add_argument('-o', '--output-file', help='Output CSV file', required = True, default = None)
    args = vars(parser.parse_args())
    return args

args = parse_args()
connectionString = args['connection']
databaseName = args['db']
out = open(args['output_file'], "w")

client = MongoClient(connectionString)
db = client[databaseName]

applications = db.applications
apps = {}
i = 0
errors = 0

out.write("_id;infoRequest;primaryOperation;created;submitted;verdictGiven\n")

for application in applications.find():
    try:
        appId = application["_id"]
        if application["infoRequest"] == True:
            infoRequest = 1
        else:
            infoRequest = 0

        if "primaryOperation" in application.keys() and application["primaryOperation"]:
            primaryOperation = application["primaryOperation"]["name"]
        else:
            primaryOperation = ""

        created = application["created"] or ""
        submitted = application["submitted"] or ""
        verdictGiven = ""
        if "verdicts" in application.keys() and len(application["verdicts"]) > 0:
            try:
                verdictGiven = application["verdicts"][0]["paatokset"][0]["paivamaarat"]["anto"]
            except:
                try:
                    if application["verdicts"][0]["timestamp"]:
                        verdictGiven = application["verdicts"][0]["timestamp"]
                    else:
                        verdictGiven = ""
                except:
                    raise


        row = appId + ";" + str(infoRequest) + ";" + primaryOperation + ";" + str(created) + ";" + str(submitted) + ";" + str(verdictGiven) + "\n"
        row = row.encode('utf-8')
        out.write(row)

        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    except:
        raise
        errors = errors + 1
        sys.stdout.write('e')
        sys.stdout.flush()

    i = i + 1

print
print("Errors: {}".format(errors))
