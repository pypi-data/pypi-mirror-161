import datetime
import json
import math
import os
import queue
import re
import ssl
import threading
import time
from typing import Union

import requests

ssl._create_default_https_context = ssl._create_unverified_context
from termcolor import cprint
from inspect import currentframe

__version__ = '0.1.39'

__info__ = {
    '2022/01/04: 0.1.18 加入 __info__。',
    '2022/01/04: 0.1.18 Carey修改 MVP的部分。',
    '2022/01/05: 0.1.19 add check_place_cover 預防漲停鎖住',
    '2022/01/06: 0.1.20 add get_stock_future_data(). 用來抓取每天股票期貨資料',
    '2022/01/06: 0.1.20 add get_stock_future_snapshot(). 用來抓每天股票、股票期貨漲停、跌停價格',
    '2022/01/11: 0.1.21 Add virtual function, check_place_cover() in ti class',
    '2022/02/10: 0.1.22 Add build_dealer_downloader()',
    '2022/02/14: 0.1.23 把 libexcel.py 搬到這邊來，以後可以全部沿用。',
    '2022/06/13: 0.1.24 加入 tplaysound ',
    '2022/06/24: 0.1.28 加入 tLineNotify',
    '2022/06/26: 0.1.29 加入 my_addressable_IP()',
    '2022/06/29: 0.1.30 加入需要的module',
    '2022/07/02: 0.1.32 加入 DefaultOrderedDict',
    '2022/07/13: 0.1.33 加入 binance_copy_bot',
    '2022/07/14: 0.1.34 加入 price_ticks_offset_dec() 要用 Decimal 避免float error',
    '2022/07/15: 0.1.35 binance_copy_bot() 改用 API方式',
    '2022/07/16: 0.1.36 加入 read_warrant_bible()',
    '2022/07/17: 0.1.37 加入 tredis'
    '2022/08/01: 0.1.39 加入註解，把一些東西拆開來，以免每次mypylib都要載入一堆 module'
}


request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

path_cronlog = 'cronlog'

from collections import OrderedDict
from collections.abc import Callable


class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
                not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


import urllib.request


def my_addressable_IP():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')


def __LINE__():
    cf = currentframe()
    return cf.f_back.f_lineno


