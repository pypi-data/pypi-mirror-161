import pandas
import platform

def json_frame(df, id_prefixes=[], separator=''):
    return df.apply(lambda x: json_series(x, id_prefixes, separator), axis=1)

def extract_value_recursively(s, col_name, orig_col_name, data):
    parts = col_name.split('.')
    if len(parts) == 1:
        data[col_name] = s[orig_col_name]
        # now convert any NaNs scalars to nulls
        try:
            if not isinstance(data[col_name], list) and pandas.isnull(data[col_name]):
                data[col_name] = None
        except ValueError as vex:
            print('unable to extract column {}'.format(col_name))
            raise vex
        #print('val for {} is type {}'.format(orig_col_name, s[orig_col_name].__class__.__name__))
    else:
        data[parts[0]] = extract_value_recursively(s, '.'.join(parts[1:]), orig_col_name, data[parts[0]] \
                                                   if parts[0] in data else {})
    return data

def json_series(s, id_prefixes=[], separator=''):
    data = {}
    
    # now convert all values into a deep dict
    for col_name in s.index.values:
        val = extract_value_recursively(s, col_name, col_name, data)
        
    # add meta to root object
    if 'meta' not in data:
        data['meta'] = {}
    if 'meta' not in data['source']:
        data['source']['meta'] = {}
        
    # track the cluster node used to process this
    data['meta']['@node'] = platform.node()
    data['source']['meta']['row'] = s.name
    
    return data