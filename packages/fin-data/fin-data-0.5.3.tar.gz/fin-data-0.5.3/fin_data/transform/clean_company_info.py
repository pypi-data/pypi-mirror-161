import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Union
from urllib.parse import urlparse

"""
import cleanco
from nameparser import HumanName
from postal.parser import parse_address

from ready_logger import logger


cleanco_terms = cleanco.prepare_terms()
cleanco_typesources = cleanco.typesources()
cleanco_countrysources = cleanco.countrysources()
"""


source_map = {
    "alphavantage_": "Alpha Vantage (OVERVIEW)",
    "alphavantage_listing_status_": "Alpha Vantage (LISTING_STATUS)",
    "finnhub_": "Finnhub (profile2)",
    "finnhub_symbols_": "Finnhub (symbol)",
    "iexcloud_": "IEX Cloud (company)",
    "nasdaq_nasdaqlisted_": "NASDAQ (nasdaqlisted.txt)",
    "nasdaq_otherlisted_": "NASDAQ (otherlisted.txt)",
    "nyse_": "NYSE (nyse.com)",
    "polygon_": "Polygon (company)",
    "sec_company_json_": "SEC (company_tickers.json)",
    "sec_company_search_": "SEC (company search)",
    "sec_ticker_txt_": "SEC (ticker.txt)",
    "yahoo_finance_": "Yahoo Finance",
}

data_dir = Path(__file__).parent / "data"


def format_sources(sources: List[str]):
    if not isinstance(sources, (list, set, tuple)):
        sources = [sources]
    sources = [source_map[re.sub(r"\d+$", "", source)] for source in sources]
    if len(sources) == 1:
        return sources.pop()
    return sources


def unique_flatten(values, out=None):
    if out is None:
        out = []
    for val in values:
        if isinstance(val, list):
            unique_flatten(val, out)
        elif val not in out:
            out.append(val)
    return out


def capitalize_words(text: str) -> str:
    words = [w.lower() for w in text.split()]
    return " ".join([w.capitalize() for w in words if w != "of"])


# load country name and abbreviations. map to formatted name.
country_names = {"usa": "United States (US)"}
"""
with data_dir.joinpath("countries.csv").open(mode="r") as i:
    for row in csv.reader(i):
        name, abrv = row
        fmt_name = f"{name} ({abrv})"
        country_names[name.lower()] = fmt_name
        country_names[abrv.lower()] = fmt_name
"""


def format_country(source_countries: Dict[str, str]):
    "Check that all names in provided {countries} list are variations of the same name and return properly formatted name."
    country_sources = defaultdict(set)
    for source, country in source_countries.items():
        if not isinstance(country, list):
            country = [country]
        for c in country:
            country_sources[country_names[c.lower()]].add(source)
    return {
        country: format_sources(sources) for country, sources in country_sources.items()
    }


# load country name and abbreviations. map to formatted name.
state_names = {}
"""
with data_dir.joinpath("states.csv").open(mode="r") as i:
    for row in csv.reader(i):
        name, abrv = row
        fmt_name = f"{name} ({abrv})"
        state_names[name.lower()] = fmt_name
        state_names[abrv.lower()] = fmt_name
"""


def format_state(source_states: List[str]) -> str:
    "Check that all names in provided {states} list are variations of the same name and return properly formatted name."
    state_sources = defaultdict(set)
    for source, state in source_states.items():
        state_sources[state_names[state.lower()]].add(source)
    return {state: format_sources(sources) for state, sources in state_sources.items()}


