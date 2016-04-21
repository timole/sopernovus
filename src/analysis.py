import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

SESSION_THRESHOLD_IN_MINUTES = 15

def summarize_applications(df):
    """ Create a summary of the applications as a table. Presumes events are in datetime order
          * Count number of comments for different roles
    """

    prevApplicationId = None
    startIndex = 0
    i = 0

    summary = pd.DataFrame()

    df = df.sort(['applicationId', 'datetime'])

    logger.info("Analyzing events")
    iterator = df.iterrows()
    for index, row in iterator:
        applicationId = row['applicationId']
        municipalityId = row['municipalityId']
	
        if applicationId != prevApplicationId and i != 0 or i == len(df) - 1:
            if prevApplicationId is not None:
                logger.debug("Handle events for application {}".format(applicationId))

                if i == len(df) - 1:
                    to = i + 1
                else:
                    to = i

                app = parse_application_summary(prevApplicationId, prevOperationId, municipalityId, df[startIndex:to])
                summary = summary.append(app, ignore_index = True)
            startIndex = i

        prevApplicationId = applicationId
        prevOperationId = row['operation']

        i = i + 1

        show_progress_bar(i, len(df))

    return summary

def parse_application_summary(applicationId, operation, municipalityId, events):
    return {    "_applicationId": applicationId, 
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
                "daysFromSubmissionToVerdict": count_days_between_events(events, 'submit-application', 'give-verdict') }


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