import json
import re
from collections import defaultdict
from pathlib import Path

from . import clean_company_info as cci

"""
def check_datetime(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (datetime, date)):
                data[k] = str(v)
            elif isinstance(v, (list, dict)):
                check_datetime(v)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, (datetime, date)):
                data[i] = str(v)
            elif isinstance(v, (list, dict)):
                check_datetime(v)
    elif isinstance(data, (datetime, date)):
        return str(data)
    return data
"""


def get_all_symbol_data(symbol, cur):
    symbol_data = defaultdict(dict)
    for table in symbol_tables:
        cur.execute(f"SELECT * FROM {table} WHERE symbol=%s", (symbol,))
        # remove unwanted columns and empty values.
        rows = [
            {
                col: re.sub("\s+", " ", str(val).strip())
                for col, val in row.items()
                if col not in {"created", "updated", "updates", "last_seen"}
            }
            and val not in (None, [], {})
            for row in cur.fetchall()
        ]
        rows = [
            {
                col: val
                for col, val in row.items()
                if val.lower() not in ("", "null", "unknown", "none")
            }
            for row in rows
        ]
        source_name = table.split(".")[-1]
        for i, row in enumerate(rows):
            source = f"{source_name}_{i}"
            for col, val in row.items():
                symbol_data[col][source] = val
    return symbol_data


def format_symbol_data(symbol, symbol_data):
    """
    map field to list of dicts where each dict has keys: 'value', 'sources', 'value_data'. (source and value_data are always list. each element in value_data is dict)
    """

    def pop_value(key):
        if key in symbol_data:
            return symbol_data.pop(key)

    formatted_data = {}
    if not symbol_data:
        return formatted_data
    company_names, security_names = cci.company_name_security_name(
        company_names=pop_value("name"), security_names=pop_value("security_name")
    )
    if company_names:
        formatted_data["company_name"] = company_names
    if security_names:
        formatted_data["security_name"] = security_names
    # check exchange from all sources.
    exchange = pop_value("exchange")
    if exchange:
        formatted_data["exchange"] = cci.format_exchange_name(exchange)
    # check symbol from all sources.
    symbol = pop_value("symbol")
    if symbol:
        formatted_data["symbol"] = cci.format_symbol(symbol)
    # check industry from all sources.
    industry = pop_value("industry")
    if industry:
        formatted_data["industry"] = cci.filter_substrings(industry)
    sector = pop_value("sector")
    if sector:
        formatted_data["sector"] = cci.filter_substrings(sector)
    website = pop_value("website")
    if website:
        formatted_data["website"] = cci.best_domain_url(website)
    ceo = pop_value("ceo")
    if ceo:
        formatted_data["ceo"] = cci.parse_human_name(ceo)
    phone = pop_value("phone")
    if phone:
        formatted_data["phone"] = cci.best_unique_phone_numbers(phone)
    country = pop_value("country")
    if country:
        formatted_data["country"] = cci.format_country(country)
    exchange_symbol = pop_value("exchange_symbol")
    if exchange_symbol:
        formatted_data["exchange_symbol"] = cci.format_symbol(exchange_symbol)
    business_address = pop_value("business_address")
    if business_address:
        formatted_data["business_address"] = cci.parse_street_address(business_address)
    mailing_address = pop_value("mailing_address")
    if mailing_address:
        formatted_data["mailing_address"] = cci.parse_street_address(mailing_address)
    state = pop_value("state")
    if state:
        formatted_data["state"] = cci.format_state(state)
    similar = pop_value("similar")
    if similar:
        formatted_data["similar"] = cci.combine_similar_symbols(similar)
    employees = pop_value("employees")
    if employees:
        formatted_data["employees"] = cci.get_employee_count(employees)
    full_time_employees = pop_value("full_time_employees")
    if full_time_employees:
        formatted_data["full_time_employees"] = cci.get_employee_count(
            full_time_employees
        )
    summary = pop_value("summary")
    if summary:
        formatted_data["summary"] = cci.get_summaries(summary)
    zipcode = pop_value("zip")
    if zipcode:
        formatted_data["zip"] = cci.filter_substrings(zipcode)
    tags = pop_value("tags")
    if tags:
        formatted_data["tags"] = cci.combine_tags(tags)
    sic = pop_value("sic")
    if sic:
        formatted_data["sic"] = cci.filter_substrings(sic)
    # add all remaining data.
    formatted_data.update(
        {field: list(sources.values()) for field, sources in symbol_data.items()}
    )
    """
    # convert all sets to list for JSON.
    formatted_data = {k: unique_flatten(v) if isinstance(
        v, (list, set)) else v for k, v in formatted_data.items()}
    """
    # unpack any one element lists.
    formatted_data = {
        k: v.pop() if isinstance(v, (list, set)) and len(v) == 1 else v
        for k, v in formatted_data.items()
    }
    return formatted_data


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pformat

    data = json.loads(Path("all.json").read_text())
    for t in ("TSLA", "GM", "AAPL", "GOOG"):
        print(f"PARSING: {t}")
        sym_data = data[t]
        Path(f"test/{t}.json").write_text(json.dumps(sym_data, indent=4))
        fmt_data = format_symbol_data(t, sym_data)
        Path(f"test/{t}.parsed.json").write_text(json.dumps(fmt_data, indent=4))

    """
    for f in Path('/home/dan/company_info_bots/test').iterdir():
        if 'parsed' not in f.name:
            data = json.loads(f.read_text())
            # try:
            fmt_data = format_symbol_data(f.stem, data)
            f.with_suffix('.parsed.json').write_text(
                json.dumps(fmt_data, indent=4))
            # except Exception as e:
            # print(f"ERROR: {e}. DATA: {pformat(data)}")
    """
