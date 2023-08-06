import pandas as pd
import datetime
import os
import plotly.express as px


class Tick:
    def __init__(self, tick_dict: dict):
        self.index = 0
        self.bool_simtrade: bool = False
        self.ts: datetime.datetime = tick_dict.get('ts', datetime.datetime(year=2020, month=1, day=1, hour=9, minute=0, second=0))
        self.close = tick_dict.get('close', 0)
        self.volume = tick_dict.get('volume', 0)
        self.price_ask = tick_dict.get('ask_price', 0)
        self.price_bid = tick_dict.get('bid_price', 0)
        self.volume_ask = tick_dict.get('ask_volume', 0)
        self.volume_bid = tick_dict.get('bid_volume', 0)


class Base_Technical_Indicator(object):

    values = {}

    @classmethod
    def __setitem__(cls, key, value):
        cls.values[key] = value

    @classmethod
    def __getitem__(cls, k):
        return cls.values[k]

    @classmethod
    def get(cls, key, default=None):
        return cls.values.get(key, default)


    def __init__(self, symbol='', date='', period_seconds=10):

        if symbol != '':
            self[symbol] = self

        self.symbol = symbol

        self.date = date

        # 用來計算 AVL。所有價格的累積平均
        self.price_acc_total = 0
        self.count_price_acc_total = 0

        # 用來計算 MA。一段時間內價格的累積平均
        self.price_acc_period = 0
        self.count_price_acc_period = 0

        # 週期
        self.period_seconds = period_seconds

        # 下個週期開始
        self.time_next_tick_second = 0
        self.time_start = datetime.datetime.now()

        self.bool_start_time_determined = False

        self.array_MA = []
        self.array_AVL = []

        # 報價
        self.price_ask = 0
        self.price_bid = 0

        self.volume_ask = 0
        self.volume_bid = 0

        # 開盤價
        self.price_open = -1

        # 目前價格
        self.price_close = 0

        # 最高、最低價
        self.price_highest = 0
        self.price_lowest = 1000000

        # 連內次、連外次
        self.price_last_ask = 0
        self.price_last_bid = 0

        self.times_deal_ask = 0
        self.times_deal_bid = 0

        # 連內量、連外量
        self.volume_deal_ask = 0
        self.volume_deal_bid = 0

        # 目前只是為了畫圖用
        self.dict_result = {'time': [],
                            'close': [],
                            'MA': [],
                            'AVL': []
                            }

    def period_accumulate(self, tick: Tick):
        # 所有價格總和與次數，用來計算所有價格的平均
        self.price_acc_total += tick.close
        self.count_price_acc_total += 1

        # 無論是否在區間內外，都要加成這兩個數值。時間到就會 reset
        self.price_acc_period += tick.close
        self.count_price_acc_period += 1

    def period_calculate(self, tick: Tick):

        # AVL 使用開盤之後所有的價格來計算平均
        if self.count_price_acc_total != 0:
            self.array_AVL.insert(0, self.price_acc_total / self.count_price_acc_total)

        # MA 是使用這段區間內的價格來平均
        if self.count_price_acc_period != 0:
            self.array_MA.insert(0, self.price_acc_period / self.count_price_acc_period)

            self.price_acc_period = 0
            self.count_price_acc_period = 0

        # print(f'Append {tick.ts}, {self.time_next_tick_second}')
        self.dict_result['time'].append(tick.ts)
        self.dict_result['close'].append(tick.close)
        self.dict_result['MA'].append(self.array_MA[0])
        self.dict_result['AVL'].append(self.array_AVL[0])

    def push(self, tick: Tick):

        if tick.ts.time() < datetime.time(9, 0, 0):
            return

        if tick.bool_simtrade:
            return

        self.price_ask = tick.price_ask if tick.price_ask != 0 else self.price_ask
        self.price_bid = tick.price_bid if tick.price_bid != 0 else self.price_bid
        self.volume_ask = tick.volume_ask if tick.volume_ask != 0 else self.volume_ask
        self.volume_bid = tick.volume_bid if tick.volume_bid != 0 else self.volume_bid

        if tick.close == 0:
            return

        # 第一個成交的 tick 到來的時間
        if not self.bool_start_time_determined:
            self.time_start = tick.ts.replace(hour=9, minute=0, second=0, microsecond=0)
            # print(f'Start time: {self.time_start}')

            # The very first tick is counted as first K

        # 第一個成交的 tick 到目前為止經過多少秒數
        time_now_second = (tick.ts - self.time_start).seconds

        self.price_open = tick.close if self.price_open == -1 else self.price_open

        self.price_close = tick.close

        self.price_highest = tick.close if tick.close > self.price_highest else self.price_highest
        self.price_lowest = tick.close if tick.close < self.price_lowest else self.price_lowest


        # 計算連內次，連外次
        # TODO: Not finished
        if True:
            if self.price_last_ask == self.price_ask:
                if tick.close == self.price_ask:
                    self.times_deal_ask += 1
                    self.volume_deal_ask += tick.volume
                else:
                    self.times_deal_ask = 0
                    self.volume_deal_ask = 0
            else:
                self.times_deal_ask = 0
                self.volume_deal_ask = 0

            self.price_last_ask = self.price_ask


        if self.bool_start_time_determined:
            # 在時間區間(period)之內，累積時間區間之內的價格與數次，用來計算時間區間之內的平均價格
            if time_now_second < self.time_next_tick_second:
                self.period_accumulate(tick)
            else:
                # 下一次的區間結束時間
                self.time_next_tick_second = time_now_second + self.period_seconds

                self.period_calculate(tick)
                self.period_accumulate(tick)

        else:
            self.bool_start_time_determined = True
            self.period_accumulate(tick)
            self.period_calculate(tick)

    def draw(self, symbol, date, filename):

        # print(self.dict_result)
        df = pd.DataFrame.from_dict(self.dict_result).astype({'close': float, 'MA': float, 'AVL': float})
        fig = px.line(df, x='time', y=['close', 'MA', 'AVL'], title=f'{date} {symbol}')
        fig.show()
        # fig.write_image(filename)

    def check_place_order(self, tick: Tick, price_threshold_trigger):
        return True


    def check_place_cover(self, tick: Tick, price_threshold_trigger):
        return True


if __name__ == '__main__':
    import gzip
    import json
    from shioaji_ticks import shioaji_ticks
    from mypylib import timeIt

    ti = Base_Technical_Indicator('2368')
    Base_Technical_Indicator('3037')
    Base_Technical_Indicator('3306')

    with timeIt('test TI'):
        with gzip.open('../data/2021-09-23_list6.txt.gz') as fp:
            for l in fp.readlines():
                ll = l.decode().split('\t')
                topic = ll[1]
                quote = ll[2]
                quote = json.loads(quote)

                symbol = topic[-4:]

                target: Base_Technical_Indicator = ti.get(symbol, None)
                if target is None:
                    continue

                target.push(shioaji_ticks(quote))

        ti['3037'].draw('4420', '2021/09/23', '3037.png')
        ti['3306'].draw('3306', '2021/09/23', '3306.png')
        ti['2368'].draw('2368', '2021/09/23', '2368.png')


