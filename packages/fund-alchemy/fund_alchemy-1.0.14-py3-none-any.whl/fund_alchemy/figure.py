import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import colorsys
import fund_alchemy.general_tools as gt
from fund_alchemy.config import matplotlib_custom_style
plt.style.use(matplotlib_custom_style)


def comprehensive_analysis(series, rf=0.03):
    """计算基于净值序列的分析指标.

    parameters:
    ----------
    series -- 净值序列
    rf -- 无风险利率

    returns:
    dict, 各指标计算结果
    """

    annual_return, annual_volatility, max_drawdown, \
        sharpe_ratio, sortino_ratio, calmar_ratio \
        = gt.Calculate_Evaluation_Indicators(series, rf, ALL_Indicator=True)
    burke_ratio = gt.Calculate_Modified_Burke_Ratio(series, rf)
    proportion_of_high_days = gt.Calculate_days_for_highs(series)
    min_holding_weeks1 = gt.Calculate_days_for_target_win_rate(
        series, min_holding_days=4, target_win_rate=0.8)
    min_holding_weeks2 = gt.Calculate_days_for_target_win_rate(
        series, min_holding_days=4, target_win_rate=0.9)
    Var, CVar = gt.Calculate_Var(series)
    maxdrawdown_initial_date, reach_maxdrawdown_days, maxdrawdown_date,\
        recovery_days, recovery_date = gt.Max_Drawdown_Details(series)
    N, win_ratio, PnL_ratio = gt.calculate_PnL_ratio(series)

    return {
        '年化收益率': annual_return,
        '年化波动率': annual_volatility,
        '最大回撤': max_drawdown,
        '夏普比率': sharpe_ratio,
        '索提诺比率': sortino_ratio,
        '卡玛比率': calmar_ratio,
        '伯克比率': burke_ratio,
        '创新高周数占比': proportion_of_high_days,
        '八成胜率最小持有周数': min_holding_weeks1,
        '九成胜率最小持有周数': min_holding_weeks2,
        'Var-95%': Var,
        'CVar-95%': CVar,
        '最大回撤前高日期': maxdrawdown_initial_date,
        '最大回撤形成天数': reach_maxdrawdown_days,
        '最大回撤日期': maxdrawdown_date,
        '最大回撤恢复天数': recovery_days,
        '最大回撤恢复日期': recovery_date,
        '净值数目': N+1,
        '胜率(r>0)': win_ratio,
        '盈亏比(r>0/r<0)': PnL_ratio,
    }


