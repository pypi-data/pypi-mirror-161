from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import as_declarative

SCHEMA_NAME = "company_info"
metadata = sa.MetaData(schema=SCHEMA_NAME)


class CompanyIDType(Enum):
    SYMBOL = "SYMBOL"
    CIK = "CIK"
    NAME = "NAME"


@as_declarative()
class CompanyInfo:
    __table_args__ = {"schema": SCHEMA_NAME}
    data_id = sa.Column(sa.String, primary_key=True)
    asset_id = sa.Column(sa.String)
    asset_id_type = sa.Column(
        ENUM(CompanyIDType, schema=SCHEMA_NAME), default=CompanyIDType.SYMBOL
    )


class NameType(Enum):
    COMPANY = "COMPANY"
    ASSET = "ASSET"
    UNKNOWN = "UNKNOWN"


class Name(CompanyInfo):
    __tablename__ = "name"
    name = sa.Column(sa.String)
    name_type = sa.Column(ENUM(NameType, schema=SCHEMA_NAME), default=NameType.UNKNOWN)


class Type(CompanyInfo):
    __tablename__ = "type"
    type = sa.Column(sa.String)


class CompanyFormerName(CompanyInfo):
    __tablename__ = "company_former_name"
    company_former_name = sa.Column(sa.String)


class CIK(CompanyInfo):
    __tablename__ = "cik"
    cik = sa.Column(sa.String, sa.CheckConstraint("cik ~ '\d{1,10}'", name="valid_cik"))


class SIC(CompanyInfo):
    __tablename__ = "sic"
    sic = sa.Column(sa.String)


class Tag(CompanyInfo):
    __tablename__ = "tag"
    tag = sa.Column(sa.String)


class Exchange(CompanyInfo):
    __tablename__ = "exchange"
    exchange = sa.Column(sa.String)


class IPODate(CompanyInfo):
    __tablename__ = "ipo_date"
    ipo_date = sa.Column(sa.DateTime(timezone=False))


class IPOPriceRange(CompanyInfo):
    __tablename__ = "ipo_price"
    price_range_low = sa.Column(sa.Float, sa.CheckConstraint("price_range_low > 0"))
    price_range_high = sa.Column(
        sa.Float, sa.CheckConstraint("price_range_high >= price_range_low")
    )


class DelistingDate(CompanyInfo):
    __tablename__ = "delisting_date"
    delisting_date = sa.Column(sa.DateTime(timezone=False))


class Status(CompanyInfo):
    __tablename__ = "status"
    status = sa.Column(sa.String)


class Currency(CompanyInfo):
    __tablename__ = "currency"
    currency = sa.Column(sa.String)


class CurrencySymbol(CompanyInfo):
    __tablename__ = "currency_symbol"
    currency_symbol = sa.Column(sa.String)


class Summary(CompanyInfo):
    __tablename__ = "summary"
    summary = sa.Column(sa.String)


class Sector(CompanyInfo):
    __tablename__ = "sector"
    sector = sa.Column(sa.String)


class Industry(CompanyInfo):
    __tablename__ = "industry"
    industry = sa.Column(sa.String)


class MarketCategory(CompanyInfo):
    __tablename__ = "market_category"
    market_category = sa.Column(sa.String)


class TestIssue(CompanyInfo):
    __tablename__ = "test_issue"


class Office(CompanyInfo):
    __tablename__ = "office"
    office = sa.Column(sa.String)


class FiscalYearEnd(CompanyInfo):
    __tablename__ = "fiscal_year_end"
    fiscal_year_end = sa.Column(sa.String)


class FullTimeEmployees(CompanyInfo):
    __tablename__ = "full_time_employees"
    full_time_employees = sa.Column(sa.String)


class CompanyOfficers(CompanyInfo):
    __tablename__ = "company_officers"
    company_officers = sa.Column(sa.String)


class Logo(CompanyInfo):
    __tablename__ = "logo"
    logo = sa.Column(sa.String)


class FIGI(CompanyInfo):
    __tablename__ = "figi"
    figi = sa.Column(sa.String)


class ShareClassFIGI(CompanyInfo):
    __tablename__ = "share_class_figi"
    share_class_figi = sa.Column(sa.String)


class Mic(CompanyInfo):
    __tablename__ = "mic"
    mic = sa.Column(sa.String)


##### LOCATION #####


class Country(CompanyInfo):
    __tablename__ = "country"
    country = sa.Column(sa.String)


class State(CompanyInfo):
    __tablename__ = "state"
    state = sa.Column(sa.String)


class StateOfInc(CompanyInfo):
    __tablename__ = "state_of_inc"
    state_of_inc = sa.Column(sa.String)


class City(CompanyInfo):
    __tablename__ = "city"
    city = sa.Column(sa.String)


class ZipCode(CompanyInfo):
    __tablename__ = "zip_code"
    zip_code = sa.Column(sa.String)


class BusinessAddress(CompanyInfo):
    __tablename__ = "business_address"
    business_address = sa.Column(sa.String)


class MailingAddress(CompanyInfo):
    __tablename__ = "mailing_address"
    mailing_address = sa.Column(sa.String)


##### Contact #####


class Phone(CompanyInfo):
    __tablename__ = "phone"
    phone = sa.Column(sa.String)


class Fax(CompanyInfo):
    __tablename__ = "fax"
    fax = sa.Column(sa.String)
