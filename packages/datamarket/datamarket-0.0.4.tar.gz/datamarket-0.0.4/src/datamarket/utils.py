########################################################################################################################
# IMPORTS

import configparser
import logging
import random
import time


########################################################################################################################
# FUNCTIONS


def get_config(config_path):
    cfg = configparser.RawConfigParser()
    cfg.read(config_path)
    return cfg


def set_logger(level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(level.upper())
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def ban_sleep(max_time, min_time=0):
    time.sleep(random.uniform(min_time, max_time))
