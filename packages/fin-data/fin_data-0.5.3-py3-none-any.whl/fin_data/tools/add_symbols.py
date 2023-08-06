"""Add manually selected symbols or symbols from export files."""

import argparse
import asyncio

from fin_data.database import DBLoader
from fin_data.models.common import top_option_symbols_table
from ready_logger import logger


async def aioadd_top_option_symbols():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="File containing symbols that should be added.",
    )
    parser.add_argument("--symbols", "-s", type=str, nargs="*", help="Symbols to add.")
    args = parser.parse_args()

    symbols = set()
    if args.symbols:
        symbols.update(args.symbols)
    if args.file:
        with open(args.file, "r") as f:
            for r in f:
                symbols.add(r.strip())
    logger.info(f"Adding {len(symbols)} symbols.")

    if not len(symbols):
        return

    loader = await DBLoader.create(
        sa_obj=top_option_symbols_table, on_duplicate_key_update=False
    )

    rows = [{"symbol": symbol} for symbol in symbols]

    await loader.load(rows)


def add_top_option_symbols():
    asyncio.run(aioadd_top_option_symbols())
