from collections import defaultdict
from datetime import datetime

import sqlalchemy as sa
from ready_logger import get_logger

from fin_data.database import DBLoader

blacklist_table = sa.Table(
    "blacklist",
    sa.MetaData(),
    sa.Column("endpoint", sa.String, primary_key=True),
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("created", sa.DateTime(timezone=False), default=datetime.utcnow),
)


class BlackLister:
    logger = get_logger("BlackLister")

    @classmethod
    async def create(
        cls, max_bad_count: int = 4, max_bad_ratio: float = 0.7, **upserter_kwargs
    ) -> None:
        self = cls()
        self.max_bad_count = max_bad_count
        self.max_bad_ratio = max_bad_ratio
        self._total = defaultdict(int)
        self._bad = defaultdict(int)
        self._upserter = await DBLoader.create(
            sa_obj=blacklist_table, on_duplicate_key_update=False, **upserter_kwargs
        )
        return self

    def mark_ok(self, endpoint: str, symbol: str):
        self._total[(endpoint, symbol)] += 1

    async def mark_bad(self, endpoint: str, symbol: str) -> True:
        key = (endpoint, symbol)
        self._bad[key] += 1
        self._total[key] += 1
        if (
            bad_count := self._bad[key]
        ) >= self.max_bad_count and bad_count / self._total[key] >= self.max_bad_ratio:
            self.logger.warning(f"Blacklisting symbol: {symbol}, endpoint: {endpoint}")
            await self._upserter.load([{"endpoint": endpoint, "symbol": symbol}])
            return True
        return False
