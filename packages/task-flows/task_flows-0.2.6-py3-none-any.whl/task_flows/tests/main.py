import os
from pathlib import Path

import pytest

if __name__ == "__main__":
    os.chdir("/home/dan/my-github-packages/task-flows/task_flows/tests")

    args = ["--sw", "-s", "-vv"]

    files = ["test_task.py"]

    for f in files:
        pytest.main(args + [f])
