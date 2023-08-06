import pytest
from task_flows.admin import check_tables


@pytest.fixture
def tables():
    # TODO temp db.
    # TODO pg url.
    try:
        check_tables()
    except SystemExit:
        # command line tool will exit with exit(0)
        pass
