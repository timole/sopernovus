import pandas as pd
import logging

logger = logging.getLogger(__name__)

def import_data(file_name):
    logger.debug("Parse CSV: " + file_name)
    df = pd.read_csv(file_name, parse_dates=['datetime'], sep = '\t')
    logger.debug("N of rows: {:.0f}".format(len(df)))
    return df
