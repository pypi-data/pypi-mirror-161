import pandas as pd
import numpy as np
import datetime as dt

# ==============================
# 常用自定义函数集
# Author: xxf
# 更新日期: 2021-12-13

# 函数目录:
# 1.kvalue2table -- 转换数据格式
# 2.ApplyFunc -- 替换变量
# 3.CutList -- 切分列表
# 4.d -- 将字符串日期格式转换为datetime.date
# 5.switcher -- 字符串与列表的互相转换
# 6.switch_df_date_fre -- 改变“日期”列频率
# 7.Calculate_Evaluation_Indicators -- 计算序列业绩
# 8.Calculate_days_for_target_win_rate -- 计算目标胜率最小持有天数
# 9.Calculate_IR -- 计算信息比率
# 10.GetRandomSample -- 有放回抽样
# 11.GetPercentile -- 返回特定值在样本中的分位数
# 12.MWRR -- 计算Money-weighted rate of return
# 13.get_rpt_date -- 获取目标日期最近的财报日(假定2,5,8,11披露)
# 14.get_current_rpt -- 获取目标日期当前所处的季度
# 15.get_last_month_end_date -- 获取目标日期最近一个月最后一天日期
# 16.Calculate_Modified_Burke_Ratio -- 计算修正伯克比率
# 17.Calculate_Var -- 计算VaR和CVaR
# 18.Max_Drawdown_Details -- 计算最大回撤细节
# 19.calculate_drawdown_max_days -- 计算水下最长天数
# 20.calculate_PnL_ratio -- 计算胜率和盈亏比
# 21.str_clearing -- 文本清洗
# 22.ym_ago -- 获取目标日期之前n个月或年的日期
# 23.detect_fre -- 检测序列的频率
# 24.drop_unstart -- 剔除产品净值未变动的区间
# 25.interpolate -- 直线内插法
# 26.find_date -- 从字符串中识别日期
# 27.table2value -- 转换数据格式
# ==============================


def kvalue2table(df, label='基金代码', variable=None, index='日期'):
    """用于转换key-value形式的数据至DataFrame.

    parameters:
    -----------
    df -- DataFrame
    label -- 分类列名
    variable -- 变量列名

    returns:
    --------
    pd.DataFrame
    """

    if variable is None:
        variable = df.columns[-1]
    CODEs = list(df[label].drop_duplicates())
    DATEs = sorted(list(df[index].drop_duplicates()))
    data = pd.DataFrame(index=DATEs)
    for code in CODEs:
        series = df[df[label] == code].set_index(index)[variable]
        series.name = code
        data = data.join(series)

    return data


def ApplyFunc(x, DICT, trans=None, fillna=float('nan')):
    """用于转换DataFrame中的数据, 配合apply函数使用.

    parameters:
    -----------
    x -- 需转换的变量.
    DICT -- dict, 对应的转换关系
    trans -- dict, 对结果的第二次转换
    fillna -- 缺省值填充值

    returns:
    --------
    value
    """

    try:
        if trans is None:
            return DICT[x]
        else:
            return trans[DICT[x]]
    except(Exception):
        return fillna


def CutList(L, n=500):
    '''将大列表L切分成每份数量为n的小列表们.

    parameters:
    -----------
    df -- pd.DataFrame, 净值数据
    fre -- 'w'/'m', 周频/月频
    date_index -- df中index是否为日期, 若否则需含一列命名为“日期”的序列.

    returns:
    --------
    df -- pd.DataFrame
    '''

    res = []
    for i in range(int(len(L)/n)+1):
        if len(L[i*n:(i+1)*n]) != 0:
            res.append(L[i*n:(i+1)*n])
    return res


def d(date, t='date'):
    '''将str的日期转化为dt.date或dt.datetime

    parameters:
    -----------
    date -- str, 日期
    t -- date/datetime

    returns:
    --------
    dt.date / dt.datetime
    '''

    if t == 'date':
        if '-' in date:
            return dt.datetime.strptime(date, "%Y-%m-%d").date()
        else:
            return dt.datetime.strptime(date, "%Y%m%d").date()
    elif t == 'datetime':
        if '-' in date:
            return dt.datetime.strptime(date, "%Y-%m-%d")
        else:
            return dt.datetime.strptime(date, "%Y%m%d")


