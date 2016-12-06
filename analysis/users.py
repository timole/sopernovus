import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def summarize_users(df):
    """ Create a summary of the applications as a table. Presumes events are in datetime order
          * Count number of comments for different roles
    """

    n = 0

    summary = None

    df = df.sort_values(['userId', 'datetime'])
    numberOfUsers = df["userId"].nunique()

    userIds = df['userId'].unique()
    nTotal = len(userIds)
    for userId in userIds:
        n = n + 1
        try:
            user = parse_user_summary(userId, df[df['userId'] == userId])

            if summary is None:
                summary = pd.DataFrame(user, index = [0])
            else:
                summary.loc[len(summary)] = user

            if n % 100 == 0:
                logger.info("Processed {}%".format( round( float(n) / nTotal * 100, 1)))

        except:
            logger.error("Unhandled exception with user id {}".format(userId))

    return summary

def parse_user_summary(userId, events):
    user = {    "userId": userId, 
                "applicantRoles": len(events[events['role'] == 'applicant']['applicationId'].unique()),
                "authorityRoles": len(events[events['role'] == 'authority']['applicationId'].unique())
            }

    return user

