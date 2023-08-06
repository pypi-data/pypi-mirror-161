import re
from pathlib import Path

from fin_data.utils import load_csv_with_header

iso_mic = load_csv_with_header(
    Path(__file__).parent.joinpath("data/ISO10383_MIC.csv").read_text()
)
mic_to_exchange = {r["MIC"]: r["NAME-INSTITUTION DESCRIPTION"] for r in iso_mic}
mic_to_exchange.update(
    {r["OPERATING MIC"]: r["NAME-INSTITUTION DESCRIPTION"] for r in iso_mic}
)


exchange_name_regs = [
    (r"NASDAQ[\s\-\/]*\(?(CAPITAL MARKET|CM)\)?", "NASDAQ (CAPITAL MARKET)"),
    (r"NASDAQ[\s\-\/]*\(?(Global Market|GM)\)?", "NASDAQ (GLOBAL MARKET)"),
    (
        r"NASDAQ[\s\-\/]*\(?NMS\)?[\s\-\/]*\(?(Global Market|GM)\)?",
        "NASDAQ NMS (GLOBAL MARKET)",
    ),
    (r"NMS", "NASDAQ NMS"),
    (
        r"NASDAQ[\s\-\/]*(\(?NGS\)?)?[\s\-\/]*\(?(GLOBAL SELECT( MARKET)?|GS)\)?",
        "NASDAQ (GLOBAL SELECT MARKET)",
    ),
    (re.escape("https://api.robinhood.com/markets/XNAS/"), "NASDAQ"),
    (re.escape("https://api.robinhood.com/markets/XNYS/"), "NYSE"),
    (r"New York Stock Exchange(,? ((Inc.?|Incorporated)|\(?NYSE\)?))?", "NYSE"),
    (r"Cboe BZX US Equities Exchange", "CBOE BZX U.S. EQUITIES EXCHANGE"),
]
exchange_name_regs = [(re.compile(k, re.IGNORECASE), v) for k, v in exchange_name_regs]


def exchange_name(name: str) -> str:
    # check if name is a MIC code.
    if name in mic_to_exchange:
        return mic_to_exchange[name]
    for reg, formatted_name in exchange_name_regs:
        if reg.match(name):
            return formatted_name
    return name
