import xlrd
import pandas as pd
from collections import defaultdict


#
# 0 日期：
# 1
# 2
# 3 權證
# 4 代碼
# 5 03027Q
# 6 03028Q
#

# dict_warrant_to_info:
#   list_warrant.keys() = ['064474', '065228', '065395'.....
#    {'權證名稱': '世紀鋼兆豐23購02', '發行券商': '兆豐', '權證價格': 0.3, '權證漲跌': 0, '權證漲跌幅': 0, '權證成交量': 0,
#    '權證買價': 0.25, '權證賣價': 0.26, '權證買賣價差': 0.04, '溢價比率': 0.431, '價內價外': 0.27385, '理論價格': 0.251,
#    '隱含波動率': 0.4703, '有效槓桿': 5.39, '剩餘天數': 235, '最新行使比例': 0.059, '標的代碼': '9958', '標的名稱': '世紀鋼',
#    '標的價格': 94.4, '標的漲跌': -1.9, '標的漲跌幅': -0.0197, '最新履約價': 130, '最新界限價': '-', '標的20日波動率': 0.4206,
#    '標的60日波動率': 0.382046, '標的120日波動率': 0.380576, '權證DELTA': 0.0145, '權證GAMMA': 0.0005, '權證VEGA': 0.0137,
#    '權證THETA': -0.0021, '內含價值': 0, '時間價值': 0.255, '流通在外估計張數': 0, '流通在外增減張數': 0, '上市日期': '2022/07/08',
#    '到期日期': '2023/03/07', '最新發行量': 5000, '權證發行價': 0.691, '認購/售類別': '認購'}
#
#
# dict_stock_to_warrant:
#   stock_warrant_map.keys() = ['6548', '6568', '6582', '6589'...]
#   stock_warrant_map['6548'] = ['05184P', '05339P', '05360P'....]

def read_warrant_bible(path_file='權證達人寶典_NEWVOL_2022-07-15.xls') -> (dict, defaultdict[list]):
    # xls = pd.ExcelFile(r"權證達人寶典_NEWVOL_2022-06-29.xls")
    xls = pd.ExcelFile(path_file)

    # Parse Sheet 0: summary
    summary = xls.parse(0)

    name1 = list(summary.iloc[2])   # 權證
    name2 = list(summary.iloc[3])   # 代碼
    new_name = []
    # 合併這兩欄位
    for x, y in zip(name1, name2):
        new_name.append(x + y)

    df: pd.DataFrame = summary.copy()
    # 合併後的名稱變成欄位名稱，這樣才不會有重複
    df.columns = new_name
    df = df.iloc[4:, :]
    df.set_index('權證代碼', inplace=True)
    dict_warrant_to_info = df.to_dict(orient='index')

    dict_stock_to_warrant = defaultdict(list)

    for x in dict_warrant_to_info:
        code = dict_warrant_to_info[x]['標的代碼']
        dict_stock_to_warrant[code].append(x)

    # print(stock_warrant_map)
    return dict_warrant_to_info, dict_stock_to_warrant


if __name__ == '__main__':
    dict_warrant_to_info, dict_stock_to_warrant = read_warrant_bible('權證達人寶典_NEWVOL_2022-07-15.xls')
