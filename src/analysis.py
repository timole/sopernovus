import sys, math
import pandas as pd
import logging

logger = logging.getLogger(__name__)

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

                app = parse_application_summary(prevApplicationId, df[startIndex:i])
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
                "comments-authority": len(find_events_by_action_and_role(events, 'add-comment', 'authority'))}

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
