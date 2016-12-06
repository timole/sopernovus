import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

SESSION_THRESHOLD_IN_MINUTES = 15

def summarize_applications(df, odf, predictiveMode):
    """ Create a summary of the applications as a table. Presumes events are in datetime order
          * Count number of comments for different roles
    """

    n = 0

    summary = None

    df = df.sort_values(['applicationId', 'datetime'])
    numberOfApplications = df["applicationId"].nunique()

    uniqueActions = df["action"].unique()
    
    logger.info("Analyzing {} events with {} unique actions".format(len(df), len(uniqueActions)))

    applicationIds = df['applicationId'].unique()
    nTotal = len(applicationIds)
    for applicationId in applicationIds:
        n = n + 1
#        try:
        appInfo = odf[odf['applicationId'] == applicationId]
        if appInfo.empty:
            logger.debug("No operative data available for application (infoRequest) " + applicationId)
            continue

        appEvents = df[df['applicationId'] == applicationId]
        if predictiveMode:
            submitEvents = appEvents[appEvents.action == "submit-application"]
            if len(submitEvents) > 0:
                appEvents = appEvents.loc[:submitEvents.index[0]]
            else:
                appEvents = None

        if appEvents is not None:
            app = parse_application_summary(applicationId, appInfo.iloc[0].to_dict(), appEvents, uniqueActions)

            if summary is None:
                summary = pd.DataFrame(app, index = [0])
            else:
                summary.loc[len(summary)] = app

        if n % 1000 == 0:
            logger.info("Processed {}%".format( round( float(n) / nTotal * 100, 1)))
#        except:
#            logger.error("Unhandled exception with id {}".format(applicationId))


    if odf is not None:
        summary = pd.merge(summary, odf, on = 'applicationId')

    return summary

def parse_application_summary(applicationId, appInfo, events, uniqueActions):
    app = {    "applicationId": applicationId, 
                "events": len(events),
                "userIds": find_unique_users_by_application(events),
                "applicants": find_unique_users_by_application_and_role(events, 'applicant'),
                "applicantId": get_role_user_id(events, 'applicant', 0),
                "applicantId2": get_role_user_id(events, 'applicant', 1),
                "applicantIds": get_role_user_ids(events, 'applicant'),
                "authorityId": get_role_user_id(events, 'authority', 0),
                "authorityId2": get_role_user_id(events, 'authority', 1),
                "authorityIds": get_role_user_ids(events, 'authority'),
                "authorities": find_unique_users_by_application_and_role(events, 'authority'),
                "comments": len(find_events_by_action_and_target(events, 'add-comment', 'application')),
                "commentsApplicant": len(find_events_by_action_and_role_and_target(events, 'add-comment', 'applicant', 'application')),
                "commentsAuthority": len(find_events_by_action_and_role_and_target(events, 'add-comment', 'authority', 'application')),
                "invitesAuthority" : len(find_events_by_action_and_role(events,'invite-with-role','authority')),
                "invitesApplicant": len(find_events_by_action_and_role(events,'invite-with-role','applicant')),
                "sessionLength": count_session_length(events, SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthApplicant": count_session_length_by_role(events, 'applicant', SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthAuthority": count_session_length_by_role(events, 'authority', SESSION_THRESHOLD_IN_MINUTES),
                "nUpdateDocs": len(find_events_by_action(events, 'update-doc')),
                "nCreateDocs": len(find_events_by_action(events, 'create-doc')),
                "nUploadAttachments": len(find_events_by_action(events, 'upload-attachment')),
                "isApplicantLastNameFilled": len(find_events_by_action_and_target(events, 'update-doc', 'henkilo.henkilotiedot.sukunimi')) > 0,
                "isSubmitted": len(find_events_by_action(events, 'submit-application')) > 0,
                "hasVerdict": len(find_events_by_action(events, 'give-verdict')) > 0,
                "isCancelled": len(find_events_by_action(events, 'cancel-application')) > 0 or 
                                len(find_events_by_action(events, 'cancel-application-authority')) > 0,
                "leadTime": count_days(appInfo, 'createdDate', 'verdictGivenDate'),
                "leadTimeCreated2Submitted": count_days(appInfo, 'createdDate', 'submittedDate'),
                "leadTimeSubmitted2VerdictGiven": count_days(appInfo, 'submittedDate', 'verdictGivenDate'),
                "flowEfficiency": count_flow_efficiency(appInfo, events, 'createdDate', 'verdictGivenDate'),
                "flowEfficiencyCreated2Submitted": count_flow_efficiency(appInfo, events, 'createdDate', 'submittedDate'),
                "flowEfficiencySubmitted2VerdictGiven": count_flow_efficiency(appInfo, events, 'submittedDate', 'verdictGivenDate')
            }

#    include_number_of_unique_actions(app, events, uniqueActions)
    return app

def include_number_of_unique_actions(app, events, uniqueActions):
    for action in uniqueActions:
        fieldName = "n-" + action
        app[fieldName] = len(find_events_by_action(events, action))

def get_role_user_id(events, role, index):
    vc = find_userId_value_counts_by_role(events, role)

    if index > (len(vc) - 1):
        return None
    else:
        return vc.sort_values(ascending = False).index[index]

def find_userId_value_counts_by_role(events, role):
    result = events[events['role'] == role]
    return result.userId.value_counts()

def get_role_user_ids(events, role):
    result = events[events['role'] == role]
    val = ""
    for id in result.userId.unique():
        if len(val) > 0:
            val = val + ','
        val = val + str(id)
    return val

def find_unique_users_by_application(events):
    return events.userId.nunique()

def find_unique_users_by_application_and_role(events, role):
    result = events[events['role'] == role]
    return result.userId.nunique()

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
        return timeBetween.days + 1
    else:
        return None

def count_days(app, fromDate, tillDate):
    delta = app[tillDate] - app[fromDate]

    if pd.isnull(delta):
        return None
    else:
        return int(delta.days + 1)

def count_flow_efficiency(app, events, fromDate, tillDate):
    days = count_days(app, fromDate, tillDate)
    if days is None or days <= 0:
        return None

    activeDates = events['datetime'].dt.normalize()
    activeDates = activeDates[activeDates >= app[fromDate].normalize()]
    activeDates = activeDates[activeDates <= app[tillDate].normalize()]

    nOfProcessedDays = len(activeDates.unique())
    flowEfficiency = int(round(float(nOfProcessedDays) / days, 2) * 100)

    return flowEfficiency