def draw_overview(df, fre="w", years=["2020", '2021', "2022"],
                  color_pct_clip=(-5, 5), show_excess_return=False):
    """净值概览图.

    parameters:
    -----------
    df -- pd.DataFrame
        两列净值序列，index为datetime.date，第一列为产品净值，第二列为业绩基准
    fre -- str, "m/w/d"
        数据频率
    years -- list
        月度收益显示的年份
    color_pct_clip -- tuple
        颜色最深对应的涨跌幅上下限
    show_excess_return -- bool
        是否展示超额收益

    returns:
    ----------
    生成matplotlib中的figure
    """

    fre_dict = {'w': 12, "d": 63}

    benchmark = df.columns[1]
    name = df.columns[0]
    df = df.fillna(method='ffill').fillna(method='bfill')
    df[[name, benchmark]] /= df[[name, benchmark]].iloc[0, :]
    df['alpha'] = ((df[name].pct_change() - df[benchmark].pct_change()).fillna(0) + 1).cumprod()
    df['dd'] = df[name]/df[name].expanding().max() - 1
    df['v'] = (df[name].pct_change().dropna()
               .rolling(fre_dict[fre]).std()*(52)**(0.5)*100).round(decimals=2)
    df['v_bk'] = (df[benchmark].pct_change().dropna()
                  .rolling(fre_dict[fre]).std()*(52)**(0.5)*100).round(decimals=2)

    res = comprehensive_analysis(df[name])
    res_bk = comprehensive_analysis(df[benchmark])

    fig = plt.figure(figsize=(9.0551181, 4.5275591*1.25))
    gs = GridSpec(10, 4, figure=fig)
    ax1 = fig.add_subplot(gs[:4, :-1])
    ax2 = fig.add_subplot(gs[4:6, :-1], sharex=ax1)
    ax3 = fig.add_subplot(gs[6:8, :-1], sharex=ax1)
    ax4 = fig.add_subplot(gs[8:10, :-1])
    ax5 = fig.add_subplot(gs[:, -1])

    l1 = ax1.plot(df[name])
    l2 = ax1.plot(df[benchmark])
    if show_excess_return:
        ax1_twin = ax1.twinx()
        l3 = ax1_twin.plot(df['alpha'], '--', linewidth=0.5, color='black')
        ax1.legend(l1+l2+l3, [name, benchmark, '超额收益'], loc='upper left')
        ax1.spines['right'].set_visible(True)
        IR = gt.Calculate_IR(df[[name, benchmark]])
    else:
        ax1.legend(l1+l2, [name, benchmark], loc='upper left')
        IR = "NaN"

    ax2.stackplot(df.index, 100*df['dd'], color=(0.8, 0.8, 0.8, 1))
    ax2.legend(['动态回撤(%)'], loc='lower left')

    ax3.plot(df[['v', 'v_bk']])
    ax3.legend(['组合滚动3个月年化波动率', '基准滚动3个月年化波动率'], loc='upper left')

    df_monthly = gt.switch_df_date_fre(df[[name, benchmark]], fre="m")
    df_monthly = df_monthly.pct_change().iloc[1:, :]
    df_monthly['y'] = [str(i.year) for i in df_monthly.index]
    df_monthly['m'] = [str(i.month) for i in df_monthly.index]
    m1_raw = gt.kvalue2table(df_monthly, "m", name, "y")
    m2_raw = gt.kvalue2table(df_monthly, "m", benchmark, "y")

    m1 = pd.DataFrame(index=years, columns=[str(i) for i in range(1, 13)])
    for i in m1.index:
        for j in m1.columns:
            if (i in m1_raw.index) and (j in m1_raw.columns):
                m1.loc[i, j] = m1_raw.loc[i, j]
            else:
                m1.loc[i, j] = float("nan")

    m2 = pd.DataFrame(index=years, columns=[str(i) for i in range(1, 13)])
    for i in m2.index:
        for j in m2.columns:
            if (i in m2_raw.index) and (j in m2_raw.columns):
                m2.loc[i, j] = m2_raw.loc[i, j]
            else:
                m2.loc[i, j] = float("nan")

    m = pd.DataFrame()
    for i in range(len(m1)):
        m = pd.concat([m, m1.iloc[[i], :]])
        m = pd.concat([m, m2.iloc[[i], :]])

    m = m * 100
    m = m.astype(float).round(2)

    def color_transfer(value):
        if value == value:
            U = (1 - value) * 100
            S = 255
            L = 180
            rgb = colorsys.hls_to_rgb(U/255, L/255, S/255)
            rgb = tuple([round(i, 4) for i in rgb])
            return rgb
        else:
            return (1, 1, 1)

    colormap = m.clip(color_pct_clip[0], color_pct_clip[1]).copy()
    colormap = colormap.applymap(
        lambda x: x / (color_pct_clip[1] - color_pct_clip[0]) + 0.5
        ).values.tolist()
    for i in range(len(colormap)):
        for j in range(len(colormap[i])):
            colormap[i][j] = color_transfer(colormap[i][j])

    m = m.applymap(lambda x: str(x)+"%").replace("nan%", "").values.tolist()
    rowLabels = ["%s-%s" % (x, y) for y in years for x in ['策略', '基准']]
    ax4.table(
        cellText=m,
        rowLabels=rowLabels,
        rowLoc='center',
        colLabels=["%s月" % i for i in range(1, 13)],
        colWidths=[0.077 for i in range(12)],
        cellColours=colormap,
        cellLoc='center',
        loc='upper right')
    ax4.set_axis_off()

    colLabels = ['基金表现', '比较基准']
    rowLabels = list(res)


    cellText = [['%.2f%%' % (100*res['年化收益率']), '%.2f%%' % (100*res_bk['年化收益率'])],
                ['%.2f%%' % (100*res['年化波动率']), '%.2f%%' % (100*res_bk['年化波动率'])],
                ['%.2f%%' % (100*res['最大回撤']), '%.2f%%' % (100*res_bk['最大回撤'])],
                ['%.2f' % res['夏普比率'], '%.2f' % res_bk['夏普比率']],
                ['%.2f' % res['索提诺比率'], '%.2f' % res_bk['索提诺比率']],
                ['%.2f' % res['卡玛比率'], '%.2f' % res_bk['卡玛比率']],
                ['%.2f' % res['伯克比率'], '%.2f' % res_bk['伯克比率']],
                ['%.2f%%' % res['创新高周数占比'], '%.2f%%' % res_bk['创新高周数占比']],
                ['%.0f' % res['八成胜率最小持有周数'], '%.0f' % res_bk['八成胜率最小持有周数']],
                ['%.0f' % res['九成胜率最小持有周数'], '%.0f' % res_bk['九成胜率最小持有周数']],
                ['%.2f%%' % (100*res['Var-95%']), '%.2f%%' % (100*res_bk['Var-95%'])],
                ['%.2f%%' % (100*res['CVar-95%']), '%.2f%%' % (100*res_bk['CVar-95%'])],
                ['%s' % res['最大回撤前高日期'], '%s' % res_bk['最大回撤前高日期']],
                ['%.0f' % res['最大回撤形成天数'], '%.0f' % res_bk['最大回撤形成天数']],
                ['%s' % res['最大回撤日期'], '%s' % res_bk['最大回撤日期']],
                ['%.0f' % res['最大回撤恢复天数'], '%.0f' % res_bk['最大回撤恢复天数']],
                ['%s' % res['最大回撤恢复日期'], '%s' % res_bk['最大回撤恢复日期']],
                ['%s' % res['净值数目'], '%s' % res_bk['净值数目']],
                ['%s' % res['胜率(r>0)'], '%s' % res_bk['胜率(r>0)']],
                ['%s' % res['盈亏比(r>0/r<0)'], '%s' % res_bk['盈亏比(r>0/r<0)']],
                ]

    if show_excess_return:
        rowLabels = rowLabels + ["信息比率"]
        cellText = cellText + [['%s' % IR, 'NaN']]

    ax5.table(
        cellText=cellText,
        rowLabels=rowLabels,
        rowLoc='center',
        colLabels=colLabels,
        colWidths=[0.8, 0.8],
        cellLoc='center',
        loc='upper left')
    ax5.set_axis_off()

    plt.subplots_adjust(left=0.06, right=0.9, top=0.9, bottom=0.05,
                        wspace=1, hspace=0.15)

    return fig


if __name__ == '__main__':
    pass
