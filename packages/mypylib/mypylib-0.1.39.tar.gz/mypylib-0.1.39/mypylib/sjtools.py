import datetime
import pandas as pd
import shioaji as sj
from shioaji import contracts
import os
from time import sleep
import json
from mypylib import get_trade_days
from typing import Union


class Quote(dict):
    def __init__(self, *args):
        super().__init__(*args)

        self.Ask: dict = {}
        self.Bid: dict = {}

    def AskPrice(self):
        return super().get('AskPrice', None)

    def AskVolSum(self):
        return super().get('AskVolSum', None)

    def AskVolume(self):
        return super().get('AskVolume', None)

    def BidPrice(self):
        return super().get('BidPrice', None)

    def BidVolSum(self):
        return super().get('BidVolSum', None)

    def BidVolume(self):
        return super().get('BidVolume', None)

    def Code(self):
        return super().get('Code', None)

    def Date(self):
        return super().get('Date', None)

    def DiffAskVol(self):
        return super().get('DiffAskVol', None)

    def DiffAskVolSum(self):
        return super().get('DiffAskVolSum', None)

    def DiffBidVol(self):
        return super().get('DiffBidVol', None)

    def DiffBidVolSum(self):
        return super().get('DiffBidVolSum', None)

    def FirstDerivedAskPrice(self):
        return super().get('FirstDerivedAskPrice', None)

    def FirstDerivedAskVolume(self):
        return super().get('FirstDerivedAskVolume', None)

    def FirstDerivedBidPrice(self):
        return super().get('FirstDerivedBidPrice', None)

    def FirstDerivedBidVolume(self):
        return super().get('FirstDerivedBidVolume', None)

    def TargetKindPrice(self):
        return super().get('TargetKindPrice', None)

    def Time(self):
        return super().get('Time', None)

    def Simtrade(self):
        return super().get('Simtrade', None)

    def zipAsk(self):
        self.Ask = dict(zip(self.AskPrice(), self.AskVolume()))

    def zipBid(self):
        self.Bid = dict(zip(self.BidPrice(), self.BidVolume()))


# {"AmountSum": [65246500.0],
#  "Close": [415.5],
#  "Date": "2022/06/07",
#  "TickType": [2],
#  "Time": "09:01:41.845465",
#  "VolSum": [156],
#  "Volume": [3]}
class Market(dict):
    def Amount(self):
        return super().get('Amount', None)

    def AmountSum(self):
        return super().get('AmountSum', None)

    def AvgPrice(self):
        return super().get('AvgPrice', None)

    def Close(self):
        return super().get('Close', None)

    def Code(self):
        return super().get('Code', None)

    def Date(self):
        return super().get('Date', None)

    def DiffPrice(self):
        return super().get('DiffPrice', None)

    def DiffRate(self):
        return super().get('DiffRate', None)

    def DiffType(self):
        return super().get('DiffType', None)

    def High(self):
        return super().get('High', None)

    def Low(self):
        return super().get('Low', None)

    def Open(self):
        return super().get('Open', None)

    def TargetKindPrice(self):
        return super().get('TargetKindPrice', None)

    def TickType(self):
        return super().get('TickType', None)

    def Time(self):
        return super().get('Time', None)

    def TradeAskVolSum(self):
        return super().get('TradeAskVolSum', None)

    def TradeBidVolSum(self):
        return super().get('TradeBidVolSum', None)

    def VolSum(self):
        return super().get('VolSum', None)

    def Volume(self):
        return super().get('Volume', None)

    def Simtrade(self):
        return super().get('Simtrade', None)



class SJ_wrapper:
    def __init__(self, _id='H121933940', password='123edcxzaqws'):
        self._id = _id
        self.password = password

        print(f'使用正式帳號 {_id} {password}')
        self.api = sj.Shioaji()
        self.api.login(_id, password, contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."))


class SJ_downloader(SJ_wrapper):
    def __init__(self, _id='H121933940', password='123edcxzaqws'):
        super(SJ_downloader, self).__init__(_id=_id, password=password)

        self.ticks = None

    def download_ticks(self, contract: contracts, date: Union[str, datetime.datetime]):
        print(contract, date)
        ticks = self.api.ticks(contract=contract, date=date if isinstance(date, str) else datetime.datetime.strftime('%Y-%m-%d'))
        self.ticks = ticks
        return ticks

    def save_ticks(self, filename):
        df = pd.DataFrame({**self.ticks})
        df.ts = pd.to_datetime(df.ts)

        df.to_csv(filename)


def unit_test_SJ_downloader():
    # downloader = SJ_downloader(_id='F130153547', password='qwer0000')
    downloader = SJ_downloader(_id='H121933940', password='123edcxzaqws')
    # downloader = SJ_downloader(_id='F130153547', password='qwer0000')

    if not os.path.isfile('trade_days.txt'):
        trade_days = get_trade_days('2018-01-01', datetime.datetime.today())
        trade_days.reverse()
        with open('trade_days.txt', 'w+') as fp:
            json.dump(trade_days, fp)
    else:
        with open('trade_days.txt') as fp:
            trade_days = json.load(fp)

    for day in trade_days:
        print(day)
        file = f'days/TXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.TXF.TXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/EXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.EXF.EXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/FXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.FXF.FXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)


def converter_SJ_ticks_to_MC():
    files = os.listdir('days')
    files.sort()
    print(files)

    with open('EXF_ticks_for_MC.txt', 'w+') as ex:
        with open('FXF_ticks_for_MC.txt', 'w+') as fx:
            with open('TXF_ticks_for_MC.txt', 'w+') as tx:
                fp = None
                for file in files:
                    if file[0:3] == 'EXF':
                        fp = ex
                    if file[0:3] == 'FXF':
                        fp = fx
                    if file[0:3] == 'TXF':
                        fp = tx



if __name__ == '__main__':

    if True:
        unit_test_SJ_downloader()

    if False:
        converter_SJ_ticks_to_MC()

