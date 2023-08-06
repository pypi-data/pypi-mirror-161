import pandas as pd
import datetime as dt
import pickle
import fund_alchemy.general_tools as gt
from fund_alchemy.config import custodian_config


class standard_custodian_table:
    """将各托管估值表数据标准化.

    Parameters:
    ----------
    custodian -- str
        目前包括：中信银行/招商证券/海通证券/中信建投/中信期货
    filepath -- str
        数据文件路径

    Attributes:
    ----------
    数据具体字段包括:
        1. name -- 产品名称
        2. date -- 估值表日期
        3. main_body -- 主体部分(标的明细)
        4. shares -- 产品份额
        5. total_assets -- 总资产
        6. total_liabilities -- 总负债
        7. nav -- 单位净值
        8. cum_nav -- 累计单位净值
        9. raw -- 原始数据(原估值表)
        10. mode -- 估值表匹配模式
        11. data -- dict, 前10项整合
    """

    def __init__(self, filepath, custodian=None):
        config = pickle.loads(custodian_config)
        cus = config['custodian'].set_index("idx")
        mode_params = config['mode'].set_index("mode")
        headers = config['header'].set_index("header")
        custodian_mode_map = {}
        for mode in cus['mode'].drop_duplicates():
            custodian_mode_map[mode] = list(cus[cus['mode'] == mode]['custodian'])

        self.MODEs = {}
        for mode in mode_params.index:
            self.MODEs[mode] = {}
            self.MODEs[mode]['header'] = \
                headers.loc[mode_params.loc[mode, 'header'], :]
            self.MODEs[mode]['code_map'] = \
                config[mode_params.loc[mode, 'account_code_map']]

        Found = False
        if custodian is None:
            # 尝试识别
            for mode in custodian_mode_map:
                if not Found:
                    try:
                        exec("a = self.%s(filepath)" % mode)
                        data = locals()["a"]
                        Found = True
                        data['mode'] = mode
                        print("mode matched, mode = %s" % mode)
                    except(Exception):
                        pass
            if Found:
                pass
            else:
                print("no mode matched.")
        else:
            for mode in custodian_mode_map:
                if custodian in custodian_mode_map[mode]:
                    exec("a = self.%s(filepath)" % mode)
                    data = locals()["a"]
                    Found = True
                    data['mode'] = mode
                    break

        if Found:
            self.fund_name = data['fund_name']
            self.date = data['inner_date']
            self.main_body = data['main_body']
            self.shares = data['shares']
            self.total_assets = data['total_assets']
            self.total_liabilities = data['total_liabilities']
            self.nav = data['nav']
            self.cum_nav = data['cum_nav']
            self.raw = data['raw']
            self.mode = data['mode']
            self.data = data

    def __repr__(self):
        pr = ""
        pr += "========================================\n"
        for i in self.data:
            if i not in ["raw", "main_body"]:
                pr += "%-20s %-20s\n" % (i, self.data[i])
        pr += "============ main_body ================\n"
        pr += str(self.data['main_body']) + "\n"
        pr += "========================================\n"

        return pr

    def mode1(self, filepath):
        xml = open(filepath, 'r', encoding="utf-8").read()
        data = {}
        lines = xml.split("<Table ss")[-1].split("</Table>")[0].split("</Row>")
        body_index = []
        for i in range(len(lines)):
            if "</Data></Cell>" in lines[i]:
                lines[i] = lines[i].split("</Data></Cell>")
                for j in range(len(lines[i])):
                    lines[i][j] = lines[i][j].split(">")[-1]
            else:
                lines[i] = []
            if len(lines[i]) == 12:
                body_index.append(i)

        data["fund_name"] = lines[1][0].replace("__估值表", "")
        data["inner_date"] = dt.datetime.strptime(lines[2][0], "%Y-%m-%d").date()
        df = pd.DataFrame(
            data=lines[body_index[0]:body_index[-1] + 1],
            columns=['c1', '科目代码', '科目名称', '数量', '单位成本',
                     '成本', '成本占净值比（％）', '行情收市价', '市值',
                     '市值占净值比（％）', '估值增值', 'c2']
        ).drop(['c1', 'c2'], axis=1)
        df[df.columns[2:]] = df[df.columns[2:]].applymap(
            lambda x: float(x) if x != "" else float('nan'))
        m = self.MODEs["mode1"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['mv_pct'] = df['mv_pct'] / 100  # 百分数变小数
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)
        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(lines[body_index[-1] + 3][1])
        data['total_assets'] = float(lines[body_index[-1] + 6][3])
        data['total_liabilities'] = float(lines[body_index[-1] + 7][3])
        data['nav'] = float(lines[body_index[-1] + 10][2])
        data['cum_nav'] = float(lines[body_index[-1] + 11][2])

        return data

    def mode2(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[0, 0].split("_")[1]
        data['inner_date'] = gt.find_date(xls.loc[0, 0])

        header1 = xls.loc[4, :]
        header2 = xls.loc[5, :]
        header = []
        for i in range(len(header1)):
            if header1[i] == header2[i]:
                header.append(header1[i])
            else:
                header.append(header1[i] + "-" + header2[i])
        last_idx = (xls.isnull().sum(axis=1) == xls.shape[1])\
            .loc[lambda x: x == True].index[-2]  # noqa: E712
        df = xls[7:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode2"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['account_code'] = df['account_code'].apply(
            lambda x: str(x).split(" ")[0].replace(".", ""))
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 4])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产合计"]).index[0], 11])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债合计"]).index[0], 11])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "今日单位净值"]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值"]).index[0], 1])

        return data

    def mode3(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[1, 0].split("___")[1]
        data['inner_date'] = gt.find_date(xls.loc[2, 7])

        header = xls.loc[3, :]
        last_idx = (xls.isnull().sum(axis=1) == xls.shape[1])\
            .loc[lambda x: x == True].index[0]  # noqa: E712
        df = xls[4:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode3"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['mv_pct'] = df['mv_pct'] / 100  # 百分数变小数
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)
        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 4])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产类合计:"]).index[0], 7])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债类合计:"]).index[0], 7])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "今日单位净值："]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值:"]).index[0], 1])

        return data

    def mode4(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[1, 0].split("___")[1]
        data['inner_date'] = gt.find_date(xls.loc[2, 0])

        header = xls.loc[3, :]

        df = xls[4:].copy().reset_index(drop=True)
        last_idx = (xls.isnull().sum(axis=1) == xls.shape[1])\
            .loc[lambda x: x == True].index[0]  # noqa: E712
        df = xls[4:last_idx].copy().reset_index(drop=True)
        df.columns = header

        m = self.MODEs["mode4"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['mv_pct'] = df['mv_pct'] / 100  # 百分数变小数
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 4])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产类合计:"]).index[0], 7])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债类合计:"]).index[0], 7])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "基金单位净值："]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值:"]).index[0], 1])

        return data

    def mode5(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[2, 0].split("_")[-2]
        data['inner_date'] = gt.find_date(xls.loc[0, 0])

        header1 = xls.loc[4, :]
        header2 = xls.loc[5, :]
        header = []
        for i in range(len(header1)):
            if header1[i] == header2[i]:
                header.append(header1[i])
            else:
                header.append(header1[i] + "-" + header2[i])
        last_idx = (xls.isnull().sum(axis=1) == xls.shape[1])\
            .loc[lambda x: x == True].index[-2]  # noqa: E712
        df = xls[7:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode5"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['account_code'] = df['account_code'].apply(
            lambda x: str(x).split(" ")[0].replace(".", ""))
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 2])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产合计"]).index[0], 7])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债合计"]).index[0], 7])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "今日单位净值"]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值"]).index[0], 1])

        return data

    def mode6(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[2, 0].split("__")[-2]
        data['inner_date'] = gt.find_date(xls.loc[0, 0])

        header = xls.loc[4, :]

        last_idx = (xls[0].loc[lambda x: x == "证券投资合计"]).index[0] - 1

        df = xls[7:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode6"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['account_code'] = df['account_code'].apply(
            lambda x: str(x).split(" ")[0].replace(".", ""))
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 2])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产合计"]).index[0], 7])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债合计"]).index[0], 7])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "今日单位净值"]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值"]).index[0], 1])

        return data

    def mode7(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        data['fund_name'] = xls.loc[1, 1].split("___")[-2]
        data['inner_date'] = gt.find_date(xls.loc[2, 1])

        header = xls.loc[3, :]
        last_idx = (xls[1].loc[lambda x: x == "证券投资合计:"]).index[0] - 1
        df = xls[4:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode7"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]

        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[1].loc[lambda x: x == "实收资本"]).index[0], 3])
        data['total_assets'] = float(
            xls.loc[(xls[1].loc[lambda x: x == "资产类合计:"]).index[0], 8])
        data['total_liabilities'] = float(
            xls.loc[(xls[1].loc[lambda x: x == "负债类合计:"]).index[0], 8])
        data['nav'] = float(
            xls.loc[(xls[1].loc[lambda x: x == "基金单位净值："]).index[0], 2])
        data['cum_nav'] = float(
            xls.loc[(xls[1].loc[lambda x: x == "累计单位净值:"]).index[0], 2])

        return data

    def mode8(self, filepath):
        xls = pd.read_excel(filepath, header=None)
        data = {}
        print(xls)
        data['fund_name'] = xls.loc[2, 0].split("_")[1]
        data['inner_date'] = gt.find_date(xls.loc[0, 0])

        header1 = xls.loc[5, :]
        header2 = xls.loc[6, :]
        header = []
        for i in range(len(header1)):
            if header1[i] == header2[i]:
                header.append(header1[i])
            else:
                header.append(header1[i] + "-" + header2[i])
        last_idx = (xls.isnull().sum(axis=1) == xls.shape[1])\
            .loc[lambda x: x == True].index[-2]  # noqa: E712
        df = xls[7:last_idx].copy().reset_index(drop=True)
        df.columns = header
        m = self.MODEs["mode2"]
        h = dict(zip(m['header'], m['header'].index))
        df = df.rename(columns=h)[list(h.values())]
        df['account_code'] = df['account_code'].apply(
            lambda x: str(x).split(" ")[0].replace(".", ""))
        df['date'] = data["inner_date"]
        data['raw'] = df.copy()

        c = m['code_map'].dropna(subset=['含标的'])
        underlyings = pd.DataFrame()
        for item in c['资产类别'].drop_duplicates():
            unit = df[df['account_code'].apply(
                lambda x:
                    len(x) > 8
                    and
                    x[:8] in list(c[c['资产类别'] == item]['account_code'])
            )].copy()
            unit['level3_code'] = unit['account_code'].apply(lambda x: x[:8])
            unit['code'] = unit['account_code'].apply(lambda x: x[8:])
            unit['asset_class'] = item
            underlyings = pd.concat([underlyings, unit], ignore_index=True)

        underlyings['date'] = data['inner_date']
        underlyings['fund_name'] = data['fund_name']
        underlyings.columns.name = None
        data['main_body'] = underlyings

        data['shares'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "实收资本"]).index[0], 4])
        data['total_assets'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "资产合计"]).index[0], 9])
        data['total_liabilities'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "负债合计"]).index[0], 9])
        data['nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "单位净值"]).index[0], 1])
        data['cum_nav'] = float(
            xls.loc[(xls[0].loc[lambda x: x == "累计单位净值"]).index[0], 1])

        return data


if __name__ == '__main__':
    pass
