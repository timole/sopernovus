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

        if applicationId != prevApplicationId and i != 0 or i == len(df) - 1:
            if not math.isnan(prevApplicationId):
                logger.debug("Handle events for application {}".format(applicationId))

                if i == len(df) - 1:
                    to = i + 1
                else:
                    to = i

                app = parse_application_summary(prevApplicationId, df[startIndex:to])
                summary = summary.append(app, ignore_index = True)
            startIndex = i

        prevApplicationId = applicationId

        i = i + 1

        show_progress_bar(i, len(df))

    return summary

def parse_application_summary(applicationId, events):
    return {    "applicationId": applicationId, 
                "events": len(events),
                "comments": len(find_events_by_action(events, 'add-comment')),
                "comments-applicant": len(find_events_by_action_and_role(events, 'add-comment', 'applicant')),
                "comments-authority": len(find_events_by_action_and_role(events, 'add-comment', 'authority')),
                "session-length": count_session_length(events, SESSION_THRESHOLD_IN_MINUTES),
                "session-length-applicant": count_session_length_by_role(events, 'applicant', SESSION_THRESHOLD_IN_MINUTES),
                "session-length-authority": count_session_length_by_role(events, 'authority', SESSION_THRESHOLD_IN_MINUTES),
                "is-submitted": len(find_events_by_action(events, 'submit-application')) > 0,
                "has-verdict": len(find_events_by_action(events, 'give-verdict')) > 0,
                "lead-time-from-submission-to-verdict": count_days_between_events(events, 'submit-application', 'give-verdict') }

def find_events_by_action(events, action):
    return events[events['action'] == action]

def find_events_by_action_and_role(events, action, role):
    # TODO: one liner would be better, but & is not supported
    result = events[events['action'] == action]
    result = result[result['role'] == role]
    return result

def show_progress_bar(index, maxIndex):
    if index % 1000 == 0:
        logger.info("Processed {}/{} rows".format(index, maxIndex))

def count_session_length(events, thresholdMinutes):
    delta = timedelta(minutes = thresholdMinutes)

    timestamps = events['datetime']

    if(len(timestamps) == 0):
        return 0

    prev = prev = timestamps.iloc[0]
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
