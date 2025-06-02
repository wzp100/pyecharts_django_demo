# demo/services/charts.py
# from typing import Dict, Any, List
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts

from demo.services.charts import build_area_team_count_bar, build_area_participant_count_bar, build_school_stats_table, \
    build_range_year_report_first_prize_bar, build_range_year_report_first_prize_table


def get_range_year_area_report_page(
    start_year: int,
    end_year: int,
    area: str,
    stats_data=None,
    use_cache: bool = True
) -> str:
    """
    在 Django view 里调用，直接返回可嵌入的 HTML+JS。
    
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 预先计算的统计数据，如果为None则自动计算
    :param use_cache: 是否使用缓存（当stats_data为None时有效）
    :return: 可嵌入的HTML+JS代码
    """
    # from demo.services.statistics import get_multi_year_stats_data
    #
    # 如果没有提供stats_data，则自动计算
    # if stats_data is None:
    #     stats_data = get_multi_year_stats_data(start_year, end_year, area, use_cache)
    #     data_by_year = stats_data['data_by_year']
    # else:
    #     data_by_year = stats_data
    #
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_range_year_report_first_prize_bar(start_year, end_year, area, stats_data),
        build_range_year_report_first_prize_table(start_year, end_year, area, stats_data)
    )
    return page.render_embed()



def get_area_detail_page(
    year: int,
    area: str,
    stats_data=None,
    use_cache: bool = True
) -> str:
    """
    将柱状图和带"赛区"列的表格放到同一个 Page，返回 render_embed() 的片段。
    
    :param year: 年份
    :param area: 赛区名称
    :param stats_data: 预先计算的统计数据，如果为None则自动计算，
                     可以是get_school_stats_data返回的完整统计数据，
                     也可以是原始统计数据格式 {school: {team_count: int, ...}, ...}
    :param use_cache: 是否使用缓存（当stats_data为None时有效）
    :return: 可嵌入的HTML+JS代码
    """
    # from demo.services.statistics import get_school_stats_data, get_area_full_stats
    #
    # # 如果没有提供stats_data，则自动计算
    # if stats_data is None:
    #     # 先尝试使用新的get_school_stats_data函数
    #     try:
    #         stats_data = get_school_stats_data(year, area, use_cache)
    #     except:
    #         # 如果失败，回退到使用get_area_full_stats函数
    #         stats_data = get_area_full_stats(year, area, use_cache)
        
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_school_stats_table(year, area, stats_data),
        build_area_team_count_bar( year , area , stats_data ),
        build_area_participant_count_bar(year, area, stats_data)
    )
    return page.render_embed()



def render_area_range_chart(
    start_year: int,
    end_year: int,
    area: str,
    stats_data=None,
    use_cache: bool = True
) -> Page:
    """
    生成【start_year–end_year 区间】【area 赛区】的五年队伍数多年度对比
    页面 HTML+JS（render_embed）。
    
    :param start_year: 开始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 预先计算的统计数据，如果为None则自动计算，
                     可以是get_multi_year_stats_data返回的完整统计数据，
                     也可以是原始的data_by_year格式数据
    :param use_cache: 是否使用缓存（当stats_data为None时有效）
    :return: Page对象
    """
    # from demo.services.statistics import get_multi_year_stats_data
    #
    # # 如果没有提供stats_data，则自动计算
    # if stats_data is None:
    #     stats_data = get_multi_year_stats_data(start_year, end_year, area, use_cache)
    
    # 3. 枚举年度柱状图
    bar = Bar(
        init_opts=opts.InitOpts(width='100%', height='600px')
    )
    
    # 兼容直接传入data_by_year的情况
    if 'years' not in stats_data and 'data_by_year' not in stats_data:
        # 直接传入的是data_by_year
        data_by_year = stats_data
        years = sorted(data_by_year.keys())
        
        # 提取学校并按参赛队伍数排序
        from demo.services.statistics import extract_schools_from_data
        schools, total_map = extract_schools_from_data(
            data_by_year, 
            years, 
            sort_key_field='team_count'
        )
    else:
        # 传入的是完整的统计数据
        years = stats_data['years']
        schools = stats_data['schools_by_team_count']
        data_by_year = stats_data['data_by_year']
        total_map = stats_data['total_team_count']
    
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