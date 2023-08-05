import pandas
from nameparser import HumanName
import re

def frame(df, field):
    print('WARNING: can take time to explode the name for all {} rows'.format(len(df)))
    return df.apply(lambda x: series(x, field), axis=1)
    
def series(s, field):
    try:
        name = '?' if pandas.isna(s[field]) else s[field]
        name = re.sub('Mstr', 'Master', name, flags=re.IGNORECASE)
        parsed = HumanName(name)
        s['forename'] = parsed.first
        s['meta.middleName'] = None if parsed.middle == '' else parsed.middle
        s['surname'] = parsed.last
        return s
    except AttributeError as ex:
        raise Exception('unable to extract name in field {}, series {}'.format(field, s))