def switcher(x, label=';'):
    """实现list与str的互相转换.

    Parameters:
    ----------
    x -- list/str
        列表或字符串
    label -- str
        分割符号

    returns:
    --------
    list / str
    """

    if type(x) == str:
        return x.split(label)
    elif type(x) == list:
        res = ''
        for i in range(len(x)):
            res += str(x[i])
            if i != len(x) - 1:
                res += label
        return res
    elif x != x:
        return []
    else:
        return x


def switch_df_date_fre(df, fre='w', date_index=True):
    '''转换日频净值数据为周/月频.

    parameters:
    -----------
    df -- pd.DataFrame, 净值数据
    fre -- 'w'/'m', 周频/月频
    date_index -- df中index是否为日期, 若否则需含一列命名为“日期”的序列.

    returns:
    --------
    df -- pd.DataFrame
    '''

    df = df.copy()
    shape = len(df.shape)

    if date_index is True:
        old_name = df.index.name
        df.index.name = '日期'
        df = df.reset_index()

    if fre == 'w':
        df['_slice'] = df['日期'].apply(lambda x: x.strftime("%Y%W"))
        first = df.iloc[0:1, :]
        last = df.iloc[-1:, :]
        mid = df.drop_duplicates(subset=['_slice'], keep='last')
        # df = first.append(mid).append(last).drop_duplicates()
        df = pd.concat([first, mid, last]).drop_duplicates()
        df = df.drop(['_slice'], axis=1).reset_index(drop=True)
    elif fre == 'm':
        df['_slice'] = df['日期'].apply(lambda x: x.strftime("%Y%m"))
        first = df.iloc[0:1, :]
        last = df.iloc[-1:, :]
        mid = df.drop_duplicates(subset=['_slice'], keep='last')
        # df = first.append(mid).append(last).drop_duplicates()
        df = pd.concat([first, mid, last]).drop_duplicates()
        df = df.drop(['_slice'], axis=1).reset_index(drop=True)

    if date_index:
        df = df.set_index('日期')
        df.index.name = old_name

    if shape == 2:
        return df.copy()
    else:
        return df[df.columns[0]].copy()


def Calculate_Evaluation_Indicators(series, rf=0.03, ALL_Indicator=False):
    '''函数用来计算年化收益率、年化波动率、最大回撤、夏普、索提诺、卡玛。

    parameters:
    -----------
    series -- pd.Series, index为dt.date的净值序列.
    rf -- 无风险利率.
    ALL_Indicator -- True/False, 是否添加索提诺和卡玛.

    returns:
    -------
    4或6个指标的tuple
    '''

    if len(series) < 5:
        if not ALL_Indicator:
            return 0, 0, 0, 0
        else:
            return 0, 0, 0, 0, 0, 0
    series = series.dropna().astype(float)
    series_original = series.copy()
    series = series.reset_index()
    series.columns = ['日期', '净值']
    series['_seq'] = series['日期'].apply(lambda x: int(x.strftime('%w')))
    series['_choose'] = False
    series.loc[0, '_choose'] = True
    for r in range(1, series.shape[0]-1):
        if series.loc[r, '_seq'] >= series.loc[r+1, '_seq']:
            series.loc[r, '_choose'] = True
    series.loc[series.shape[0]-1, '_choose'] = True
    series = series[series['_choose']]\
        .drop(['_seq', '_choose'], axis=1)\
        .set_index('日期')['净值']
    rr = round((
        (series.iloc[-1]/series.iloc[0])
        ** (365./(series.index[-1]-series.index[0]).days)
        - 1.), 4)
    std = round((series.pct_change().std()*np.sqrt(52.)), 4)
    if std != 0:
        sharpe = round((rr-rf)/std, 4)
    else:
        sharpe = 0
    maxdrawdown = round((
        1.-(series_original/series_original.expanding().max())
        ).max(), 4)
    if not ALL_Indicator:
        return rr, std, maxdrawdown, sharpe
    else:
        d_std = series.pct_change().dropna()\
            .apply(lambda x: min(x, 0)).std()*np.sqrt(52.)
        if d_std != 0:
            sortino = round((rr-rf)/d_std, 4)
        else:
            sortino = 0
        if maxdrawdown != 0:
            calmar = round(rr / maxdrawdown, 4)
        else:
            calmar = 0
        return rr, std, maxdrawdown, sharpe, sortino, calmar


