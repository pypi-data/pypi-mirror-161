# coding: utf-8
"""Base logging gonfiguration."""

import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(name):
    """Set up base logger for package."""
    logger = logging.getLogger(name)
    handler = TimedRotatingFileHandler(filename='tabassist.log', when='D')
    formatter = logging.Formatter('%(asctime)s  (%(name)s): %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel('DEBUG')
    return logger
