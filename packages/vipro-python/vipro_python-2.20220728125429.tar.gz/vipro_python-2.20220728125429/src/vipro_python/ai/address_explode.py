from .address import frame

# extract addresses
def extract_address(df, full_address_field):
    return df.apply(lambda x: extract_address_series(x, full_address_field), axis=1, result_type='expand')

def extract_address_series(s, full_address_field):
    addrSplit = s[full_address_field].split(', ')
    for i in range(0, len(addrSplit)):
        s['Addr{}'.format(i+1)] = addrSplit[i]
        if i == len(addrSplit)-1:
            s['AddrLast'] = addrSplit[i]
    return s

def apply(df, full_address_field):
    # slow operation for large datasets
    print('WARNING: exploding addresses can take a long time with {} records'.format(len(df)))
    extracted_df = extract_address(df, full_address_field)
    addr_df = extracted_df.copy()
    addr_df['addr1_clean'] = frame(addr_df, ['Addr1', 'Addr2', 'Addr3', 'Addr4', 'Addr5', 'Addr6', 'Addr7', 'Addr8'])
    addr_df['AddrLast'] = addr_df['AddrLast'].str.upper()
    return addr_df
    
def cleanup(df):
    # which columns?
    colsToRm = ['AddrLast', 'addr1_clean']
    for i in range(0, 15):
        field = 'Addr{}'.format(i)
        if field in df:
            colsToRm.append(field)
    df.drop(columns=colsToRm, inplace=True)