def Calculate_days_for_target_win_rate(series, min_holding_days=20,
                                       target_win_rate=0.8, **kwargs):
    """用于计算X成胜率(区间收益大于0)所需要的最小持有天数.

    parameters:
    -----------
    series -- pd.Series, index为dt.date的净值序列.
    min_holding_days -- int, 最少持有天数
    target_win_rate -- float, 目标胜率.
    kwargs:
        ShowDistribution -- int, 持有天数

    return:
    -------
    day -- 最小持有天数
    series -- 滚动区间收益序列
    """

    df = series.copy()
    df = df.reset_index()
    df.columns = ['日期', '净值']
    rolling_return = {}

    day = 0
    for p in range(min_holding_days, len(df)-min_holding_days):
        rolling_return[p] = df['净值'] / df['净值'].shift(p) - 1
        if (rolling_return[p] > 0).map({True: 1, False: 0}).sum() \
                > target_win_rate*(len(df)-p):
            day = p
            break

        # df[p] = df['净值'] / df['净值'].shift(p) - 1
        # if (df[p] > 0).map({True: 1, False: 0}).sum() \
        #         > target_win_rate*(len(df)-p):
        #     day = p
        #     break

    if 'ShowDistribution' in kwargs:
        newframe = pd.DataFrame(rolling_return)
        print(newframe)
        df = df.merge(newframe, left_index=True, right_index=True)
        return (day, df[kwargs['ShowDistribution']])

    return day


def Calculate_days_for_highs(series):
    """用于计算创新高天数占总天数的比例.

    parameters:
    -----------
    series -- pd.Series, index为dt.date的净值序列.

    return:
    -------
    pct -- float, 创高新天数占比
    """

    df = series.copy()
    df = df.reset_index()
    df.columns = ['日期', '净值']

    days = len(df)-1
    df['new_high'] = (
        df['净值'] >= df['净值'].expanding().max()
        ).replace({True: 1, False: 0})
    pct = round(100*df['new_high'].sum() / days, 2)

    return pct


def Calculate_IR(df):
    """用于计算信息比率.

    parameters:
    -----------
    df -- pd.DataFrame, 包含两列的表, index为日期, 第二列为净值序列, 第三列为基准序列.

    return:
    -------
    IR -- float, 信息比率
    """

    df = df.copy()
    df.columns = ['净值', '基准']
    df = df.astype(float).pct_change(fill_method=None)
    df['active_return'] = df['净值'] - df['基准']
    IR = df['active_return'].mean() / df['active_return'].std()

    return round(IR, 4)


def GetRandomSample(sample):
    """有放回抽样.

    parameters:
    -----------
    sample -- list, 样本

    return:
    -------
    RES -- list, 有放回随机抽样样本
    """

    N = len(sample)
    rdm = np.random.random(N)*N
    RES = [sample[int(i)] for i in rdm]
    return RES


def GetPercentile(x, sample):
    """返回特定值在样本中的分位数.

    parameters:
    -----------
    x -- 特定值
    sample -- list, 样本

    return:
    -------
    pct -- float, 分位数
    """

    sample = sorted(sample)
    for i in range(len(sample)):
        if x >= sample[i]:
            pass
        else:
            return float(i)/len(sample)
        if i == len(sample) - 1:
            return 1


