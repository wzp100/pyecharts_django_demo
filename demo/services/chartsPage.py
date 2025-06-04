# demo/services/charts.py
# from typing import Dict, Any, List
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts

from demo.services.charts import build_area_detail_team_count_bar , build_area_detail_participant_count_bar , \
    build_area_detail_stats_table , \
    build_range_year_report_first_prize_bar , build_range_year_report_first_prize_table , \
    build_range_year_area_report_participant_count_bar , build_range_year_area_report_participant_count_table


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
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_range_year_area_report_participant_count_table(start_year , end_year , area , stats_data),
        build_range_year_area_report_participant_count_bar (start_year , end_year , area , stats_data),
        # build_range_year_report_first_prize_bar(start_year, end_year, area, stats_data),
        # build_range_year_report_first_prize_table(start_year, end_year, area, stats_data)
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
        
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        build_area_detail_stats_table( year , area , stats_data ),
        build_area_detail_team_count_bar( year , area , stats_data ),
        build_area_detail_participant_count_bar( year , area , stats_data )
    )
    return page.render_embed()
