# demo/services/charts.py
from typing import Dict, Any, List
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts


def build_school_stats_table(
        year: int,
        area: str,
        stats: Dict[str, Dict[str, Any]]
) -> Table:
    """
    生成xx年xx赛区各个学校统计表格，包含各校的参赛队伍数、获奖率等信息。
    构造一个 pyecharts Table，列：
    学校名称 | 赛区 |
    {year}年参赛队伍数量 |
    {year}年获奖率 |
    {year}年分赛区一等奖获奖队数量 |
    {year}年分赛区一等奖获奖率 |
    {year}年分赛区二等奖获奖队数量 |
    {year}年分赛区二等奖获奖率 |
    {year}年晋级率 |
    {year}年决赛一等奖获奖率
    """
    headers = [
        "学校名称",
        "赛区",
        f"{year}年参赛队伍数量",
        f"{year}年获奖率",
        f"{year}年分赛区一等奖获奖队数量",
        f"{year}年分赛区一等奖获奖率",
        f"{year}年分赛区二等奖获奖队数量",
        f"{year}年分赛区二等奖获奖率",
        f"{year}年晋级率",
        f"{year}年决赛一等奖获奖率",
    ]

    rows = []
    for school, data in stats.items():
        tc = data.get('team_count', 0)
        ac = data.get('award_count', 0)
        fp = data.get('first_prize_count', 0)
        sp = data.get('second_prize_count', 0)
        qc = data.get('qualification_count', 0)
        ff = data.get('final_first_prize_count', 0)

        def pct(part, whole):
            return f"{round(part / whole * 100, 2)}%" if whole else "0%"

        rows.append([
            school,
            area,
            tc,
            pct(ac, tc),
            fp,
            pct(fp, tc),
            sp,
            pct(sp, tc),
            pct(qc, tc),
            pct(ff, tc),
        ])

    table = Table()
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(title=f"{year}年{area}学校统计表")
    )
    return table


