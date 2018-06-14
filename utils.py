import logging
import time


def config_logging():
    logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename="logs\log{}.log".format(time.strftime("%Y%m%d-%H%M%S")),
                            filemode='w')
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)