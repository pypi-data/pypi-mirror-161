import csv
import os
import random
from io import StringIO
from typing import Dict, List

from ready_logger import get_logger

logger = get_logger("fin-data")

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
]


def random_user() -> str:
    return random.choice(USER_AGENTS)


def get_redis_url():
    var = "REDIS_URL"
    if var not in os.environ:
        raise ValueError(
            f"Environmental variable {var} is not set. Can not connect to Redis."
        )
    return os.environ[var]


def load_csv_with_header(file_text: str) -> List[Dict[str, str]]:
    fo = StringIO(file_text)
    header = [c.strip() for c in next(csv.reader(fo))]
    return list(csv.DictReader(fo, fieldnames=header))


def user_header() -> Dict[str, str]:
    return {"User-Agent": "Danklabs.org. Open Source Data."}  # random_user()}