def MWRR(df, start_ret=-1, end_ret=1, error=0.00001):
    """计算Money-weighted rate of return, 适用场景如基金定投的收益计算.

    parameters:
    -----------
    cash_flows -- pd.Series, index为日期, 值为现金流数值
    end_date -- dt.datetime, 期末日期
    end_asset -- float, 期末资产
    start_ret -- float, 年化收益率测试起始值
    end_ret -- float, 年化收益率测试终止值
    error -- float, 计算精度

    return:
    -------
    float, MWRR
    """

    df = df.reset_index()
    df.columns = ['date', 'nav', 'inflow']
    df.loc[0, 'shares'] = df.loc[0, 'inflow'] / df.loc[0, 'nav']
    for r in df.index[1:]:
        df.loc[r, 'shares'] = \
            df.loc[r, 'inflow'] / df.loc[r, 'nav'] + df.loc[r - 1, 'shares']
    df['mv'] = df['nav'] * df['shares']
    cash_flows = df.set_index('date')['inflow']
    end_date = df['date'].iloc[-1]
    end_asset = df['mv'].iloc[-1]

    def f(r0, r1):
        diff0 = 0
        ret0 = 0
        for ret in np.linspace(r0, r1, 3):
            SUM = 0
            for i in range(len(cash_flows)):
                cash = cash_flows.iloc[i]
                date = cash_flows.index[i]
                d = (end_date - date).days
                SUM += cash*(1+ret)**(d/365)
            diff = SUM - end_asset
            if diff * diff0 < 0:
                return ret0, ret
            else:
                diff0 = diff
                ret0 = ret
        return None

    check_range = f(start_ret, end_ret)
    if check_range is None:
        print('Out of range!')
        return
    else:
        a, b = check_range
        while 1:
            if b - a <= error:
                return round((a+b)/2, 4), end_asset
            else:
                a, b = f(a, b)


def get_rpt_date(date, fisicalyear=False, str_output=True):
    """获取目标日期最近的财报日(假定2,5,8,11披露).

    parameters:
    -----------
    date -- str, 日期
    fisicalyear -- bool, 是否获取财年
    str_output -- bool, 是否返回str日期

    return:
    -------
    str, 财报日期
    """

    if type(date) == str:
        y = date[:4]
        date = d(date)
    else:
        y = str(date.year)

    if fisicalyear:
        if date < d(y + '0331'):
            output = str(int(y)-2) + '1231'
        else:
            output = str(int(y)-1) + '1231'
    else:
        if date < d(y + '0201'):
            output = str(int(y)-1)+'0930'
        elif date < d(y + '0501'):
            output = str(int(y)-1)+'1231'
        elif date < d(y + '0801'):
            output = y + '0331'
        elif date < d(y + '1101'):
            output = y + '0630'
        else:
            output = y + '0930'

    if str_output:
        return output
    else:
        return d(output)


def get_current_rpt(date, str_output=False):
    """获取目标日期当前所处的季度.

    parameters:
    -----------
    date -- str, 日期
    str_output -- bool, 是否返回str日期

    return:
    -------
    str / dt.date
    """

    if type(date) == str:
        y = date[:4]
        date = d(date)
    else:
        y = str(date.year)

    if date <= d(y + '0331'):
        output = y + '0331'
    elif date <= d(y + '0630'):
        output = y + '0630'
    elif date <= d(y + '0930'):
        output = y + '0930'
    elif date <= d(y + '1231'):
        output = y + '1231'

    if str_output:
        return output
    else:
        return d(output)


def get_last_month_end_date(date, str_output=True):
    """获取目标日期最近一个月最后一天日期.

    parameters:
    -----------
    date -- str, 日期
    str_output -- bool, 是否返回str日期

    return:
    -------
    str / dt.date
    """

    if type(date) == str:
        y = int(date[:4])
        m = int(date[4:6])
        date = d(date)
    else:
        y = date.year
        m = date.month
    output = (dt.datetime(y, m, 1) - dt.timedelta(days=1)).date()
    if str_output:
        return output.strftime('%Y%m%d')
    else:
        return output


def Calculate_Modified_Burke_Ratio(series, rf):
    """计算修正伯克比率.

    parameters:
    -----------
    series -- pd.Series, 净值序列
    rf -- float, 无风险利率

    return:
    -------
    float, round 4
    """

    if len(series) < 5:
        return float('nan')
    series = series.dropna().astype(float)
    dd = series/series.expanding().max() - 1.
    mssd = ((dd**2).sum()/len(dd))**(0.5)
    if mssd == 0:
        return 999
    rr = ((series.iloc[-1]/series.iloc[0])
          ** (365./(series.index[-1]-series.index[0]).days)
          - 1.)
    return round((rr - rf)/mssd, 4)


