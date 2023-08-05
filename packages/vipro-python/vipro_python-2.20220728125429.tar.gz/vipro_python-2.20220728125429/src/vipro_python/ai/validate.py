import pandas
import re
import dateutil.parser

valid_authorities=['Basildon', 'Braintree', 'Brentwood', 'CastlePoint', 'Chelmsford', 'Colchester', 'EppingForest', 'EssexCounty', 'Harlow', 'Maldon', 'Rochford', 'Southend', 'Tendring', 'Thurrock', 'Uttlesford']
fields_global = ['@timestamp', 'authority', 'address_id', 'source.uri', 'full_address', 'lookup_id']
fields_children_schema = ['forename', 'surname', 'school.name']
fields_residents_schema = ['forename', 'surname']
fields_companies_schema = ['company_name', 'sbrr.active', 'sbrr.amount']
fields_children_dates = ['@timestamp', 'school.meta.entryDate']
always_for_surnames = ['NACRO', 'NOTTING HILL GENESIS', 'PASSMORES ACADEMY', 'SUPPORTWORKS', 'STREETS2HOMES', 'LIVABILITY']
company_words = ['GROUP', 'LTD', 'LIMITED', 'BOARD', 'SOCIETY', 'SOLUTIONS', 'SYSTEMS', 'CONSULTING', 'DEVELOPMENT', 'PROPERTIES', 'ESTATE', 'TRUST', 'PLC', 'COUNCIL', 'BRENTWOOD', 'CHELMSFORD', 'BASILDON', 'ASSOCIATION', 'HOUSING', 'MOSAIC', 'HARVEST', 'AND CARE', 'CARE HOMES', 'AGENCY', 'LLP', 'BOROUGH', '&', 'LETTINGS', 'SERVICE', 'HOLDINGS', 'WINE BAR', 'SOUTH EAST', 'UK OUTREACH', 'CORPORATION', 'CHARITABLE CORP', 'CENTRE', 'CHURCH', 'HOSPITAL', 'METALTECH', 'CARE NHS', 'TEMPLE OF', 'MAYOR', 'AUCTION SALE', 'ELECTRONICS', 'SOCIAL CLUB', 'BUTCHER', 'INTERNATIONAL', 'TRADING', 'HOMES', 'SCHOOL', 'NHS ', 'MANAGEMENT', 'GREENE KING', 'PARISH', 'CHARITIES', 'CHARITY', 'EVANGELIST', 'CO.', 'HOUSE ESSEX', 'ENGLAND', 'COMMUNITY', 'OF DEFENCE', 'INSTITUTION', 'PARTNERSHIP', 'NURSING HOME', 'FOUNDATION', 'RECREATION', 'CLUB', 'LIMTED', 'TEAM', 'MENTAL HEALTH', 'CHEMIST', 'PLACES', 'WORKS', 'OF THE', 'HOTEL', 'MEMORIAL', 'COMPANY', 'RESIDENTIAL']

def children(df):
    return df.apply(lambda x: series(x, fields_children_schema, fields_children_dates), axis=1)

def residents(df):
    return df.apply(lambda x: series(x, fields_residents_schema, fields_children_dates), axis=1)

def companies(df):
    return df.apply(lambda x: series(x, fields_companies_schema, fields_children_dates), axis=1)

def is_company(series):
    return series.map(lambda x: False if pandas.isna(x) else contains_company_word(x))

def contains_company_word(name):
    uname = name.upper()
    if uname in always_for_surnames:
        return True
    for word in company_words:
        if ' {}'.format(word) in uname:
            #print('detected word {} in {}'.format(word, uname))
            return True
    return False

def series(series, fields_schema, fields_dates):
    series_for(series, fields_global, 'global')
    series_for(series, fields_schema, 'domain-specific')
    series_dates(series, fields_dates)

def series_for(series, fields, category):
    for field in fields:
        if field not in series:
            raise Exception('missing field {}, category={}'.format(field, category))
        if isinstance(series[field], list):
            continue
        if pandas.isna(series[field]):
            raise Exception('empty value in field {}, category={}, series={}'.format(field, category, series))
        if field == 'authority' and series[field] not in valid_authorities:
            raise Exception('authority "{}" was not recognised, category={}, series={}'.format(series[field], category, series))
        if field == 'surname':
            if re.search(r'\s+deceased', series[field], flags=re.IGNORECASE):
                raise Exception('{} contains deceased flag, category={}, series={}'.format(field, category, series))
        if field in ['lookup_id', 'address_id']:
            if re.search(r'^[@•]', series[field], flags=re.IGNORECASE):
                raise Exception('{} contains • or @ prefix, category={}, series={}'.format(field, category, series))
        if field in ['dob', 'meta.startDate', 'meta.endDate', 'ctd.startDate', 'ctd.endDate']:
            if not pandas.isna(series[field]):
                if series[field].find('T') == -1 or series[field].find('/') == -1 or series[field].find(':') == -1:
                    raise Exception('{} contains a datetime but not in iso format, category={}, series={}'.format(field, category, series))

def series_dates(series, date_fields):
    for field in date_fields:
        if field in series:
            val = series[field]
            if not pandas.isna(val):
                dateutil.parser.isoparse(val)