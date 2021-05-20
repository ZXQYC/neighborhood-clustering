import json
import time

import numpy as np
import pandas as pd
import requests

import progress

def get_delay(avg_secs=1):
    dtime = np.random.exponential(avg_secs)
    time.sleep(dtime)

def getdata(addr):
    get_delay()
    x = requests.get('https://www.propertyshark.com/mason/UI/tax_search.html?locale=il_champaign&search_type=address&search_token='+addr.replace(' ','+')+'&location=Champaign+County%2C+IL')
    return x.json()

def fix_dollar(s):
    s = s if s else '0'
    s = s.replace('$','').replace(',','')
    return float(s)

def parse_data(data):
    res = {}
    res['address_found'] = data['address_found']
    res['taxes_found'] = data['taxes_found']
    res['tax_year'] = int(data['tax_year'] if data['tax_year'] else 0)
    for field in ['tax_amount','market_value','land_value','building_value']:
        res[field] = fix_dollar(data[field])
    return res

def data_for_addr(addr):
    d = parse_data(getdata(addr))
    d['address'] = addr
    return d

def get_all_tax_info(addrs,updateEvery=50, printAll=True):
    ans = []
    prog = progress.Progress(len(addrs), updateEvery)
    for i,a in enumerate(addrs):
        d = data_for_addr(a)
        ans.append(d)
        if printAll: print(i,':',d)
        prog.update()
    return pd.DataFrame(ans)