import re
import pandas

# potentially doesn't need to be exhaustive as it's only trying to catch possible outliers
street_identifiers = [
    'road', 'lane', 'avenue', 'passage', 'street', 'close', 'mews', 'parade', 'gardens', 'chase', 'court', 'esplanade', 'place', 'drive', 'grove',
]

def frame(df, addr_line_names):
    return df.apply(lambda x: series(x, addr_line_names), axis=1)

def series(series, addr_line_names):
    data = []
    for field in addr_line_names:
        if field in series:
            data.append(series[field])
    return simple_record(data)
    
def simple_record(data):
    ''' extract first line of the address '''
    try:
        data = ['' if pandas.isna(d) else d for d in data]
        result = data[0].strip()
        poss_road_field = 1
        is_short = lambda x: len(re.sub('flat', '', re.sub(r'\\s+', '', re.sub(',', '', x)), flags=re.IGNORECASE)) < 10
        # first line is all in brackets (southend ctd)
        if re.search(r'^\(.*\)$', result):
            result = re.sub(r'^\((.*)\)$', r'\1', result)
            if len(data) > 1:
                result += ' ' + data[1].strip()
        # two numbers without a flat prefix?
        if len(data) > 1 and re.search(r'^\d+(a|b|c|d|e)?$', result) and re.search(r'^\d+', data[1].strip()):
            result = 'Flat ' + result
        # separate flat number from street address with a comma
        if re.search('flat', result, re.IGNORECASE):
            result += ','
        # only number / flat number in 1st line?
        if is_short(result) and len(data) > 1:
            result += ' ' + data[1].strip()
            poss_road_field += 1
        # what about street name separated in addr2/3?
        if  len(data) > poss_road_field + 1 and (is_short(result) or any(re.search(si, data[poss_road_field], re.IGNORECASE) for si in street_identifiers)):
            result += ' ' + data[poss_road_field].strip()
        # what about street name separated in addr2 3 and 4?
        elif len(data) > poss_road_field + 1 and any(re.search(si, data[poss_road_field + 1], re.IGNORECASE) for si in street_identifiers):
            result += ' ' + data[poss_road_field].strip() + ' ' + data[poss_road_field + 1].strip()
        # flat prefix wrong way around?
        result = re.sub(r'([0-9]+)\s+flat', r'Flat \1', result, flags=re.IGNORECASE)
        result = re.sub(r'\(((Flat|Unit).*)\)', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r'^(\d{1,5}?\s*)\((.*)\)', r'\1\2', result, flags=re.IGNORECASE)
        result = re.sub(r'R\/O\s+', '', result, flags=re.IGNORECASE)
        result = re.sub(r'\(.*\)', '', result)
        return re.sub(r'\s+', ' ', result).strip()
    except AttributeError as e:
        print('error caused by input: {}'.format(data))
        raise e
