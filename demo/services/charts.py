# demo/services/charts.py
from typing import Dict, Any
from pyecharts import options as opts
from pyecharts.charts import Bar, Page
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts

def build_school_stats_table(year: int, area: str, stats: Dict[str, Dict[str, Any]]) -> Table:
    """
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
    schools = list(stats.keys())
    team_counts = [stats[s]['team_count'] for s in schools]

    bar = (
        Bar()
        .add_xaxis(schools)
        .add_yaxis(f"{year}年{area}参赛队伍数", team_counts)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年{area} 各学校参赛队伍数"),
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
    table = build_school_stats_table(year, area, stats)

    page.add(table, bar)
    return page.render_embed()
