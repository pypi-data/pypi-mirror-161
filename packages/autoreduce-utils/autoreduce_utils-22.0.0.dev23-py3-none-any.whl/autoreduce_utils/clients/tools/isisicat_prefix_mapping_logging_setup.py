# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
import logging
import logging.handlers

from autoreduce_utils.settings import LOG_FILE, LOG_LEVEL

LOGGING_LOC = LOG_FILE

logger = logging.getLogger(__package__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.RotatingFileHandler(LOGGING_LOC, maxBytes=104857600, backupCount=20)
handler.setLevel(LOG_LEVEL)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