def filter_substrings(source_strings: Union[List[Tuple[str]], Dict[str, str]]):
    "return strings in list that are not a substring of any other string in the list. (case insensitive)"
    if isinstance(source_strings, dict):
        source_strings = list(source_strings.items())
    # map original formatted string to a filtered representation that can be used for fuzzy matching.
    source_strings = [
        (source, string, re.sub(r"(^[a-zA-Z0-9]|and|or)", "", string))
        for source, string in source_strings
    ]
    # sort strings by length (longest to shortest) so substring checks will be done in the right order.
    source_strings.sort(key=lambda t: len(t[1]), reverse=True)
    # keep strings that are not a substring of any longer string.
    source_strings_fmt = defaultdict(set)
    for i, (source, string, filtered_string) in enumerate(source_strings):
        if not any(
            re.search(f"(?i){filtered_string}", longer_string[2])
            for longer_string in source_strings[:i]
        ):
            source_strings_fmt[string].add(source)
    return {
        string: format_sources(sources)
        for string, sources in source_strings_fmt.items()
    }


def add_substring_keys(d: Dict[str, Set[str]]):
    combined = defaultdict(set)

    def combined_key(k):
        for lk in combined.keys():
            if re.search(f"(?i){k}", lk):
                return lk
        return k

    d = sorted(d.items(), key=lambda i: len(i[0]), reverse=True)
    for k, v in d:
        combined[combined_key(k)].update(v)


def best_unique_phone_numbers(source_numbers: Dict[str, str]):
    numbers = defaultdict(set)

    def number_key(number):
        filtered_number = re.sub(r"[^\d]", "", number)
        # if filtered number is substring of existing number key, use that key.
        for existing_key in numbers.keys():
            if re.search(f"(?i){filtered_number}", existing_key):
                return existing_key
        return filtered_number

    number_sources = defaultdict(set)
    for source, number in sorted(source_numbers.items(), key=lambda n: len(n[1])):
        key = number_key(number)
        numbers[key].add(number)
        number_sources[key].add(source)
    # find the longest (i.e. most formatted) number ofr each filtered number.
    num_to_sources = {}
    for key, nums in numbers.items():
        best_num = sorted(nums, key=lambda n: len(n))[-1]
        num_to_sources[best_num] = number_sources[key]
    return {
        number: format_sources(sources) for number, sources in num_to_sources.items()
    }


def parse_human_name(source_names: List[str]):
    def build_full_name(names_parsed):
        names_parsed = {
            key: set(name[key] for name in names_parsed if key in name)
            for key in ("title", "first", "middle", "last", "suffix")
        }
        name_parts = []
        # check for title.
        if len(names_parsed["title"]):
            if len(names_parsed["title"]) > 1:
                logger.error(f"More than one title found: {names_parsed['title']}")
            name_parts.append(("title", "/".join(names_parsed["title"])))
        # add first name.
        name_parts.append(("first", names_parsed["first"].pop()))
        # check for middle name.
        if len(names_parsed["middle"]) == 1:
            name_parts.append(("middle", names_parsed["middle"].pop()))
        elif len(names_parsed["middle"]) > 1:
            # sort shortest to longest.
            middle = sorted(names_parsed["middle"], key=lambda n: len(n))
            # check if shortest is initial and longest is actual name.
            if re.match(r"[A-Z]\.?$", middle[0]) and middle[-1].startswith(
                middle[0][0]
            ):
                # add complete middle name (not initial)
                name_parts.append(middle[-1])
            else:
                logger.error(f"Conflicting middle name: {middle}")
                name_parts.append("/".join(middle))
        # add last name.
        name_parts.append(("last", names_parsed["last"].pop()))
        # join name parts into name string.
        formatted_name = " ".join([p[1].capitalize() for p in name_parts])
        # convert name_parts list to dict.
        return formatted_name, dict(name_parts)

    names = [
        (source, HumanName(name.lower()).as_dict())
        for source, name in source_names.items()
    ]
    names = [
        (source, {k: v for k, v in name.items() if v != ""}) for source, name in names
    ]
    fl_to_full, fl_sources = defaultdict(set), defaultdict(set)
    for source, name in names:
        fl = (name["first"], name["last"])
        fl_to_full[fl].add(tuple(name.items()))
        fl_sources[fl].add(source)
    names_data = []
    for fl, parsed_names in fl_to_full.items():
        parsed_names = [dict(name) for name in parsed_names]
        formatted_name, name_parts = build_full_name(parsed_names)
        sources = fl_sources[fl]
        # TODO unpack name parts?
        names_data.append(
            {
                "formatted_name": formatted_name,
                "name_parts": name_parts,
                "sources": format_sources(sources),
            }
        )
    return names_data


