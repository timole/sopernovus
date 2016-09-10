import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

SESSION_THRESHOLD_IN_MINUTES = 15

def summarize_applications(df, odf):
    """ Create a summary of the applications as a table. Presumes events are in datetime order
          * Count number of comments for different roles
    """

    prevApplicationId = None
    startIndex = 0
    i = 0

    summary = None

    df = df.sort_values(['applicationId', 'datetime'])

    numberOfApplications = df["applicationId"].nunique()

    logger.info("Analyzing events")
    iterator = df.iterrows()
    for index, row in iterator:
        applicationId = row['applicationId']

        if applicationId != prevApplicationId and i != 0 or i == len(df) - 1:
            if prevApplicationId is not None:
                logger.debug("Handle events for application {}".format(applicationId))

                if i == len(df) - 1:
                    to = i + 1
                else:
                    to = i

                app = parse_application_summary(prevApplicationId, prevOperationId, prevMunicipalityId, df[startIndex:to], odf[odf['applicationId'] == prevApplicationId].iloc[0].to_dict())

                if summary is None:
                    summary = pd.DataFrame(app, index = [0])
                else:
                    summary.loc[len(summary)] = app
            startIndex = i

        prevApplicationId = applicationId
        prevOperationId = row['operation']
        prevMunicipalityId = row['municipalityId']

        i = i + 1

        show_progress_bar(i, len(df))

    if odf is not None:
        summary = pd.merge(summary, odf, on = 'applicationId')

    return summary

def parse_application_summary(applicationId, operation, municipalityId, events, appInfo):
    app = {    "applicationId": applicationId, 
                "_municipalityId": municipalityId,
                "_operationId": operation,
                "events": len(events),
				"userIds": find_unique_users_by_application(events),
                "comments": len(find_events_by_action_and_target(events, 'add-comment', 'application')),
                "commentsApplicant": len(find_events_by_action_and_role_and_target(events, 'add-comment', 'applicant', 'application')),
                "commentsAuthority": len(find_events_by_action_and_role_and_target(events, 'add-comment', 'authority', 'application')),
                "invitesAuthority" : len(find_events_by_action_and_role(events,'invite-with-role','authority')),
                "invitesApplicant": len(find_events_by_action_and_role(events,'invite-with-role','applicant')),
                "sessionLength": count_session_length(events, SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthApplicant": count_session_length_by_role(events, 'applicant', SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthAuthority": count_session_length_by_role(events, 'authority', SESSION_THRESHOLD_IN_MINUTES),
                "updateDocs": len(find_events_by_action(events, 'update-doc')),
                "createDocs": len(find_events_by_action(events, 'create-doc')),
                "isSubmitted": len(find_events_by_action(events, 'submit-application')) > 0,
                "hasVerdict": len(find_events_by_action(events, 'give-verdict')) > 0,
                "isCancelled": len(find_events_by_action(events, 'cancel-application')) > 0 or 
                                len(find_events_by_action(events, 'cancel-application-authority')) > 0,
                "daysFromSubmissionToVerdict": count_days_between_events(events, 'submit-application', 'give-verdict'),
                "leadTimeCreated2Submitted": count_days(appInfo, 'createdDate', 'submittedDate'),
                "leadTimeSubmitted2Sent": count_days(appInfo, 'submittedDate', 'sentDate'),
                "leadTimeSent2VerdictGiven": count_days(appInfo, 'sentDate', 'verdictGivenDate'),
                "leadTimeCreated2Sent": count_days(appInfo, 'createdDate', 'sentDate'),
                "leadTime": count_days(appInfo, 'createdDate', 'verdictGivenDate'),
                "leadTimeCreated2Canceled": count_days(appInfo, 'createdDate', 'canceledDate'),
                "leadTimeSubmitted2VerdictGiven": count_days(appInfo, 'submittedDate', 'verdictGivenDate'),
                "flowEfficiencyCreated2Submitted": count_flow_efficiency(appInfo, events, 'createdDate', 'submittedDate'),
                "flowEfficiencySubmitted2Sent": count_flow_efficiency(appInfo, events, 'submittedDate', 'sentDate'),
                "flowEfficiencySent2VerdictGiven": count_flow_efficiency(appInfo, events, 'sentDate', 'verdictGivenDate'),
                "flowEfficiencyCreated2Sent": count_flow_efficiency(appInfo, events, 'createdDate', 'sentDate'),
                "flowEfficiency": count_flow_efficiency(appInfo, events, 'createdDate', 'verdictGivenDate'),
                "flowEfficiencyCreated2Canceled": count_flow_efficiency(appInfo, events, 'createdDate', 'canceledDate'),
                "flowEfficiencySubmitted2VerdictGiven": count_flow_efficiency(appInfo, events, 'submittedDate', 'verdictGivenDate')
            }
    pdb.set_trace()
    return app

def find_unique_users_by_application(events):
	return events.userId.nunique()

def find_events_by_action(events, action):
    return events[events['action'] == action]

def find_events_by_action_and_target(events, action, target):
    result = events[events['action'] == action]
    result = events[events['target'] == target]
    return result

def find_events_by_action_and_role(events, action, role):
    # TODO: one liner would be better, but & is not supported
    result = events[events['action'] == action]
    result = result[result['role'] == role]
    return result

def find_events_by_action_and_role_and_target(events, action, role, target):
    # TODO: one liner would be better, but & is not supported
    result = find_events_by_action_and_role(events, action, role)
    result = result[result['role'] == role]
    result = result[result['target'] == target]
    return result

def show_progress_bar(index, maxIndex):
    if index % 1000 == 0:
        logger.info("Processed {}/{} rows".format(index, maxIndex))

def count_session_length(events, thresholdMinutes):
    delta = timedelta(minutes = thresholdMinutes)

    timestamps = events['datetime']

    if(len(timestamps) == 0):
        return 0

    prev = timestamps.iloc[0]
    i = 1
    totalSession = 0
    while i < len(timestamps):
        diff = timestamps.iloc[i] - prev
        prev = timestamps.iloc[i]
        if(diff < delta):
            totalSession = totalSession + diff.total_seconds()

        i = i + 1
        
    return round(totalSession / 60, 0)

def count_session_length_by_role(events, role, thresholdMinutes):
    return count_session_length(events[events['role'] == role], thresholdMinutes)

def count_days_between_events(events, fromEvent, tillEvent):
    e1 = find_events_by_action(events, fromEvent)
    e2 = find_events_by_action(events, tillEvent)

    if(len(e1) > 0 and len(e2) > 0):
        firstSubmission = e1.iloc(0)
        verdictGiven = e2.iloc(0)        
        timeBetween = e2['datetime'].iloc[0] - e1['datetime'].iloc[0]
        return timeBetween.days
    else:
        return None

def count_days(app, fromDate, tillDate):
    delta = app[tillDate] - app[fromDate]

    if pd.isnull(delta):
        return None
    else:
        return int(delta.days)

def count_flow_efficiency(app, events, fromDate, tillDate):
    days = count_days(app, fromDate, tillDate)
    if days is None:
        return None

    nOfProcessedDays = len(events['datetime'].dt.normalize().unique())
    flowEfficiency = int(round(float(nOfProcessedDays) / days, 2) * 100)

    return flowEfficiency
