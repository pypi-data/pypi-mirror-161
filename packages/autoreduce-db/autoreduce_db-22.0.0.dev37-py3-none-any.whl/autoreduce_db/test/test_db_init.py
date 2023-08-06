import os
from pathlib import Path
import subprocess

from autoreduce_db.autoreduce_django.settings import PROJECT_DEV_ROOT

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def test_migrate_default():
    """Tests the default migration location"""
    assert subprocess.check_call(["python", "autoreduce_db/manage.py", "migrate"], cwd=REPO_ROOT) == 0
    assert Path(PROJECT_DEV_ROOT, "sqlite3.db").exists()


def test_migrate_specific_location():
    """Test that migrating respects the location specified in AUTOREDUCTION_USERDIR"""
    expected_location = "/tmp/testsqlite3.db"
    custom_env = os.environ.copy()
    custom_env["AUTOREDUCTION_USERDIR"] = expected_location
    assert subprocess.check_call(["python", "autoreduce_db/manage.py", "migrate"], cwd=REPO_ROOT, env=custom_env) == 0
    expected = Path(PROJECT_DEV_ROOT, expected_location)

    assert expected.exists()