def parse_street_address(source_addrs: Dict[str, str]):
    key_to_addr = {}

    def get_key(parsed_addr, addr):
        for key in key_to_addr.keys():
            if all(t in parsed_addr for t in key):
                return key
        key_to_addr[parsed_addr] = addr
        return parsed_addr

    source_addrs_data = []
    for source, addrs in source_addrs.items():
        if not isinstance(addrs, list):
            addrs = [addrs]
        for addr in addrs:
            source_addrs_data.append((source, addr, tuple(parse_address(addr))))
    # primary sort by number of components in pasted address, secondary sort by length of original address text.
    source_addrs_data.sort(key=lambda t: (len(t[2]), len(t[1])))
    addr_sources = defaultdict(set)
    for source, addr, parse_addr in source_addrs_data:
        key = get_key(parse_addr, addr)
        addr_sources[key].add(source)
    return [
        {
            "sources": format_sources(addr_sources[parse_addr]),
            "address_components": {v: k for k, v in parse_addr},
            "address": addr,
        }
        for parse_addr, addr in key_to_addr.items()
    ]


def best_domain_url(source_urls: Dict[str, str]) -> Dict[str, str]:
    "Get best/most formatted URL for each domain in list."
    domain_urls, domain_sources = defaultdict(set), defaultdict(set)
    for source, url in source_urls.items():
        # remove trailing /
        url = url.rstrip("/")
        filtered_url = re.sub(r"(https?:\/\/)?(www\.)?", "", url)
        domain_urls[filtered_url].add(url)
        domain_sources[filtered_url].add(source)
    # assume longest URL has most formatting (i.e scheme, etc)
    domain_best_url = {
        filtered_url: sorted(urls, key=lambda u: len(u))[-1]
        for filtered_url, urls in domain_urls.items()
    }
    return {
        url: format_sources(domain_sources[filtered_url])
        for filtered_url, url in domain_best_url.items()
    }


def get_summaries(source_summaries: Dict[str, str]):
    summary_sources = defaultdict(set)
    for source, summary in source_summaries.items():
        summary_sources[summary.strip()].add(source)
    return {
        summary: format_sources(sources) for summary, sources in summary_sources.items()
    }


def format_symbol(source_symbols: Dict[str, str]) -> Dict[str, str]:
    source_symbols = {
        source: symbol.upper() for source, symbol in source_symbols.items()
    }
    symbol_sources = defaultdict(set)
    for source, symbol in source_symbols.items():
        symbol_sources[symbol].add(source)
    return {
        symbol: format_sources(sources) for symbol, sources in symbol_sources.items()
    }


def combine_similar_symbols(source_symbol_lists: Dict[str, List[List[str]]]) -> str:
    symbol_sources = defaultdict(set)
    for source, symbol_lists in source_symbol_lists.items():
        if not isinstance(symbol_lists, list):
            symbol_lists = [symbol_lists]
        for symbol_list in symbol_lists:
            symbol_list = [s.upper().strip() for s in symbol_list]
            for s in symbol_list:
                symbol_sources[s].add(source)
    return {
        symbol: format_sources(sources) for symbol, sources in symbol_sources.items()
    }


def check_business_status():
    # check that google places address is same as address for ticker.
    pass


def capitalized_ratio(text: str) -> float:
    "Get fracion for words in text that are capitalized."
    cap_word_count = 0
    words = text.split(" ")
    for word in words:
        if len(word) == 1 and word == word.upper():
            cap_word_count += 1
        elif re.search("^[A-Z][a-z]", word) is not None:
            cap_word_count += 1
    return cap_word_count / len(words)


