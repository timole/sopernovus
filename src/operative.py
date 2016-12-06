#!/usr/bin/python

import sys, re, pdb
import logging
import argparse
import json

import numpy as np, pandas as pd
import datetime, random

from pymongo import MongoClient

userIds = {}
userIdSeq = 200000

appIds = {}
appIdSeq = 300000

def parse_args():
    defaultConnString = "mongodb://localhost:27017/"
    parser = argparse.ArgumentParser(description='SOPERNOVSA')
    parser.add_argument('-c', '--connection' , help='Database connection string url, default: ' + defaultConnString, required = False, default = defaultConnString)
    parser.add_argument('-d', '--db' , help='Database name', required = True)
    parser.add_argument('-o', '--output-file', help='Output CSV file', required = True, default = None)
    parser.add_argument('-p', '--output-file-pub', help='Output pub CSV file', required = True, default = None)
    parser.add_argument('-ia', '--input-file-applications', help='Input original application ids CSV file', required = True, default = None)
    parser.add_argument('-im', '--input-file-municipalities', help='Input original municipality ids CSV file', required = True, default = None)
    args = vars(parser.parse_args())
    return args

def report_error(errorId):
    sys.stdout.write(errorId)
    sys.stdout.flush()

def parse_date(dateString):
    if dateString is None or dateString == 0:
        return ""
    else:
        return str(datetime.datetime.fromtimestamp(dateString/1000.0))

args = parse_args()
connectionString = args['connection']
databaseName = args['db']
out = open(args['output_file'], "w")
outPub = open(args['output_file_pub'], "w")

origApps = pd.read_csv(args['input_file_applications'], sep = ';')
pubAppDict = {}
print "create app dict"
for index, row in origApps.iterrows():
    pubAppDict[row["originalApplicationId"]] = row["applicationId"]

origMunis = pd.read_csv(args['input_file_municipalities'], sep = ';')
pubMuniDict = {}
print "create muni dict"
for index, row in origMunis.iterrows():
    pubMuniDict[row["originalMunicipalityId"]] = row["municipalityId"]

print "dicts created"

# out.write("applicationId;created;submitted;verdictGiven\n")
out.write("applicationId;municipalityId;permitType;state;operationId;operationId2;operationId3;operations;createdDate;submittedDate;sentDate;verdictGivenDate;canceledDate;isCanceled;lat;lon\n")
outPub.write("applicationId;municipalityId;permitType;state;operationId;operationId2;operationId3;operations;createdDate;submittedDate;sentDate;verdictGivenDate;canceledDate;isCanceled;lat;lon\n")

client = MongoClient(connectionString)
db = client[databaseName]

applications = db.applications
apps = {}
i = 0

applications = applications.find()

print "Found {} applications".format(applications.count())

errors = 0
total = 0

for application in applications:
    appId = application["_id"]

    if application["infoRequest"]:
        continue

    if not appId in appIds.keys():
        appIds[appId] = str(appIdSeq)
        appIdSeq = appIdSeq + 1
        pubAppId = appIds[appId]

    municipalityId = application["municipality"]

    permitType = application["permitType"]

    comments = application["comments"]

    created = parse_date(application["created"])

    submitted = parse_date(application["submitted"])

    if "canceled" in application.keys():
        canceled = parse_date(application["canceled"])
    else:
        canceled = ""

    if "sent" in application.keys():
        sent = parse_date(application["sent"])
    else:
        sent = ""

    verdictGiven = ""
    verdicts = application["verdicts"]
    if len(verdicts) > 0:
        for verdict in verdicts:
            for paatos in verdict["paatokset"]:
                if "paivamaarat" in paatos.keys():
                    if "anto" in paatos["paivamaarat"].keys():
                        pvm = paatos["paivamaarat"]["anto"]
                        if pvm is not None and verdictGiven == "":
                            verdictGiven = parse_date(pvm)
        if verdictGiven == "" and "timestamp" in verdicts[0].keys() and verdicts[0]["timestamp"] is not None:
            verdictGiven = parse_date(verdicts[0]["timestamp"])

    if verdictGiven is not None:
        verdictGiven = str(verdictGiven)
    else:
        verdictGiven = ""

    canceled = None
    if "canceled" in application.keys():
        canceled = application["canceled"]

    if canceled is not None:
        canceled = parse_date(canceled)
    else:
        canceled = ""

    isCanceled = "false"
    if canceled != "":
        isCanceled = "true"

    try:
        operationId = application["primaryOperation"]["name"]
    except:
        operationId = ""
        report_error('o')

    operationId2 = ""
    operationId3 = ""
    allOperations = operationId

    try:
        if "secondaryOperations" in application.keys() and len(application["secondaryOperations"]) > 0:
            operationId2 = application["secondaryOperations"][0]["name"]
        if "secondaryOperations" in application.keys() and len(application["secondaryOperations"]) > 1:
            operationId3 = application["secondaryOperations"][1]["name"]

        for secondaryOperation in application["secondaryOperations"]:
            allOperations = allOperations + ","
            allOperations = allOperations + str(secondaryOperation["name"])
    except:
        report_error('2')

    try:
        state = application["state"]
    except:
        state = ""
        report_error('s')

    try:
        municipalityId = application["municipality"]
    except:
        municipalityId = ""
        report_error('m')

    lat = ""
    lon = ""
    if "location-wgs84" in application.keys() and len(application["location-wgs84"]) == 2:
        lon = str(application["location-wgs84"][0])
        lat = str(application["location-wgs84"][1])

    # row = appId + ";" + created + ";" + submitted + ";" + verdictGiven + "\n"


    row = appId + ";" + municipalityId + ";" + permitType + ";" + state + ";" + operationId + ";" + operationId2 + ";" + operationId3 + ";" + allOperations + ";"+ created + ";" + submitted + ";" + sent + ";" + verdictGiven + ";" + canceled + ";" + isCanceled + ";" + lat + ";" + lon + "\n"
    row = row.encode('utf-8')
#    print row
    out.write(row)

    municipalityId = long(municipalityId)
    if municipalityId in pubMuniDict.keys():
        pubMunicipalityId = str(pubMuniDict[municipalityId])
    else:
        print "Error: municipality id not found: " + municipalityId
        continue

    if appId in pubAppDict.keys():
        pubAppId = "LP-" + pubMunicipalityId + "-" + str(pubAppDict[appId])
    else:
        report_error('n')
        continue



    pubLat = str(61.495386 + (random.random() * 2 - 1))
    pubLon = str(23.775424 + (random.random() * 2 - 1))

    pubRow = pubAppId + ";" + pubMunicipalityId + ";" + permitType + ";" + state + ";" + operationId + ";" + operationId2 + ";" + operationId3 + ";" + allOperations + ";"+ created + ";" + submitted + ";" + sent + ";" + verdictGiven + ";" + canceled + ";" + isCanceled + ";" + pubLat + ";" + pubLon + "\n"
    pubRow = pubRow.encode('utf-8')
#    print row
    outPub.write(pubRow)

    if i % 1000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

    i = i + 1

#    if i == 3:
#        break

#    except:
#        sys.stdout.write('e')
#        sys.stdout.flush()

