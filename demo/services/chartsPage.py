# demo/services/charts.py
from typing import Dict, Any, List
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts

from demo.services.charts import build_area_detail_bar, build_area_participant_count_bar, build_school_stats_table, \
    build_range_year_report_first_prize_bar, build_range_year_report_first_prize_table


def get_range_year_area_report_page(
    start_year: int,
    end_year: int,
    area: str,
    stats
) -> str:
    """
    在 Django view 里调用，直接返回可嵌入的 HTML+JS。
    """
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_range_year_report_first_prize_bar(start_year, end_year, area, stats),
        build_range_year_report_first_prize_table(start_year, end_year, area, stats)
    )
    return page.render_embed()



def get_area_detail_page(year: int, area: str, stats: Dict[str, Dict[str, Any]]) -> str:
    """
    将柱状图和带“赛区”列的表格放到同一个 Page，返回 render_embed() 的片段。
    """
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_school_stats_table(year, area, stats),
        build_area_detail_bar(year, area, stats),
        build_area_participant_count_bar(year, area, stats)
    )
    return page.render_embed()



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
    # data_by_year: Dict[int, Dict[str, Dict[str, int]]] = (
    #     get_school_yearly_stats_range(start_year, end_year, area)
    # )
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

    # 7. 放到同一个 Page
    page = Page(layout=Page.SimplePageLayout)
    page.add(bar, table)
    return page