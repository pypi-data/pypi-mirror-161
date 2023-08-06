# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
"""
Settings for connecting to the test services that run locally
"""
import os
import logging
import logging.handlers
import sys

FACILITY = 'ISIS'

AUTOREDUCE_HOME_ROOT = os.environ.get("AUTOREDUCTION_USERDIR", os.path.expanduser("~/.autoreduce"))

############################################## Logging ##############################################
os.makedirs(os.path.join(AUTOREDUCE_HOME_ROOT, "logs"), exist_ok=True)

LOG_LEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
LOG_FILE = os.path.join(AUTOREDUCE_HOME_ROOT, 'logs', 'autoreduce.log')

rotating_file_handler = logging.handlers.RotatingFileHandler(filename=LOG_FILE, maxBytes=209715200, backupCount=5)
stream_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    datefmt="%d/%b/%Y %H:%M:%S",
                    level=LOG_LEVEL,
                    handlers=[rotating_file_handler, stream_handler])

#####################################################################################################

PROJECT_DEV_ROOT = os.path.join(AUTOREDUCE_HOME_ROOT, "dev")
os.makedirs(PROJECT_DEV_ROOT, exist_ok=True)

# The reduction outputs are copied here on completion. They are saved in /tmp/<randomdir>
# as the reduction is running. By default the output is also saved locally
# unless AUTOREDUCTION_PRODUCTION is specified
CEPH_DIRECTORY = f"{PROJECT_DEV_ROOT}/reduced-data/%s/RBNumber/RB%s/autoreduced/%s/"
MANTID_PATH = "/tmp/Mantid/lib"
AUTOREDUCE_API_URL = os.getenv('AUTOREDUCE_API_URL', "http://127.0.0.1:8001/api")

if "AUTOREDUCTION_PRODUCTION" in os.environ:
    # for when deploying on production - this is the real path where the mounts are
    ARCHIVE_ROOT = "\\\\isis\\inst$\\" if os.name == "nt" else "/isis"
    CEPH_DIRECTORY = "/instrument/%s/RBNumber/RB%s/autoreduced/%s"
    MANTID_PATH = "/opt/Mantid/lib"
    AUTOREDUCE_API_URL = os.getenv('AUTOREDUCE_API_URL', "https://reduce.isis.cclrc.ac.uk/api")
elif "RUNNING_VIA_PYTEST" in os.environ or "PYTEST_CURRENT_TEST" in os.environ:
    # For testing which uses a local folder to simulate an archive. It's nice for this
    # to be different than the development one, otherwise running the tests will delete
    # any manual changes you've done to the archive folder, e.g. for testing reduction scripts
    ARCHIVE_ROOT = os.path.join(PROJECT_DEV_ROOT, 'test-archive')
else:
    # the default development path
    ARCHIVE_ROOT = os.path.join(PROJECT_DEV_ROOT, 'data-archive')

# The path is structured as follows. The %s fill out the instrument name and the cycle number
CYCLE_DIRECTORY = os.path.join(ARCHIVE_ROOT, 'NDX%s', 'Instrument', 'data', 'cycle_%s')
SCRIPTS_DIRECTORY = os.path.join(ARCHIVE_ROOT, "NDX%s", "user", "scripts", "autoreduction")

SCRIPT_TIMEOUT = 3600  # The max time to wait for a user script to finish running (seconds)
TEMP_ROOT_DIRECTORY = "/autoreducetmp"
