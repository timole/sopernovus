#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, sys, json

from pymongo import MongoClient

a = None

def parseColumnNames(f):
    line = f.readline()
    return line.split(',')

inputFilename = sys.argv[1]
inputFilenameCron = sys.argv[2]
outputfilename = sys.argv[3]
outputfilenameIds = sys.argv[4]
outputfilenameMunicipalityIds = sys.argv[5]

client = MongoClient('localhost', 27017)
db = client['lupapiste']
applications = db.applications
apps = {}
i = 0
for application in applications.find():
    appId = application["_id"]
    appFields = {}
    if "primaryOperation" in application.keys():
        if application["primaryOperation"] is not None and "name" in application["primaryOperation"].keys():
            op = application["primaryOperation"]["name"]
    else:
        op = ""

    appFields["primaryOperation"] = op
    apps[appId] = appFields
    if i % 1000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    i = i + 1

f = open(inputFilename, "r")
fcron = open(inputFilenameCron, "r")
out = open(outputfilename, "w")
outIds = open(outputfilenameIds, "w")
outMunicipalityIds = open(outputfilenameMunicipalityIds, "w")

columnNames = parseColumnNames(f)
print("Column names")


i = 0
for col in columnNames:
    print `i` + ": " + col
    i = i + 1

out.write("datetime;applicationId;operation;municipalityId;userId;role;action;target\n")

ids = {}
idSeq = 100000

municipalityIds = {}
municipalityIdSeq = 1000

userIds = {}
userIdSeq = 100000

parsed = 0
errors = 0
for line in f:
    fields = line.split(',')
    datetime = re.match("\"(.*) .*", fields[1]).group(1)

#    print "ts: " + datetime
    rawMatch = re.match(".*? - (.*)\"", line)
    js = rawMatch.group(1).replace("\"\"", "\"")
    
    try:
        data = json.loads(js)
    except ValueError:
        errors = errors + 1
        #sys.stdout.write('E')
        #print("Error parsing json")
        continue

    if data["type"] == "command":
#        print(data)
        action = data["action"]
        if action == "login" or action == "register-user" or action == "update-user" or action == "update-user-organization" or action == "reset-password" or action == "users-for-datatables" or action == "impersonate-authority" or action == "frontend-error" or action == "browser-timing":
            continue
#        if not id in data["data"].keys():
#            continue
        id = ""
        role = ""
        userId = ""
        try:

            if action == "create-application":
                id = ""
                role = data["user"]["role"]
                userId = data["user"]["id"]
            else:
                if action == "neighbor-response":
#                    print(data)
                    id = data["data"]["applicationId"]
                    role = "neighbor"
                    userId = data["data"]["neighborId"]
                else:
                    userId = data["user"]["id"]
                    role = data["user"]["role"]
                    id = data["data"]["id"]
        except:
            #sys.stdout.write('i')
            errors = errors + 1

            #print("No id for " + data["action"])

        target = ""
        try:
            if action == "update-doc":
                target = data["data"]["updates"][0][0]
            if action == "upload-attachment":
                target = data["data"]["attachmentType"]["type-id"]
            if action == "mark-seen":
                target = data["data"]["type"]
            if action == "approve-doc":
                target = data["data"]["path"]
            if action == "add-comment":
                target = data["data"]["target"]["type"]
            if action == "create-doc":
                target = data["data"]["schemaName"]
            if action == "invite-with-role":
                target = data["data"]["role"]
        except:
            #sys.stdout.write('t')
            target = ""
            errors = errors + 1

        if id != "":
            if not id in ids.keys():
                ids[id] = str(idSeq)
                idSeq = idSeq + 1
        
            pubId = ids[id]
        else:
            pubId = ""

        pubMunicipalityId = ""
        municipalityId = ""
        if id != "":
            if id is not None and len(id.split('-')) == 4:
                municipalityId = id.split('-')[1]
                if not municipalityId in municipalityIds.keys():
                    municipalityIds[municipalityId] = str(municipalityIdSeq)
                    municipalityIdSeq = municipalityIdSeq + 1

                pubMunicipalityId = municipalityIds[municipalityId]

        if not userId in userIds.keys():
            userIds[userId] = str(userIdSeq)
            userIdSeq = userIdSeq + 1
        pubUserId = userIds[userId]

        op = ""
        if id in apps.keys():
            app = apps[id]
            op = app["primaryOperation"]

        l = datetime + ";" + pubId  + ";" + op + ";" + pubMunicipalityId + ";" + pubUserId + ";" + role + ";" + action + ";" + target + "\n"
#        print(l)
        out.write(l)

    parsed = parsed + 1

    if parsed % 1000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

columnNames = parseColumnNames(fcron)
for line in fcron:
    fields = line.split(',')

    datetime = re.match("\"(.*) .*", fields[1]).group(1)

#    print "ts: " + datetime
    raw = fields[7]

    rawMatch = re.match(".*?\[(LP.*?)\].*", raw)
    id = rawMatch.group(1)

    jsMatch = re.match(".*? - (.*)\"", line)
    js = jsMatch.group(1).replace("\"\"", "\"")
        
    try:
        data = json.loads(js)
    except ValueError:
        errors = errors + 1
        #sys.stdout.write('E')
        #print("Error parsing json")
        continue

    if data["event"] == "Found new verdict":
        if id != "":
            if not id in ids.keys():
                ids[id] = str(idSeq)
                idSeq = idSeq + 1
        
            pubId = ids[id]
        else:
            pubId = ""

        op = ""
        if id in apps.keys():
            app = apps[id]
            op = app["primaryOperation"]
                
        l = datetime + ";" + pubId  + ";" + op + ";" + pubMunicipalityId + ";" + pubUserId + ";" + role + ";" + action + ";" + target + "\n"
#        print(l)
        out.write(l)

#    else:
        #errors = errors + 1
        #sys.stdout.write('N')

    parsed = parsed + 1

    if parsed % 10000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

outIds.write("applicationId;originalApplicationId\n")
for idKey in ids.keys():
    id = ids[idKey]
    if id is None or idKey is None:
        print "Error: None:"
        print("id")
        print(id)
        print("idKey")
        print(idKey)
    else:
        outIds.write(id + ";" + idKey + "\n")

outMunicipalityIds.write("municipalityId;originalMunicipalityId\n")
for idKey in municipalityIds.keys():
    id = municipalityIds[idKey]
    if id is None or idKey is None:
        print "Error: None:"
        print("id")
        print(id)
        print("idKey")
        print(idKey)
    else:
        outMunicipalityIds.write(id + ";" + idKey + "\n")

outMunicipalityIds.close()
outIds.close()
out.close()

print

print "Errors: " + str(errors)
print "Parsed: " + str(parsed)
