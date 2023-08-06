import re 
import pandas
import jellyfish
from datetime import datetime

def common(series):
    return series.str.replace(r'\s+deceased', '', flags=re.IGNORECASE) \
        .str.replace(r'^\.+', '', regex=True) \
        .str.strip() \
        .str.title()

def id_common(series):
    return series.str.upper() \
        .str.replace("'", '') \
        .str.replace(r'\(((Flat|Unit).*)\)', r'\1', flags=re.IGNORECASE, regex=True) \
        .str.replace(r'^(\d{1,5}?\s*)\((.*)\)', r'\1\2', flags=re.IGNORECASE, regex=True) \
        .str.replace(r'^\((.*)\)', r'\1', regex=True) \
        .str.replace(r'\(.*\)', '', regex=True) \
        .str.replace(r'[^A-Z\d\s@•]+', '', regex=True) \
        .str.strip()

def forename(series):
    return common(series) \
        .str.replace(r'\s+[A-Z]$', '', regex=True, flags=re.IGNORECASE) \
        .map(lambda s: '?' if pandas.isna(s) or s == '' else s)

def surname(series):
    return common(series) \
        .map(lambda s: '?' if pandas.isna(s) or s == '' else s)

def company_name(series):
    return common(series)

def school_name(series):
    return common(series.fillna('Unlisted'))

def build_soundex(str_val, first_word):
    try:
        if str_val is None:
            return None
        elif first_word:
            return jellyfish.soundex(str_val.strip().split(' ')[0])
        return jellyfish.soundex(str_val)
    except Exception as ex:
        raise Exception('unable to build soundex for str_val "{}"'.format(str_val))

def resident_id(forename, surname, address_id):
    fsoundex = forename.map(lambda s: build_soundex(s, True))
    ssoundex = surname.map(lambda s: build_soundex(s, False))
    series = fsoundex + '•' + ssoundex + '@' + address_id
    return id_common(series) \
        .str.replace(r'\s+', ' ', regex=True) # always last move

def address_id(series):
    return id_common(series) \
        .str.replace(r'\s+', ' ', regex=True) # always last move

def company_id(series):
    return id_common(series.str.upper() \
        .str.replace(r'^.*\s+T/A\s+(.+)$', r'\1', regex=True) \
        .str.replace('LTD', '') \
        .str.replace('LIMITED', '') \
        .str.replace('LLP', '') \
        .str.replace('A/C', '') \
        .str.replace('&', ' AND ') \
        .str.replace(r'- REF:.*', '', regex=True) \
        .str.replace(r'^@', '', regex=True)) \
        .str.replace(r'\s+', ' ', regex=True) # always last move

def discount_code(series):
    return series.map(lambda s: None if pandas.isna(s) else discount_code_string(s.upper()))

def discount_code_string(code):
    if code is None:
        return code
    code = code.upper()
    if code in ['SINGLE', 'SPD'] or code.find('SINGLE') != -1:
        return 'SPD'
    if code.find('EMPTY') != -1 or code.find('UNINHAB') != -1 or code in ['NO RESIDENTS']:
        return 'EMPTY'
    # southend's raw empty codes
    if code.find('PCLC') == 0 or code.find('PCLD') == 0 or code in ['PREM100', 'PREM200', 'PREM300']:
        return 'EMPTY'
    return code

def parse_dates(s, date_formats):
    # try the formats we know about
    for date_format in date_formats:
        try:
            return datetime.strptime(s, date_format)
        except ValueError as ex:
            continue
    # last thing, try an iso parse
    try:
        return datetime.fromisoformat(s.split('.')[0])
    except ValueError as ex:
        raise Exception('unable to parse "{}" with formats: {} (and iso failed too)'.format(s, date_formats))

def convert_residents_to_companies(df, rule_name, func_map_name):
    companies_df = df.copy()
    companies_df['meta.original_lookup_id'] = companies_df['lookup_id'].copy()
    companies_df['meta.exceptional_rule_name'] = rule_name
    companies_df['company_name'] = company_name(func_map_name(companies_df))
    companies_df['lookup_id'] = company_id(companies_df['company_name'])
    companies_df['company_name'] = companies_df['company_name'].map(lambda s: s.split(' T/A ') if s.find(' T/A ') != -1 else s)
    companies_df['sbrr.active'] = False
    companies_df['sbrr.amount'] = 0
    companies_df.drop(columns=['forename', 'surname'], inplace=True)
    return companies_df


# test = pandas.DataFrame([
#     pandas.Series({'company_name': '4 Stars Private Limited T/A Red Chilliezs'})
# ])
# res = company_id(test['company_name'])
# print('res = {}'.format(res.iloc[0]))
