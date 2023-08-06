import os
from pathlib import Path

import pytest

if __name__ == "__main__":
    os.chdir("/home/dan/my-github-packages/fin-data-db/fin_data/database/tests")

    args = ["--sw", "-s", "-vv"]

    files = [
        # "test_compare.py",
        "test_load.py",
        "test_load_sources.py",
        "test_data_id_creator.py",
        "test_filters.py",
    ]

    for f in files:
        pytest.main(
            args
            + [
                f,
                "--pg-url",
                os.environ["POSTGRESQL_URL"],
            ]
        )
