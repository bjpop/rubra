'''Management of pipeline logging.'''

import ruffus.proxy_logger as proxy_logger
import logging
import os.path
from config import GLOBAL_PIPELINE_CONFIG

GLOBAL_PIPELINE_LOGGER = None

def init_log(options):
    log_dir = options.pipeline['log_dir']
    log_file = os.path.join(log_dir, options.pipeline['log_file'])
    mk_dir(log_dir)
    loggerArgs = {}
    loggerArgs["file_name"] = log_file
    loggerArgs["level"] = logging.DEBUG
    loggerArgs["rotating"] = False
    loggerArgs["maxBytes"] = 20000
    loggerArgs["backupCount"] = 10
    loggerArgs["formatter"] = "%(asctime)s - %(message)s"
    proxy, mutex = \
        proxy_logger.make_shared_logger_and_proxy(setup_std_shared_logger,
            "NGS_pipeline", loggerArgs)
    return {'proxy': proxy, 'mutex': mutex}

def log_info(msg, logger):
    with logger['mutex']:
        logger['proxy'].info(msg)

def start_logger():
    global GLOBAL_PIPELINE_LOGGER
    GLOBAL_PIPELINE_LOGGER = init_log(GLOBAL_PIPELINE_CONFIG)

def set_config(config):
    global GLOBAL_PIPELINE_CONFIG
    GLOBAL_PIPELINE_CONFIG = config

def finalize_drmaa_session():
    global GLOBAL_DRMAA_SESSION
    GLOBAL_DRMAA_SESSION.exit()
