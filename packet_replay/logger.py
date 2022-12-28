"""
 # @ Author: zzsuki
 # @ Create Time: 2020-11-24 13:50:42
 # @ Modified by: zzsuki
 # @ Modified time: 2020-11-24 13:50:45
 # @ Description:
"""
import logging


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    FORMAT = "[%(asctime)s: %(filename)s - line %(lineno)s - %(funcName)5s() ] %(message)s"
    formatter = logging.Formatter(FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
