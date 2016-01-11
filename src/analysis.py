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

        if applicationId != prevApplicationId and prevApplicationId is not None:
            app = parse_application_summary(prevApplicationId, df[startIndex:i])
            summary = summary.append(app, ignore_index = True)
            startIndex = i

        prevApplicationId = applicationId
        i = i + 1

        if i % 100000 == 0:
            logger.info("Processed {}/{} rows".format(i, len(df)))

    summary = summary.append(parse_application_summary(prevApplicationId, df[startIndex:i]), ignore_index = True)
    return summary

def parse_application_summary(applicationId, events):
    n_events = len(events)

    return {  "applicationId": applicationId, 
              "nEvents": n_events }
