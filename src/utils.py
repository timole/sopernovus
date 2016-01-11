import logging


def log_config():
    logging.basicConfig(filename = "sopernovus.log", filemode='w', level=logging.DEBUG, 
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
