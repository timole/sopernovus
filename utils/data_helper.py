import pandas as pd
import logging
import pdb

logger = logging.getLogger(__name__)

def import_data(file_name):
    logger.info("Reading data from file " + file_name)
    df = pd.read_csv(file_name, parse_dates=['datetime'], sep = ';')
    df = df[df["municipalityId"].notnull()]
    df["municipalityId"] = df["municipalityId"].astype(int)
    df["userId"] = df["userId"].astype(int)
    logger.info("N of rows: {:.0f}".format(len(df)))
    df = df.sort_values(['applicationId', 'datetime'])
    return df

def import_operative_data(file_name):
    logger.info("Reading data from file " + file_name)
    df = pd.read_csv(file_name, parse_dates=['createdDate', 'submittedDate', 'sentDate', 'verdictGivenDate', 'canceledDate'], sep = ';')
    logger.info("N of rows: {:.0f}".format(len(df)))
    df = df.sort_values(['applicationId'])
    return df
