import logging

from logging.config import fileConfig


fileConfig("log.ini", disable_existing_loggers=False)
LOGGER = logging.getLogger('uvicorn.error')
LOGGER.setLevel(logging.DEBUG)