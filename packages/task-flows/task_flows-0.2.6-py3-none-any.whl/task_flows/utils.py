import os
from functools import cache
from pathlib import Path
from subprocess import run

import sqlalchemy as sa
from ready_logger import get_logger
from sqlalchemy.engine import Engine

logger = get_logger("task-flows")
systemd_dir = Path.home() / ".config/systemd/user"


# TODO switch this to nullpool engine in class instance?
@cache
def get_engine(var_name="POSTGRES_URL") -> Engine:
    """Create an Sqlalchemy engine using a Postgresql URL from environment variable."""
    if not (url := os.getenv(var_name)):
        raise RuntimeError(
            f"Environment variable {var_name} is not set. Can not connect to database."
        )
    return sa.create_engine(url)


def systemctl(*args):
    run(["systemctl", "--user", *args])