def build_area_detail_bar(year: int, area: str, stats: Dict[str, Dict[str, Any]]) -> Bar:
    """
    构造柱状图，显示各学校的参赛队伍数。
    :param year: 年份
    :param area: 赛区
    :param stats: 统计数据
    :return: 柱状图
    """
    schools = list(stats.keys())
    team_counts = [stats[s]['team_count'] for s in schools]

    bar = (
        Bar()
        .add_xaxis(schools)
        .add_yaxis(f"{year}年{area}参赛队伍数", team_counts)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年{area}各学校参赛队伍数"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    )
    return bar

def build_area_participant_count_bar(year: int, area: str, stats: Dict[str, Dict[str, Any]]) -> Bar:
    """
    构造柱状图，显示各学校的参赛人员数。
    :param year: 年份
    :param area: 赛区
    :param stats: 统计数据
    :return: 柱状图
    """
    schools = list(stats.keys())
    team_counts = [stats[s]['participant_count'] for s in schools]

    bar = (
        Bar()
        .add_xaxis(schools)
        .add_yaxis(f"{year}年{area}参赛人员数", team_counts)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年{area}各学校参赛人员数"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    )
    return bar


def render_area_detail_chart(year: int, area: str, stats: Dict[str, Dict[str, Any]]) -> str:
    """
    将柱状图和带“赛区”列的表格放到同一个 Page，返回 render_embed() 的片段。
    """
    page = Page(layout=Page.SimplePageLayout)
    bar   = build_area_detail_bar(year, area, stats)
    participant_count_bar = build_area_participant_count_bar(year, area, stats)
    table = build_school_stats_table(year, area, stats)

    page.add(table, bar, participant_count_bar)
    return page.render_embed()

##############################################################################################################
def build_range_year_report_first_prize_bar(
    start_year: int,
    end_year: int,
    area: str,
    data_by_year
) -> Bar:
    """
    构造柱状图 + 两条折线：
      - 各年“分赛区一等奖获奖队数量”柱状
      - “五年总和”折线（Y 轴 0 左侧）
      - “平均获奖率”折线（Y 轴 1 右侧）
    """
    # 1. 拿到多年度数据
    # data_by_year = get_school_yearly_stats_range(start_year, end_year, area)
    years = list(range(start_year, end_year + 1))

    # 2. 汇总所有学校 & 计算五年总和与平均率
    schools = sorted(
        {s for stats in data_by_year.values() for s in stats},
        key=lambda s: sum(data_by_year[y].get(s, {}).get('first_prize_count', 0) for y in years),
        reverse=True
    )
    total_fp = {s: sum(data_by_year[y].get(s, {}).get('first_prize_count', 0) for y in years) for s in schools}
    total_tc = {s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)         for s in schools}
    avg_rate = {
        s: round(total_fp[s] / total_tc[s] * 100, 2) if total_tc[s] else 0.0
        for s in schools
    }

    # 3. 柱状图（每年 first_prize_count）
    bar = Bar()
    bar.add_xaxis(schools)
    for y in years:
        bar.add_yaxis(
            f"{y}年分赛区一等奖获奖队数量",
            [ data_by_year[y].get(s, {}).get('first_prize_count', 0) for s in schools ],
            label_opts=LabelOpts(is_show=True)
        )

    # 4. 左侧“汇总”折线
    bar.extend_axis(
        yaxis=AxisOpts(
            name="五年总和",
            position="right",
            axislabel_opts=LabelOpts(formatter="{value}")
        )
    )
    line_sum = (
        Line()
        .add_xaxis(schools)
        .add_yaxis(
            "五年总和",
            [ total_fp[s] for s in schools ],
            yaxis_index=1,
            label_opts=LabelOpts(is_show=True)
        )
    )
    bar.overlap(line_sum)

    # 5. 右侧“平均获奖率”折线
    line_rate = (
        Line()
        .add_xaxis(schools)
        .add_yaxis(
            "一等奖平均获奖率",
            [ avg_rate[s] for s in schools ],
            yaxis_index=1,
            label_opts=LabelOpts(
                is_show=True,
                formatter="{c}%"
            )
        )
    )
    bar.overlap(line_rate)

    # 6. 全局配置
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"{start_year}–{end_year} {area} 赛区各高校近五年分赛区一等奖获奖数量及平均获奖率"
        ),
        xaxis_opts=AxisOpts(axislabel_opts=LabelOpts(rotate=45)),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        legend_opts=opts.LegendOpts(pos_top="10%"),
    )
    return bar


def build_range_year_report_first_prize_table(
    start_year: int,
    end_year: int,
    area: str,
    data_by_year
) -> Table:
    """
    构造底部表格，列：
      学校名称 |
      {y}年获奖队数量… |
      五年总和 |
      平均获奖率
    """
    # data_by_year = get_school_yearly_stats_range(start_year, end_year, area)
    years = list(range(start_year, end_year + 1))

    # 1. 学校排序同上
    schools = sorted(
        {s for stats in data_by_year.values() for s in stats},
        key=lambda s: sum(data_by_year[y].get(s, {}).get('first_prize_count', 0) for y in years),
        reverse=True
    )
    total_fp = {s: sum(data_by_year[y].get(s, {}).get('first_prize_count', 0) for y in years) for s in schools}
    total_tc = {s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)         for s in schools}

    # 2. 表头
    headers = ["学校名称"] + [f"{y}年获奖队数量" for y in years] + ["五年总和", "平均获奖率"]

    # 3. 行数据
    rows = []
    for s in schools:
        row = [s]
        for y in years:
            row.append(data_by_year[y].get(s, {}).get('first_prize_count', 0))
        row.append(total_fp[s])
        rate = f"{round(total_fp[s]/total_tc[s]*100,2)}%" if total_tc[s] else "0%"
        row.append(rate)
        rows.append(row)

    table = (
        Table()
        .add(headers, rows)
        .set_global_opts(
            title_opts=ComponentTitleOpts(
                title=f"{area} 赛区各高校近五年分赛区一等奖获奖统计（表格）"
            )
        )
    )
    return table