def Calculate_Var(series, a=0.05, pct=False):
    """计算Historical Value at Risk历史在险价值.

    parameters:
    -----------
    series -- pd.Series, 净值/收益率序列
    a -- float, 置信度
    pct -- bool, 输入的序列是涨跌还是净值

    return:
    -------
    Var, CVar
    """
    if len(series) > 20:
        if pct:
            r = series.dropna().sort_values().reset_index(drop=True)
        else:
            r = series.pct_change().dropna().sort_values().reset_index(drop=True)
        threshold = int(len(r)*a)-1
        Var = r.loc[threshold]
        CVar = r[:threshold].mean()

        return round(Var, 4), round(CVar, 4)

    else:
        return float("nan"), float("nan")


def Max_Drawdown_Details(series):
    """计算最大回撤细节.

    parameters:
    -----------
    series -- pd.Series, 净值序列

    return:
    -------
    maxdrawdown_initial_date, reach_maxdrawdown_days, maxdrawdown_date,
    recovery_days, recovery_date
    """

    drawdown = 1. - series/series.expanding().max()
    maxdrawdown = drawdown.max()
    maxdrawdown_date = drawdown[drawdown == maxdrawdown].index[-1]

    drawdown1 = drawdown[:maxdrawdown_date]
    maxdrawdown_initial_date = drawdown1[drawdown1 == 0].index[-1]
    reach_maxdrawdown_days = (maxdrawdown_date - maxdrawdown_initial_date).days

    drawdown2 = drawdown[maxdrawdown_date:]
    if (drawdown2 == 0).sum() > 0:
        recovery_date = drawdown2[drawdown2 == 0].index[0]
        recovery_days = (recovery_date - maxdrawdown_date).days
        recovery_date = recovery_date.strftime('%Y%m%d')
    else:
        recovery_date = float('nan')
        recovery_days = float('nan')

    return maxdrawdown_initial_date.strftime('%Y%m%d'), \
        reach_maxdrawdown_days, maxdrawdown_date.strftime('%Y%m%d'),\
        recovery_days, recovery_date


def calculate_drawdown_max_days(series):
    """计算水下最长天数.

    parameters:
    -----------
    series -- pd.Series, 净值序列

    return:
    -------
    drawdown_max_days, drawdown_max_days_recovery_date
    """

    drawdown = 1. - series/series.expanding().max()
    res = pd.DataFrame()
    last_high = drawdown.index[0]
    for date in drawdown.index:
        if drawdown.loc[date] == 0:
            last_high = date
            res.loc[date, 'drawdown_days'] = 0
        else:
            res.loc[date, 'drawdown_days'] = (date - last_high).days

    return int(res['drawdown_days'].max()), \
        res[res['drawdown_days'] == res['drawdown_days'].max()].index[-1]


def calculate_PnL_ratio(series, target=0):
    """计算胜率和盈亏比.

    parameters:
    -----------
    series -- pd.Series, 净值序列

    return:
    -------
    N, 收益率数量 
    win_ratio, 收益率大于target的占比
    PnL_ratio, 收益率大于target的收益与小于target的收益的比值
    """

    r = series.dropna().pct_change().dropna()
    N = len(r)
    win_ratio = r.loc[lambda x: x > target].count() / N
    PnL_ratio = -1*r.loc[lambda x: x > target].mean() \
        / r.loc[lambda x: x < target].mean()

    return N, round(win_ratio, 4), round(PnL_ratio, 4)


def str_clearing(text):
    """文本清洗.

    parameters:
    -----------
    text -- str, 文本信息

    return:
    -------
    str
    """

    def remove_items(text, symbol):
        a = text.split(symbol)
        b = ''
        for i in a:
            b += i
        return b

    text = remove_items(text, '\n')
    text = remove_items(text, '\r')
    text = remove_items(text, ' ')

    return text


