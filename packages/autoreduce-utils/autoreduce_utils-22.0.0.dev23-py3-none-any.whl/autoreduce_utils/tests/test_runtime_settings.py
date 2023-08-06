import os
import sys
import shutil
import tempfile
import pytest

# pylint:disable=import-outside-toplevel


@pytest.fixture(autouse=True)
def clear_module():
    """
    Delete the "autoreduce_utils.settings" module from the ones currently imported in the interpreter runtime.
    This should allow each test to import it in a fresh state, recomputing the effect of environment vars.

    This is a hack. Don't use it in code outside of testing.
    """
    if "autoreduce_utils.settings" in sys.modules:
        del sys.modules["autoreduce_utils.settings"]


def test_autoreduce_home_root_default():
    """
    Tests the default value of AUTOREDUCE_HOME_ROOT, and that the dir exists
    """
    from autoreduce_utils.settings import AUTOREDUCE_HOME_ROOT, LOG_FILE, PROJECT_DEV_ROOT, \
        CEPH_DIRECTORY, ARCHIVE_ROOT, CYCLE_DIRECTORY, SCRIPTS_DIRECTORY
    assert ".autoreduce" in AUTOREDUCE_HOME_ROOT
    assert os.path.exists(AUTOREDUCE_HOME_ROOT)
    assert os.path.exists(PROJECT_DEV_ROOT)
    assert os.path.exists(os.path.dirname(LOG_FILE))
    assert AUTOREDUCE_HOME_ROOT in CEPH_DIRECTORY
    assert AUTOREDUCE_HOME_ROOT in ARCHIVE_ROOT
    assert AUTOREDUCE_HOME_ROOT in CYCLE_DIRECTORY
    assert AUTOREDUCE_HOME_ROOT in SCRIPTS_DIRECTORY


def test_autoreduce_home_root_env_var():
    """
    Tests whether the value of AUTOREDUCE_HOME_ROOT can be changed with the env var,
     and that the new dir gets made when imported
    """
    new_value = f"/tmp/{tempfile.TemporaryFile().name}"  # pylint: disable=consider-using-with
    os.environ["AUTOREDUCTION_USERDIR"] = new_value
    from autoreduce_utils.settings import AUTOREDUCE_HOME_ROOT, LOG_FILE, PROJECT_DEV_ROOT, \
        CEPH_DIRECTORY, ARCHIVE_ROOT, CYCLE_DIRECTORY, SCRIPTS_DIRECTORY
    assert AUTOREDUCE_HOME_ROOT == new_value
    assert os.path.exists(AUTOREDUCE_HOME_ROOT)
    assert os.path.exists(PROJECT_DEV_ROOT)
    assert os.path.exists(os.path.dirname(LOG_FILE))
    assert new_value in CEPH_DIRECTORY
    assert new_value in ARCHIVE_ROOT
    assert new_value in CYCLE_DIRECTORY
    assert new_value in SCRIPTS_DIRECTORY
    shutil.rmtree(new_value)


def test_log_level_default():
    """ Test the default log level """
    from autoreduce_utils.settings import LOG_LEVEL
    assert LOG_LEVEL == "INFO"


def test_log_level_env():
    """ Test that the env var configures the log level """
    os.environ["LOGLEVEL"] = "DEBUG"
    from autoreduce_utils.settings import LOG_LEVEL
    assert LOG_LEVEL == "DEBUG"


def test_pytest_env_var():
    """ Test running with the pytest env var. """
    os.environ["RUNNING_VIA_PYTEST"] = "1"
    from autoreduce_utils.settings import ARCHIVE_ROOT
    assert "test-archive" in ARCHIVE_ROOT


def test_no_pytest_env_var():
    """ Test running without the pytest env var """
    if "RUNNING_VIA_PYTEST" in os.environ:
        os.environ.pop("RUNNING_VIA_PYTEST")
    if "PYTEST_CURRENT_TEST" in os.environ:
        os.environ.pop("PYTEST_CURRENT_TEST")
    from autoreduce_utils.settings import ARCHIVE_ROOT
    assert "data-archive" in ARCHIVE_ROOT


def test_production_env_var():
    """
    Test running with production paths. Only used on production machines, or when contacting
    production queue/db for manual operations.
    """
    os.environ["AUTOREDUCTION_PRODUCTION"] = "1"
    from autoreduce_utils.settings import ARCHIVE_ROOT, CEPH_DIRECTORY
    assert "/isis" in ARCHIVE_ROOT
    assert "/instrument" in CEPH_DIRECTORY
