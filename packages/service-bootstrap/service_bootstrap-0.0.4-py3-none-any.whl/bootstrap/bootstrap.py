import logging
import os
import sys
import pytz

import tzlocal
import yaml

from datetime import datetime


def start_service():

    timezone = os.getenv('TIMEZONE', str(tzlocal.get_localzone()))

    def configure_default_logging():
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format="%(levelname)-8s | %(asctime)s | %(threadName)-25s | %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %z"
        )

        loglevels_from_file = dict()
        if os.path.exists("loglevels.yaml"):
            with open("loglevels.yaml", 'r') as f:
                loglevels_from_file = yaml.full_load(f)
        loglevels = {
            'apscheduler.scheduler': 'ERROR',
            'apscheduler.executors.default': 'WARN',
            **loglevels_from_file
        }
        for logger_name in loglevels:
            level = loglevels[logger_name]
            logging.getLogger(logger_name).setLevel(level)
        logging.Formatter.converter = lambda *args: datetime.now(tz=pytz.timezone(timezone)).timetuple()

    def configure_file_logging():
        from logging import config as logging_config
        with open("logging.yaml", 'r') as f:
            config = yaml.full_load(f)
            logging_config.dictConfig(config)

    if os.path.exists("logging.yaml"):
        configure_file_logging()
    else:
        configure_default_logging()

    logger = logging.getLogger("main")
    logger.info("Starting application!")
    logger.info("Your timezone is %s" % timezone)

    config_file = os.getenv('CONFIG', 'config/config.yaml')

    with open(config_file, 'r') as f:
        config = yaml.full_load(f)

    return config, logger, timezone