security_name_common_terms = [
    r" CUMULATIVE($|[^a-z])",
    r" REDEEMABLE($|[^a-z])",
    r" PFD($|[^a-z])",
    r" SERIES($|[^a-z])",
    r" A($|[^a-z])",
    r" B($|[^a-z])",
    r" C($|[^a-z])",
    r" (Capital|Common) (Stock|Shares)",
    " Beneficial Interest",
    "- Warrants",
    "- Units",
    r" Ord($|[^a-z])",
    r" UNIT($|[^a-z])",
    r"\d\.\d+%",
    r" - Class($|[^a-z])",
    r"\d{4}[^\d]\d{2}[^\d]\d{2}",
]
security_name_common_terms = [
    re.compile(r, re.IGNORECASE) for r in security_name_common_terms
]


def company_name_security_name(
    company_names: Dict[str, str], security_names: Dict[str, str]
):
    def best_formated_name(names: List[Dict[str, str]]):
        "Want longest name and also properly capitalized name."
        # score each source name.
        scores = [0] * len(names)
        # find word count of each name.
        word_counts = [name["name"].count(" ") for name in names]
        # get max word count for normalizing word counts.
        max_word_count = max(word_counts)
        if max_word_count > 0:
            scores = [
                score + (word_count / max_word_count)
                for word_count, score in zip(word_counts, scores)
            ]
        # find fraction of capitalized words in each name.
        cap_ratios = [capitalized_ratio(name["name"]) for name in names]
        # get max capitalized ratio for normalizeing capitalized ratios.
        max_cap_ratio = max(cap_ratios)
        if max_cap_ratio > 0:
            scores = [
                score + (cap_ratio / max_cap_ratio)
                for cap_ratio, score in zip(cap_ratios, scores)
            ]
        # round scores for approximate comparison.
        scores = [round(score, 1) for score in scores]
        # return longest name with highest score. longest name should have most formatting etc.
        highest_score = max(scores)
        # primary sort on score value, secondary sort on name length.
        return sorted(zip(names, scores), key=lambda t: (t[1], len(t[0]["name"])))[-1][
            0
        ]

    def best_unique_names(names: List[str]):
        # map (filtered name, legal_type) to original name data.
        names_data = defaultdict(list)
        for name in names:
            names_data[(name["name_no_legal_type"].lower(), name["legal_type"])].append(
                name
            )
        return [
            best_formated_name(name_list) if len(name_list) > 1 else name_list.pop()
            for name_list in names_data.values()
        ]

    # combine company names and security names as "company names" are often security names.
    source_names = []
    if company_names:
        source_names.extend(company_names.items())
    if security_names:
        source_names.extend(security_names.items())
    # parse name data.
    names = [
        {
            "name": re.sub(r"\s+", " ", name).strip(),
            "source": format_sources(source),
            "name_no_legal_type": cleanco.basename(
                name, cleanco_terms, prefix=False, middle=False, suffix=True
            ),
            "legal_type": ", ".join(cleanco.matches(name, cleanco_typesources)),
            "legal_type_countries": ", ".join(
                set(cleanco.matches(name, cleanco_countrysources))
            ),
        }
        for source, name in source_names
    ]

    # sort names based on whether they are security names or compnay names.
    security_names, company_names = [], []
    for name in names:
        if any(
            re.search(r, name["name"]) is not None for r in security_name_common_terms
        ):
            security_names.append(name)
        else:
            company_names.append(name)
    if len(security_names) > 1:
        security_names = best_unique_names(security_names)
    if len(company_names) > 1:
        company_names = best_unique_names(company_names)
    for l in (security_names, company_names):
        for d in l:
            del d["name_no_legal_type"]
    return company_names, security_names


def add_integer_commas(number):
    if not isinstance(number, int):
        try:
            number = int(number.strip())
        except Exception as e:
            logger.error(f"Could not convert number str to int: {e}")
            return number
    return "{:,}".format(number)