def render_first_prize_chart(
    start_year: int,
    end_year: int,
    area: str,
    stats
) -> str:
    """
    在 Django view 里调用，直接返回可嵌入的 HTML+JS。
    """
    page = Page(layout=Page.SimplePageLayout)
    bar = build_range_year_report_first_prize_bar(start_year, end_year, area, stats)
    table = build_range_year_report_first_prize_table(start_year, end_year, area, stats)
    page.add(bar, table)
    return page.render_embed()

# 显示指定年份范围、赛区的各年参赛队伍数统计柱状图
def build_range_year_area_report_participant_count_bar(
    start_year: int,
    end_year: int,
    area: str,
    schools: List[str],
    years: List[int],
    data_by_year: Dict[int, Dict[str, Dict[str, int]]],
    total_map: Dict[str, int]
) -> Bar:
    # 3. 枚举年度柱状图
    bar = Bar(
        init_opts=opts.InitOpts(width='100%', height='600px')
    )
    bar.add_xaxis(schools)
    for y in years:
        bar.add_yaxis(
            f"{y}年参赛队伍数量",
            [data_by_year[y].get(s, {}).get('team_count', 0) for s in schools],
            label_opts=LabelOpts(is_show=True)
        )

    # 4. 添加右侧第二 Y 轴，并叠加汇总折线
    bar.extend_axis(
        yaxis=AxisOpts(
            name="五年汇总",
            position="right",
            axislabel_opts=LabelOpts(formatter="{value}")
        )
    )
    line = (
        Line()
        .add_xaxis(schools)
        .add_yaxis(
            "五年汇总",
            [total_map[s] for s in schools],
            yaxis_index=1,
            label_opts=LabelOpts(is_show=True)
        )
    )
    bar.overlap(line)

    # 5. 全局布局
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=f"{start_year}–{end_year} {area} 赛区队伍数对比"
        ),
        xaxis_opts=AxisOpts(axislabel_opts=LabelOpts(rotate=45)),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        legend_opts=opts.LegendOpts(pos_top="10%")
    )
    return bar

# 显示指定年份范围、赛区的各年参赛队伍数统计表
def build_range_year_area_report_participant_count_table(
    start_year: int,
    end_year: int,
    area: str,
    schools: List[str],
    years: List[int],
    data_by_year,
    total_map: Dict[str, int]
) -> Table:

    # 6. 构造底部表格
    headers = ["学校名称"] + [f"{y}年队伍数" for y in years] + ["五年总和"]
    rows = []
    for s in schools:
        row = [s] + [
            data_by_year[y].get(s, {}).get('team_count', 0)
            for y in years
        ] + [total_map[s]]
        rows.append(row)

    table = (
        Table()
        .add(headers, rows)
        .set_global_opts(
            title_opts=ComponentTitleOpts(title=f"{area} 赛区五年报名详情")
        )
    )
    return table

def render_area_range_chart(
    start_year: int,
    end_year: int,
    area: str,
    data_by_year
) -> Page:
    """
    生成【start_year–end_year 区间】【area 赛区】的五年队伍数多年度对比
    页面 HTML+JS（render_embed）。
    """
    # 1. 拿到多年度数据
    years: List[int] = sorted(data_by_year.keys())

    # 2. 汇总所有学校并按五年总和降序
    schools = list({
        s for stats in data_by_year.values() for s in stats
    })
    total_map = {
        s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)
        for s in schools
    }
    schools.sort(key=lambda s: total_map[s], reverse=True)

    # 7. 放到同一个 Page
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_range_year_area_report_participant_count_bar(
            start_year, end_year,
            area, schools, years, data_by_year, total_map
        ),
        build_range_year_area_report_participant_count_table(
            start_year, end_year,
            area, schools, years, data_by_year, total_map
        )
    )
    return page