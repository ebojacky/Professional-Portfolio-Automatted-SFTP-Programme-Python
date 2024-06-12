# tools.py

import logging
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import paramiko.util
from pathlib import Path

import config


def create_directories(paths):
    try:
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logging.critical(str(e))


def setup_logging(log_name):
    log_file_name = f'{ichp_config.PATHS["LOG_PATH"]}/{log_name}'
    log_handler = TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=10)
    logging.basicConfig(level=logging.INFO, format=ichp_config.LOG_FORMAT, handlers=[log_handler])

    logging.info("Starting")


def write_paramiko_details():
    if ichp_config.DETAILED_SFTP_LOGS:
        paramiko.util.log_to_file(ichp_config.SFTP_LOG_PATH)


def get_recent_dates(period_in_days):
    return [datetime.strftime(datetime.today() - timedelta(days=i), '%Y%m%d')
            for i in range(period_in_days)
            ][::-1]
