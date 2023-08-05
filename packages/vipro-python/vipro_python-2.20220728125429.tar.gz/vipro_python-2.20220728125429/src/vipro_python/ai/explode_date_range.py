import re
from datetime import datetime

PATTERN_FOR_CHELMSFORD=r'^([\d\/]+)\s*-\s*([\d\/]+)$'

def frame(df, field, date_format, pattern):
    return df.apply(lambda x: series(x, field, date_format, pattern), axis=1, result_type='expand')
    
def series(s, field, date_format, pattern):
    val = s[field]
    if val is None: return s
    res = re.match(pattern, val)
    s['meta.startDate'] = datetime.strptime(res.group(1), date_format).isoformat()
    s['meta.endDate'] = datetime.strptime(res.group(2), date_format).isoformat()
    return s