def ym_ago(date, distance, Type, output="date"):
    """获取目标日期之前n个月或年的日期(日期推算).

    parameters:
    -----------
    date -- dt.date, 目标日期
    distance -- float, 距离
    Type -- "m"/"y", 月或年
    output -- "date"/"str/"datetime", 返回类型

    return:
    -------
    dt.date/str/dt.datetime
    """

    y, m, d = date.year, date.month, date.day
    if Type == 'm':
        m1 = m - distance
        if m1 <= 0:
            m1 = 12 + m1
            y1 = y - 1
            d1 = d
        else:
            m1 = m1
            y1 = y
            d1 = d
    elif Type == 'y':
        y1 = y - distance
        m1 = m
        d1 = d
    if output == 'date':
        return dt.datetime(y1, m1, d1).date()
    elif output == "str":
        return dt.datetime(y1, m1, d1).strftime("%Y%m%d")
    elif output == "datetime":
        return dt.datetime(y1, m1, d1)


def detect_fre(series):
    '''检测序列的频率.

    parameters:
    -----------
    series -- pd.Series, 以datetime.date为index的序列.

    returns:
    --------
    str, "d/w/m", 频率
    '''

    if (np.mean([i.day for i in series.index[-3:]]) >= 26) \
            and (series.index[-1].month != series.index[-2].month):
        return 'm'
    elif np.mean([i.weekday() for i in series.index[-12:]]) >= 3.5:
        return 'w'
    else:
        return 'd'


def drop_unstart(series, threshold=0.0001):
    '''剔除产品备案至实际运作这段净值未变动的区间.

    parameters:
    -----------
    series -- pd.Series, 以datetime.date为index的序列.

    returns:
    --------
    pd.Series
    '''

    if len(series) > 0:
        nav0 = series.iloc[0]
        need_to_drop = -1
        for i in series.index[1:]:
            nav_i = series.loc[i]
            need_to_drop += 1
            if abs(nav_i - nav0) <= threshold:
                pass
            else:
                break
        if need_to_drop == 0:
            pass
        else:
            series = series[need_to_drop-1:]

    return series


def interpolate(v0, v1, N):
    """直线内插法.

    parameters:
    ----------
    v0 -- 起始值
    v1 -- 终止值
    N -- 点位数目

    return:
    ----------
    list
    """

    d = (v1 - v0)/(N+1)
    s = [v0]
    for i in range(N):
        s.append(v0+(i+1)*d)
    s.append(v1)

    return s


def find_date(string):
    """从字符串中识别日期.

    Parameters:
    ----------
    string -- str, 字符串

    Return:
    ----------
    datetime.date or None, 日期
    """

    import re
    res = re.search(r"\d{4}-\d{1,2}-\d{1,2}", string)
    if res is not None:
        y, m, d = res.group(0).split("-")
        return dt.datetime(int(y), int(m), int(d)).date()
    res = re.search(r"\d{4}/\d{1,2}/\d{1,2}", string)
    if res is not None:
        y, m, d = res.group(0).split("/")
        return dt.datetime(int(y), int(m), int(d)).date()
    res = re.search(r"\d{4}[0,1]{1}\d{1}\d{2}", string)
    if res is not None:
        y, m, d = res.group(0)[:4], res.group(0)[4:6], res.group(0)[6:]
        return dt.datetime(int(y), int(m), int(d)).date()
    res = re.search(r"\d{4}年\d{1,2}月\d{1,2}日", string)
    if res is not None:
        res = res.group(0)
        res = res.replace("年", "-")
        res = res.replace("月", "-")
        res = res.replace("日", "")
        y, m, d = res.split("-")
        return dt.datetime(int(y), int(m), int(d)).date()
    return None


def table2kvalue(table, index_name, column_name, value_name):
    """用于转换DataFrame形式的数据至key-value.

    parameters:
    -----------
    table -- DataFrame
    index_name -- 索引类别名称
    column_name -- 列类别名称
    value_name -- 值名称

    returns:
    --------
    pd.DataFrame
    """

    df = pd.DataFrame()
    table.index.name = index_name
    for col in table.columns:
        c = table[[col]].reset_index().rename(columns={col: value_name})
        c[column_name] = col
        df = df.append(c, ignore_index=True)

    return df


if __name__ == '__main__':

    pass
