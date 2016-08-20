import pandas as pd
import logging
import pdb

logger = logging.getLogger(__name__)

def import_data(file_name):
    logger.debug("Parse CSV: " + file_name)
    df = pd.read_csv(file_name, parse_dates=['datetime'], sep = ';')
    df["municipalityId"] = df["municipalityId"].astype(int)
    df["userId"] = df["userId"].astype(int)
    logger.debug("N of rows: {:.0f}".format(len(df)))
    df = df.sort(['applicationId', 'datetime'])
    return df

def import_operative_data(file_name):
    logger.debug("Parse CSV: " + file_name)
    df = pd.read_csv(file_name, parse_dates=['createdDate', 'submittedDate', 'sentDate', 'verdictGivenDate', 'canceledDate'], sep = ';')
    logger.debug("N of rows: {:.0f}".format(len(df)))
    df = df.sort(['applicationId'])
    return df