def get_all_stock_code_name_dict():
    today = datetime.datetime.today()

    cache_file = f'all_stock_code-{today.strftime("%Y%m%d")}.json'

    if not os.path.isfile(cache_file):

        import shioaji as sj

        def simu_login(id='PAPIUSER08', password='2222'):
            print(f'使用測試帳號 {id} {password}')
            api = sj.Shioaji(simulation=True)
            api.login(id, password, contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."))
            return api

        api = simu_login()

        all_code_name_dir = {}
        for x in api.Contracts.Stocks.OTC:
            if len(x.code) == 4:
                all_code_name_dir[x.code] = x.name

        for x in api.Contracts.Stocks.TSE:
            if len(x.code) == 4:
                all_code_name_dir[x.code] = x.name

        with open(cache_file, 'w') as fp:
            json.dump(all_code_name_dir, fp)
    else:
        with open(cache_file, 'r') as fp:
            all_code_name_dir = json.load(fp)

    return all_code_name_dir


def get_day_trade_candidates(output_file_path='可當沖.json', days=0):
    import pandas as pd
    OTC_url_format = 'https://www.tpex.org.tw/web/stock/trading/' \
                     'intraday_trading/intraday_trading_list_print.php?' \
                     'l=zh-tw&d={}/{:02d}/{:02d}&stock_code=&s=0,asc,1'

    SEM_url_format = 'https://www.twse.com.tw/exchangeReport/' \
                     'TWTB4U?response=html&date={}{:02d}{:02d}&selectType=All'

    today = datetime.datetime.today() - datetime.timedelta(days=days)

    SEM_url = SEM_url_format.format(today.year, today.month, today.day)

    # print(SEM_url)

    ssl._create_default_https_context = ssl._create_unverified_context
    table = pd.read_html(SEM_url)
    df = table[0]
    df.columns = df.columns.droplevel()
    if '證券代號' not in df.columns:
        df = table[1]
        df.columns = df.columns.droplevel()
    df['證券代號'] = df['證券代號'].astype('str')
    mask = df['證券代號'].str.len() == 4
    df = df.loc[mask]
    df = df[['證券代號', '證券名稱', '暫停現股賣出後現款買進當沖註記']]
    df['暫停現股賣出後現款買進當沖註記'] = df['暫停現股賣出後現款買進當沖註記'].apply(lambda x: False if x == 'Y' else True)

    OCT_url = OTC_url_format.format(today.year - 1911, today.month, today.day)
    # print(OCT_url)

    ssl._create_default_https_context = ssl._create_unverified_context
    table = pd.read_html(OCT_url)

    df1 = table[0]
    df1.columns = df1.columns.droplevel()
    df1['證券代號'] = df1['證券代號'].astype('str')
    mask = df1['證券代號'].str.len() == 4
    df1 = df1.loc[mask]
    df1 = df1[['證券代號', '證券名稱', '暫停現股賣出後現款買進當沖註記']]
    df1['暫停現股賣出後現款買進當沖註記'] = df1['暫停現股賣出後現款買進當沖註記'].apply(lambda x: False if x == '＊' else True)

    all_df = pd.concat([df, df1])
    all_df.rename({'證券代號': 'symbol'}, axis=1, inplace=True)
    all_df.rename({'證券名稱': 'name'}, axis=1, inplace=True)
    all_df.rename({'暫停現股賣出後現款買進當沖註記': 'DayTrade'}, axis=1, inplace=True)
    all_df = all_df.set_index('name')
    ret = all_df.to_dict('index')
    all_df.to_csv(output_file_path)

    return ret


def get_top_future_trade_volume_list():
    url = 'https://deeptrade.pfcf.com.tw/stockf/volume30/volume?format=json'
    r = requests.get(url)
    data = json.loads(r.text)

    pattern = '^[0-9]*'

    top_future_rank = []

    for x in data:
        code = re.match(pattern, x[0])[0]
        name = re.sub(pattern, '', x[0])
        top_future_rank.append([code, name, x[1]])

    return top_future_rank


def get_stock_future_snapshot(filename='stock_future_snapshot.txt'):
    import shioaji as sj

    def login(id='H121933940',
              password='123edcxzaqws',
              ca_path="SinoPac.pfx",
              ca_password='H121933940',
              person_id='H121933940'):
        print(f'使用正式帳號 {id} {password}')
        api = sj.Shioaji()
        api.login(id,
                  password,
                  contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
                  )
        return api

    api = login()

    contracts = []

    for x in api.Contracts.Futures:
        target = x[x._name + 'R1']
        if target is not None:
            if target.name[0] == '小':
                continue
            if len(target.underlying_code) > 4:
                continue
            if target.underlying_code != "":
                print(target.underlying_code, target.symbol[0:3], target.name)
                contracts.append(target)
                c = api.Contracts.Stocks[target.underlying_code]
                if c is not None:
                    contracts.append(c)

    with open(f'{path_cronlog}/{filename}', 'w+') as fp:
        fp.write(f'# {datetime.datetime.now()}\n')
        # 隔天早上八點半以後資料會更新
        c: sj.shioaji.Contract
        for c in contracts:
            fp.write(f'{c.code} {c.reference} {c.limit_up} {c.limit_down}\n')

    api.logout()


def get_stock_future_data(filename='stock_future_data.txt'):
    import pandas as pd
    if not os.path.isdir(path_cronlog):
        os.mkdir(path_cronlog)

    html_tables = pd.read_html('https://www.taifex.com.tw/cht/5/stockMargining')

    df_dict: dict = html_tables[0].to_dict('index')

    with open(f'{path_cronlog}/{filename}', 'w+') as fp:
        fp.write(f'# {datetime.datetime.now()}\n')

        for rec in df_dict.values():
            line = f'{rec["股票期貨標的證券代號"]} {rec["股票期貨英文代碼"]} {rec["股票期貨  中文簡稱"]} {rec["原始保證金適用比例"]}'
            print(line)
            fp.write(f'{line}\n')


def get_punishment_list():
    import pandas as pd
    if not os.path.isdir(path_cronlog):
        os.mkdir(path_cronlog)

    if os.path.isfile(f'{path_cronlog}/punishment-{datetime.datetime.today().strftime("%Y-%m-%d")}.txt'):
        p_code = []
        p_name = []
        with open(f'{path_cronlog}/punishment-{datetime.datetime.today().strftime("%Y-%m-%d")}.txt') as f:
            line: str
            for line in f.readlines():
                line = line.rstrip()
                code, name = line.split(' ')
                p_code.append(code)
                p_name.append(name)
    else:
        URL_TWSE = 'https://www.twse.com.tw/announcement/punish?response=html'
        TPEX_TWSE = 'https://www.tpex.org.tw/web/bulletin/disposal_information/disposal_information_print.php'

        ssl._create_default_https_context = ssl._create_unverified_context

        # print('讀取上市處置股資料')
        p1_code = pd.read_html(URL_TWSE)[0].astype('str')['證券代號'].values
        p1_name = pd.read_html(URL_TWSE)[0].astype('str')['證券名稱'].values
        # print('讀取上櫃處置股資料')
        p2_code = pd.read_html(TPEX_TWSE)[0]['證券代號'][0:-1].values
        p2_name = pd.read_html(TPEX_TWSE)[0]['證券名稱'][0:-1].values
        p_code = list(p1_code) + list(p2_code)
        p_name = list(p1_name) + list(p2_name)
        print(f'處置股資料 {p_code}')

        with open(f'{path_cronlog}/punishment-{datetime.datetime.today().strftime("%Y-%m-%d")}.txt', 'w') as f:
            for code, name in zip(p_code, p_name):
                f.write(f'{code} {name}\n')

    for code, name in zip(p_code, p_name):
        pass
        # print(code, name)
    return p_code, p_name


# 來源網頁: https://www.twse.com.tw/zh/page/trading/exchange/TWT92U.html
# 抓取資料: https://www.twse.com.tw/exchangeReport/TWT92U?date=20211008
def get_TSE_short_selling_list(date=datetime.datetime.today()):
    if not os.path.isdir(path_cronlog):
        os.mkdir(path_cronlog)
    path_cache = f'{path_cronlog}/TSE-short-selling_list-{date.strftime("%Y-%m-%d")}.txt'
    if os.path.isfile(path_cache):
        with open(path_cache) as fp:
            ret_dict = json.load(fp)
    else:
        url = f'https://www.twse.com.tw/exchangeReport/TWT92U?date={date.strftime("%Y%m%d")}'
        r = requests.get(url, headers=request_headers)
        ret = json.loads(r.text)
        ret_dict = {'list': [], 'stop short selling list': []}
        for x in ret['data']:
            ret_dict['list'].append(x[0])
            if x[2] == '*':
                ret_dict['stop short selling list'].append(x[0])
        with open(path_cache, 'w') as fp:
            json.dump(ret_dict, fp)
    return ret_dict


# 來源網頁: https://www.tpex.org.tw/web/stock/margin_trading/margin_mark/margin_mark.php?l=zh-tw
# 抓取資料: https://www.tpex.org.tw/web/stock/margin_trading/margin_mark/margin_mark_result.php?&d=110/09/08
def get_OTC_short_selling_list(date=datetime.datetime.today()):
    if not os.path.isdir(path_cronlog):
        os.mkdir(path_cronlog)
    path_cache = f'{path_cronlog}/OTC-short-selling_list-{date.strftime("%Y-%m-%d")}.txt'
    if os.path.isfile(path_cache):
        with open(path_cache) as fp:
            ret_dict = json.load(fp)
    else:
        url = f'https://www.tpex.org.tw/web/stock/margin_trading/margin_mark/margin_mark_result.php?&d={date.year - 1911}/{date.month:02d}/{date.day:02d}'
        r = requests.get(url, headers=request_headers)
        ret = json.loads(r.text)
        ret_dict = {'list': [], 'stop short selling list': []}
        for x in ret['aaData']:
            ret_dict['list'].append(x[0])
            if x[2] == '*':
                ret_dict['stop short selling list'].append(x[0])
        with open(path_cache, 'w') as fp:
            json.dump(ret_dict, fp)
    return ret_dict


def get_short_selling_list(date=datetime.datetime.today()):
    TSE_list = get_TSE_short_selling_list(date)
    OTC_list = get_OTC_short_selling_list(date)

    return {'list': TSE_list['list'] + OTC_list['list'], 'stop short selling list': TSE_list['stop short selling list'] + OTC_list['stop short selling list']}


def parse_date_time(date_string, time_string) -> datetime.datetime:
    if '.' in time_string:
        if '/' in date_string:
            timestamp = datetime.datetime.strptime(f'{date_string} {time_string}', '%Y/%m/%d %H:%M:%S.%f')
        else:
            timestamp = datetime.datetime.strptime(f'{date_string} {time_string}', '%Y-%m-%d %H:%M:%S.%f')
    else:
        if '/' in date_string:
            timestamp = datetime.datetime.strptime(f'{date_string} {time_string}', '%Y/%m/%d %H:%M:%S')
        else:
            timestamp = datetime.datetime.strptime(f'{date_string} {time_string}', '%Y-%m-%d %H:%M:%S')
    return timestamp


class timeIt:
    def __init__(self, prompt=''):
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now()
        self.prompt = prompt

    def __enter__(self):
        self.start_time = datetime.datetime.now()
        print(f'Start to {self.prompt}. {self.start_time}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.datetime.now()
        print(f'It took {(self.end_time - self.start_time).seconds} seconds to finish {self.prompt}.')


########################
# Decimal
########################
from decimal import Decimal

def get_current_price_tick_dec(price: Decimal, down=False):
    # print(f'get_current_price_tick: {price}')
    if down:
        if price <= Decimal('10'):
            return Decimal('0.01')
        if 10 < price <= Decimal('50'):
            return Decimal('0.05')
        if 50 < price <= Decimal('100'):
            return Decimal('0.1')
        if 100 < price <= Decimal('500'):
            return Decimal('0.5')
        if 500 < price <= Decimal('1000'):
            return Decimal('1')
        if price > Decimal('1000'):
            return Decimal('5')
    else:
        if price < Decimal('10'):
            return Decimal('0.01')
        if 10 <= price < Decimal('50'):
            return Decimal('0.05')
        if 50 <= price < Decimal('100'):
            return Decimal('0.1')
        if 100 <= price < Decimal('500'):
            return Decimal('0.5')
        if 500 <= price < Decimal('1000'):
            return Decimal('1')
        if price >= Decimal('1000'):
            return Decimal('5')


# price1 should be .LE. to price2
def get_ticks_between_dec(_price1: Decimal, _price2: Decimal):
    if _price2 < _price1:
        price1 = _price2
        price2 = _price1
    else:
        price1 = _price1
        price2 = _price2
    # print(price1, price2)
    ticks = 0
    while True:
        price1 += get_current_price_tick_dec(price1)
        # print(f'{ticks}: {price1} {price2}')
        if price1 > price2:
            break
        ticks += 1
    return ticks


# TODO: Use decimal
def price_ticks_offset_dec(price, ticks):
    current_tick = get_current_price_tick(price)
    price = round(price - (price + 0.001) % current_tick, 2)
    # print(f'normalized price: {price}')
    if ticks == 0:
        return price
    step = 1 if ticks > 0 else -1
    for i in range(0, ticks, step):
        current_tick = get_current_price_tick(price, down=True if step == -1 else False)
        # print(i, price, current_tick)
        price += current_tick * step
    return round(price, 3)


def get_limit_up_and_down_price_dec(price):
    limit_up = price * 1.1
    tick = get_current_price_tick(limit_up)
    # By Carey
    # df['漲停價'] = round(df['漲停價'] - ((df['漲停價']+0.001) % df['tick_up']),2)
    limit_up = round(limit_up - (limit_up + 0.001) % tick, 2)

    limit_down = price * 0.9
    tick = get_current_price_tick(limit_down)
    limit_down = math.ceil(limit_down / tick)
    limit_down = limit_down * tick

    return round(limit_up, 3), round(limit_down, 3)


def price_stop_profit_and_lose_dec(price_enter, percentage_stop_profit, percentage_stop_lose, bool_call_or_put, tax=0.0015, fee=0.001425):
    if bool_call_or_put:
        price_stop_profit = price_ticks_offset(price_enter * (1 + percentage_stop_profit + fee * 2 + tax), 0)
        price_stop_lose = price_ticks_offset(price_enter * (1 + percentage_stop_lose + fee * 2 + tax), 0)
    else:
        price_stop_profit = price_ticks_offset(price_enter * (1 - percentage_stop_profit - fee * 2 - tax), 0)
        price_stop_lose = price_ticks_offset(price_enter * (1 - percentage_stop_lose - fee * 2 - tax), 0)

    return price_stop_profit, price_stop_lose


########################
# Obselete
########################

def get_current_price_tick(price, down=False):
    # print(f'get_current_price_tick: {price}')
    if down:
        if price <= 10:
            return 0.01
        if 10 < price <= 50:
            return 0.05
        if 50 < price <= 100:
            return 0.1
        if 100 < price <= 500:
            return 0.5
        if 500 < price <= 1000:
            return 1
        if price > 1000:
            return 5
    else:
        if price < 10:
            return 0.01
        if 10 <= price < 50:
            return 0.05
        if 50 <= price < 100:
            return 0.1
        if 100 <= price < 500:
            return 0.5
        if 500 <= price < 1000:
            return 1
        if price >= 1000:
            return 5


# price1 should be .LE. to price2
def get_ticks_between(_price1, _price2):
    if _price2 < _price1:
        price1 = _price2
        price2 = _price1
    else:
        price1 = _price1
        price2 = _price2

    ticks = 0
    while True:
        price1 += get_current_price_tick(price1)
        if price1 > price2:
            break
        ticks += 1
    return ticks


def price_ticks_offset(price, ticks):
    current_tick = get_current_price_tick(price)
    price = round(price - (price + 0.001) % current_tick, 2)
    # print(f'normalized price: {price}')
    if ticks == 0:
        return price
    step = 1 if ticks > 0 else -1
    for i in range(0, ticks, step):
        current_tick = get_current_price_tick(price, down=True if step == -1 else False)
        # print(i, price, current_tick)
        price += current_tick * step
    return round(price, 3)


def get_limit_up_and_down_price(price):
    limit_up = price * 1.1
    tick = get_current_price_tick(limit_up)
    # By Carey
    # df['漲停價'] = round(df['漲停價'] - ((df['漲停價']+0.001) % df['tick_up']),2)
    limit_up = round(limit_up - (limit_up + 0.001) % tick, 2)

    limit_down = price * 0.9
    tick = get_current_price_tick(limit_down)
    limit_down = math.ceil(limit_down / tick)
    limit_down = limit_down * tick

    return round(limit_up, 3), round(limit_down, 3)


def price_stop_profit_and_lose(price_enter, percentage_stop_profit, percentage_stop_lose, bool_call_or_put, tax=0.0015, fee=0.001425):
    if bool_call_or_put:
        price_stop_profit = price_ticks_offset(price_enter * (1 + percentage_stop_profit + fee * 2 + tax), 0)
        price_stop_lose = price_ticks_offset(price_enter * (1 + percentage_stop_lose + fee * 2 + tax), 0)
    else:
        price_stop_profit = price_ticks_offset(price_enter * (1 - percentage_stop_profit - fee * 2 - tax), 0)
        price_stop_lose = price_ticks_offset(price_enter * (1 - percentage_stop_lose - fee * 2 - tax), 0)

    return price_stop_profit, price_stop_lose


#
# Usage:
#   for day in date_range(datetime.datetime(year=2021, month=1, day=1), datetime.datetime(year=2021, month=10, day=1)):
#       print(day)
#
def date_range(start_date, end_date, bool_reverse=False):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def mypylib_unit_test():
    cprint('抓取上市融券資料', 'yellow')
    print(get_TSE_short_selling_list())

    cprint('抓取上櫃融券資料', 'yellow')
    print(get_OTC_short_selling_list())

    cprint('抓取融券資料', 'yellow')
    print(get_short_selling_list())

    cprint('抓取處置股資料', 'yellow')
    print(get_punishment_list())

    cprint('抓取成交量前幾名的股票期貨名單', 'yellow')
    print(get_top_future_trade_volume_list())

    cprint('抓取可當沖資料', 'yellow')
    print(get_day_trade_candidates())


def short_selling_to_csv():
    import pandas as pd
    for day in date_range(datetime.datetime(year=2019, month=1, day=1), datetime.datetime.today()):
        print(day)
        TSE_path_cache = f'{path_cronlog}/TSE-short-selling_list-{day.strftime("%Y-%m-%d")}.txt'
        OTC_path_cache = f'{path_cronlog}/OTC-short-selling_list-{day.strftime("%Y-%m-%d")}.txt'

        if os.path.isfile(TSE_path_cache) and os.path.isfile(OTC_path_cache):
            with open(TSE_path_cache) as fp:
                TSE_list = json.load(fp)
            with open(OTC_path_cache) as fp:
                OTC_list = json.load(fp)

            all = {'list': TSE_list['list'] + OTC_list['list'], 'stop short selling list': TSE_list['stop short selling list'] + OTC_list['stop short selling list']}

            if len(all['list']) < 100:
                continue

            data = {}

            for symbol in all['list']:
                data[symbol] = [1, 0]

            for symbol in all['stop short selling list']:
                data[symbol][1] = 1

            # df = pd.DataFrame.from_dict(data, orient='index', columns=['list', 'stop short selling list'])
            # print(df)
            # df.to_csv(f'csv/list-{day.strftime("%Y-%m-%d")}.csv')

            with open(f'json/list-{day.strftime("%Y-%m-%d")}.json', 'w') as fp:
                json.dump(data, fp)


def get_future_ex(date: datetime.datetime, next_month=False):
    end_of_contract_day = 21 - (date.replace(day=1).weekday() + 2) % 7;
    letter = chr(ord('A') - (0 if next_month else 1) + date.month + (1 if end_of_contract_day < date.day else 0))

    return f'{"A" if letter == "M" else letter}{(date.year + (1 if letter == "M" else 0)) % 10}'


def is_end_of_contract_day(date: datetime.datetime):
    end_of_contract_day = 21 - (date.replace(day=1).weekday() + 4) % 7
    # print(f'end of contrract day: {end_of_contract_day}')
    return True if date.day == end_of_contract_day else False


def load_all_shioaji_ticks(source_dir='../../shioaji_ticks'):
    all_files = []

    for d in os.listdir(source_dir):
        if not os.path.isdir(f'{source_dir}/{d}'):
            continue
        if d == 'cache':
            continue
        for f in os.listdir(f'{source_dir}/{d}'):
            if not f.startswith('20'):
                continue
            full_path = f'{source_dir}/{d}/{f}'
            all_files.append([full_path, d, f.split('.')[0]])
    return all_files


def build_dealer_downloader(date=datetime.datetime(year=2020, month=1, day=1), target_directory='自營商歷史資料'):
    if not os.path.isdir(target_directory):
        os.mkdir(target_directory)

    day_delta = datetime.timedelta(days=1)
    while date < datetime.datetime.now():
        print(date)

        # time.sleep(30)

        date = date + day_delta

        #
        # 上櫃
        #
        otc_dealer_buy_csv_path = f'{target_directory}/{date.year}{date.month:02d}{date.day:02d}_OTC_buy.csv'
        otc_dealer_sell_csv_path = f'{target_directory}/{date.year}{date.month:02d}{date.day:02d}_OTC_sell.csv'
        if os.path.isfile(otc_dealer_buy_csv_path) is False:
            url = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_hedge_result.php?l=zh-tw&t=D&type=buy&d={date.year - 1911}/{date.month:02d}/{date.day:02d}"
            print(url)

            r = requests.get(url, headers=request_headers)
            jdata = json.loads(r.content)

            if len(jdata['aaData']) == 0:
                continue

            with open(otc_dealer_buy_csv_path, 'w') as f:
                f.write('\ufeff')
                f.write(',,,(自行買賣),(自行買賣),(自行買賣),(避險),(避險),(避險),買賣超\n')
                f.write(',,,買進,賣出,買賣超,買進,賣出,買賣超,(仟股)\n')
                f.write(',,,,,(仟股),,,(仟股),,\n')
                # print(jdata)

                for x in jdata['aaData']:
                    # print(x)
                    string = '\t'.join(x)
                    string = string.replace(',', '')
                    string = string.replace('\t', ',')
                    f.write(string + '\n')

        if os.path.isfile(otc_dealer_sell_csv_path) is False:
            url = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_hedge_result.php?l=zh-tw&t=D&type=sell&d={date.year - 1911}/{date.month:02d}/{date.day:02d}"
            print(url)

            r = requests.get(url, headers=request_headers)
            jdata = json.loads(r.content)
            with open(otc_dealer_sell_csv_path, 'w') as f:
                f.write('\ufeff')
                f.write(',,,(自行買賣),(自行買賣),(自行買賣),(避險),(避險),(避險),買賣超\n')
                f.write(',,,買進,賣出,買賣超,買進,賣出,買賣超,(仟股)\n')
                f.write(',,,,,(仟股),,,(仟股),,\n')

                for x in jdata['aaData']:
                    # print(x)
                    string = '\t'.join(x)
                    string = string.replace(',', '')
                    string = string.replace('\t', ',')
                    f.write(string + '\n')

        #
        # 上市
        #
        dealer_csv_path = f'{target_directory}/{date.year}{date.month:02d}{date.day:02d}.csv'
        if os.path.isfile(dealer_csv_path) is False:
            url = f'https://www.twse.com.tw/fund/TWT43U?response=csv&date={date.year}{date.month:02d}{date.day:02d}'
            print(url)

            r = requests.get(url, headers=request_headers)
            with open(dealer_csv_path + '_', 'wb') as f:
                f.write(r.content)

            with open(dealer_csv_path, 'w') as f:
                f.write('\ufeff')

            time.sleep(10)

            os.system(f'/usr/bin/iconv -f BIG5-2003 -t UTF-8 {dealer_csv_path}_ >> {dealer_csv_path}')
            os.unlink(dealer_csv_path + '_')



def get_trade_days(date_start: Union[str, datetime.datetime] = '2018-01-01',
                   date_end: Union[str, datetime.datetime] = '2022-07-31') -> list:
    date_start = date_start if isinstance(date_start, str) else date_start.strftime('%Y-%m-%d')
    date_end = date_end if isinstance(date_end, str) else date_end.strftime('%Y-%m-%d')

    file_cache = f'trade_days_{date_start}_{date_end}.txt'

    if os.path.isfile(file_cache):
        with open(file_cache) as fp:
            return json.load(fp)

    from FinMind.data import DataLoader
    # print(date_start, date_end)

    dl = DataLoader()
    stock_data = dl.taiwan_stock_daily(stock_id='2330', start_date=date_start, end_date=date_end)
    days = stock_data['date']
    # print(days)
    list_days = []
    for x in days:
        list_days.append(x)

    with open(file_cache, 'w+') as fp:
        json.dump(list_days, fp)

    return list_days


if __name__ == '__main__':
    from time import sleep

    if True:
        ret = get_trade_days()
        print(ret)

        exit(0)



    if False:
        build_dealer_downloader()

    if False:
        all = load_all_shioaji_ticks()
        print(f'There are {len(all)} files')

        get_stock_future_snapshot()
        get_stock_future_data()

        print(get_future_ex(datetime.datetime(year=2021, month=12, day=1)))
        print(get_future_ex(datetime.datetime(year=2021, month=12, day=15)))
        print(get_future_ex(datetime.datetime(year=2021, month=12, day=30)))
        print(is_end_of_contract_day(datetime.datetime(year=2021, month=12, day=1)))
        print(is_end_of_contract_day(datetime.datetime(year=2021, month=12, day=14)))
        print(is_end_of_contract_day(datetime.datetime(year=2021, month=12, day=15)))
        print(is_end_of_contract_day(datetime.datetime(year=2021, month=12, day=16)))
        print(get_future_ex(datetime.datetime(year=2021, month=12, day=15), next_month=is_end_of_contract_day(datetime.datetime(year=2021, month=12, day=15))))

        print(get_ticks_between(100, 100))

        mypylib_unit_test()

    if False:
        for day in date_range(datetime.datetime(year=2019, month=1, day=1), datetime.datetime.today()):
            print(day)
            TSE_path_cache = f'{path_cronlog}/TSE-short-selling_list-{day.strftime("%Y-%m-%d")}.txt'
            OTC_path_cache = f'{path_cronlog}/OTC-short-selling_list-{day.strftime("%Y-%m-%d")}.txt'
            if not os.path.isfile(TSE_path_cache) and not os.path.isfile(OTC_path_cache):
                get_short_selling_list(day)
                sleep(5)

        short_selling_to_csv()

        print(__LINE__())
