# demo/services/charts.py
from typing import Dict, Any, List, Union, Optional
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts, ToolboxOpts
from demo.models import SchoolYearlyCache

# # 通用工具函数
def _format_percentage(number , ndigits:int = 2) -> str:
    """
    格式化为字符串形式的带百分号的百分数
    :param number:要转换的数字
    :param ndigits:要保留的小数位数
    """
    if number:
        return f"{round ( number * 100 , ndigits )}%"
    else:
        return "0%"


# 排序函数
def _data_sort_and_extract(stats_data, sort_key, extract_key, header = 'school', ):
    """
    用于数据在画图之前的排序和从总数据提取需要的数据
    :param stats_data: 统计数据列表
    :param sort_key: 排序的键，倒序从大到小
    :param extract_key: 提取的字段
    :param header: 提取的x轴数据或者说表头
    :return:
    """
    stats_data.sort (
        key = lambda item: item[sort_key] ,
        reverse = True
    )
    headers = [item[header] for item in stats_data]
    rows = [item[extract_key] for item in stats_data]
    return headers, rows

def create_generic_bar(
    x_data: List[str],
    y_data_list: List[List[Any]],
    y_names: List[str],
    title: str,
    label_show: bool = True,
    rotate_labels: int = 45,
) -> Bar:
    """
    创建通用柱状图
    
    :param x_data: X轴数据
    :param y_data_list: Y轴数据列表（可多个系列）
    :param y_names: Y轴系列名称列表
    :param title: 图表标题
    :param label_show: 是否显示标签
    :param rotate_labels: X轴标签旋转角度
    :return: 柱状图对象
    """
    bar = Bar(
        init_opts= opts.InitOpts(
            width="100%",
            height="800px"
        ),
    )

    bar.add_xaxis(x_data)

    for i, y_data in enumerate(y_data_list):
        bar.add_yaxis(
            y_names[i],
            y_data,
            label_opts=opts.LabelOpts(is_show=label_show)
        )

    bar.set_global_opts(

        title_opts = opts.TitleOpts(title=title),
        xaxis_opts = opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=rotate_labels)),
        datazoom_opts = opts.DataZoomOpts(
            pos_bottom = "20",
        ),
        toolbox_opts= opts.ToolboxOpts(),
    )
    bar = (
        Grid(init_opts=opts.InitOpts(width="100%"))
        .add(
            bar,
            grid_opts=opts.GridOpts(
                pos_bottom="25%"
            )
        )
    )
    return bar


def create_generic_table(
    headers: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None
) -> Table:
    """
    创建通用表格
    
    :param headers: 表头
    :param rows: 行数据
    :param title: 表格标题
    :return: 表格对象
    """
    table = Table()
    table.add(headers, rows)
    
    if title:
        table.set_global_opts(
            title_opts=ComponentTitleOpts(title=title)
        )
    
    return table

#---------------------------------------------------------------------------------------

def build_area_detail_stats_table(
        year: int,
        area: str,
        stats_data: List
) -> Table:
    """
    生成xx年xx赛区各个学校统计表格，包含各校的参赛队伍数、获奖率等信息。
    构造一个 pyecharts Table
    :param year: 年份
    :param area: 赛区
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {team_count: int, ...}, ...}
    """
    # 选择要显示的字段
    headers =[
        'school',
        'team_count',
        'award_count',
        'first_prize_count',
        'first_prize_rate',
        'second_prize_count',
        'second_prize_rate',
        'third_prize_count',
        'third_prize_rate',
        'qualification_rate',
        'final_first_prize_rate'
    ]
    # 初始化汉语字段
    chinese_headers=[]
    # 查找model里面的注释，并替换
    for temp_header in headers:
        temp_header = SchoolYearlyCache._meta.get_field(temp_header).db_comment
        chinese_headers.append(temp_header)
    # 原始统计数据
    # 数据排序
    stats_data.sort(
        key=lambda temp_item: temp_item['team_count'],
        reverse=True
    )
    rows = []
    # 提取出数据并进行百分数的替换
    for item in stats_data:
        one_row = []
        for temp_header in headers:
            if 'rate' in temp_header:
                one_row.append(_format_percentage(item[temp_header]))
            else:
                one_row.append(item[temp_header])
        rows.append(one_row)

    return create_generic_table(
        chinese_headers,
        rows, 
        title=f"{year}年{area}学校统计表"
    )


def build_area_detail_team_count_bar(year: int , area: str , stats_data: List) -> Bar:
    """
    构造柱状图，显示各学校的参赛队伍数。
    :param year: 年份
    :param area: 赛区名称
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {team_count: int, ...}, ...}
    :return: 柱状图
    """
    schools, team_counts = _data_sort_and_extract (
        stats_data = stats_data ,
        sort_key = 'team_count' ,
        extract_key = 'team_count' ,
        header = 'school'
    )
    return create_generic_bar(
        x_data=schools,
        y_data_list=[team_counts],
        y_names=[f"{year}年{area}参赛队伍数"],
        title=f"{year}年{area}各学校参赛队伍数"
    )

def build_area_detail_participant_count_bar(year: int , area: str , stats_data: List) -> Bar:
    """
    构造柱状图，显示各学校的参赛人员数。
    :param year: 年份
    :param area: 赛区名称
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {participant_count: int, ...}, ...}
    :return: 柱状图
    """
    schools, participant_counts = _data_sort_and_extract(
        stats_data= stats_data,
        sort_key = 'participant_count',
        extract_key = 'participant_count',
        header = 'school'
    )
    return create_generic_bar(
        x_data=schools,
        y_data_list=[participant_counts],
        y_names=[f"{year}年{area}参赛人员数"],
        title=f"{year}年{area}各学校参赛人员数"
    )

#-------------------------------------------------------------------------------------------------
def build_range_year_report_first_prize_bar(
    start_year: int,
    end_year: int,
    area: str,
    stats_data: Dict
) -> Bar:
    """
    构造柱状图 + 两条折线：
      - 各年"分赛区一等奖获奖队数量"柱状
      - "五年总和"折线（Y 轴 0 左侧）
      - "平均获奖率"折线（Y 轴 1 右侧）
      
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 统计数据，从statistics.py的get_multi_year_stats_data获取，
                     或者直接是data_by_year格式的数据
    :return: 柱状图对象
    """
    # 兼容直接传入data_by_year的情况
    # if 'years' not in stats_data and 'data_by_year' not in stats_data:
    # 直接传入的是data_by_year
    data_by_year = stats_data
    years = list(range(start_year, end_year + 1))

    # 提取学校并按一等奖获奖数量排序
    from demo.services.statistics import extract_schools_from_data
    schools, total_first_prize = extract_schools_from_data(
        data_by_year,
        years,
        sort_key_field='first_prize_count'
    )

    # 计算总参赛队伍数
    total_team_count = {
        s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)
        for s in schools
    }

    # 计算平均获奖率
    avg_first_prize_rate = {
        s: round(total_first_prize[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in schools
    }
    # else:
    #     # 传入的是完整的统计数据
    #     years = stats_data['years']
    #     schools = stats_data['schools_by_first_prize']
    #     data_by_year = stats_data['data_by_year']
    #     total_first_prize = stats_data['total_first_prize']
    #     avg_first_prize_rate = stats_data['avg_first_prize_rate']

    # 3. 柱状图（每年 first_prize_count）
    bar = Bar()
    bar.add_xaxis(schools)
    for y in years:
        bar.add_yaxis(
            f"{y}年分赛区一等奖获奖队数量",
            [ data_by_year[y].get(s, {}).get('first_prize_count', 0) for s in schools ],
            label_opts=LabelOpts(is_show=True)
        )

    # 4. 左侧"汇总"折线
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
            [ total_first_prize[s] for s in schools ],
            yaxis_index=1,
            label_opts=LabelOpts(is_show=True)
        )
    )
    bar.overlap(line_sum)

    # 5. 右侧"平均获奖率"折线
    line_rate = (
        Line()
        .add_xaxis(schools)
        .add_yaxis(
            "一等奖平均获奖率",
            [ avg_first_prize_rate[s] for s in schools ],
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
    stats_data: Dict
) -> Table:
    """
    构造底部表格，列：
      学校名称 |
      {y}年获奖队数量… |
      五年总和 |
      平均获奖率
      
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 统计数据，从statistics.py的get_multi_year_stats_data获取，
                     或者直接是data_by_year格式的数据
    :return: 表格对象
    """
    # 兼容直接传入data_by_year的情况
    if 'years' not in stats_data and 'data_by_year' not in stats_data:
        # 直接传入的是data_by_year
        data_by_year = stats_data
        years = list(range(start_year, end_year + 1))
        
        # 提取学校并按一等奖获奖数量排序
        from demo.services.statistics import extract_schools_from_data
        schools, total_first_prize = extract_schools_from_data(
            data_by_year, 
            years, 
            sort_key_field='first_prize_count'
        )
        
        # 计算总参赛队伍数
        total_team_count = {
            s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)
            for s in schools
        }
        
        # 计算平均获奖率
        avg_first_prize_rate = {
            s: round(total_first_prize[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
            for s in schools
        }
    else:
        # 传入的是完整的统计数据
        years = stats_data['years']
        schools = stats_data['schools_by_first_prize']
        data_by_year = stats_data['data_by_year']
        total_first_prize = stats_data['total_first_prize']
        avg_first_prize_rate = stats_data['avg_first_prize_rate']

    # 2. 表头
    headers = ["学校名称"] + [f"{y}年获奖队数量" for y in years] + ["五年总和", "平均获奖率"]

    # 3. 行数据
    rows = []
    for s in schools:
        row = [s]
        for y in years:
            row.append(data_by_year[y].get(s, {}).get('first_prize_count', 0))
        row.append(total_first_prize[s])
        row.append(f"{avg_first_prize_rate[s]}%")
        rows.append(row)

    return create_generic_table(
        headers, 
        rows, 
        title=f"{area} 赛区各高校近五年分赛区一等奖获奖统计（表格）"
    )


# 显示指定年份范围、赛区的各年参赛队伍数统计柱状图
def build_range_year_area_report_participant_count_bar(
    start_year: int,
    end_year: int,
    area: str,
    stats_data: Dict
) -> Bar:
    """
    构造柱状图，显示各年参赛队伍数量
    
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 统计数据，从statistics.py的get_multi_year_stats_data获取，
                     或者直接是data_by_year格式的数据
    :return: 柱状图对象
    """
    # 兼容直接传入data_by_year的情况
    if 'years' not in stats_data and 'data_by_year' not in stats_data:
        # 直接传入的是data_by_year
        data_by_year = stats_data
        years = sorted(data_by_year.keys())
        
        # 提取学校并按参赛队伍数排序
        from demo.services.statistics import extract_schools_from_data
        schools, total_team_count = extract_schools_from_data(
            data_by_year, 
            years, 
            sort_key_field='team_count'
        )
    else:
        # 传入的是完整的统计数据
        years = stats_data['years']
        schools = stats_data['schools_by_team_count']
        data_by_year = stats_data['data_by_year']
        total_team_count = stats_data['total_team_count']

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
            [total_team_count[s] for s in schools],
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
        legend_opts=opts.LegendOpts(pos_top="10%"),
        toolbox_opts=opts.ToolboxOpts(),
        datazoom_opts=opts.DataZoomOpts()

    )

    return bar

# 显示指定年份范围、赛区的各年参赛队伍数统计表
def build_range_year_area_report_participant_count_table(
    start_year: int,
    end_year: int,
    area: str,
    stats_data: Dict
) -> Table:
    """
    构造表格，显示各年参赛队伍数量
    
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param stats_data: 统计数据，从statistics.py的get_multi_year_stats_data获取，
                     或者直接是data_by_year格式的数据
    :return: 表格对象
    """
    # 兼容直接传入data_by_year的情况
    if 'years' not in stats_data and 'data_by_year' not in stats_data:
        # 直接传入的是data_by_year
        data_by_year = stats_data
        years = sorted(data_by_year.keys())
        
        # 提取学校并按参赛队伍数排序
        from demo.services.statistics import extract_schools_from_data
        schools, total_team_count = extract_schools_from_data(
            data_by_year, 
            years, 
            sort_key_field='team_count'
        )
    else:
        # 传入的是完整的统计数据
        years = stats_data['years']
        schools = stats_data['schools_by_team_count']
        data_by_year = stats_data['data_by_year']
        total_team_count = stats_data['total_team_count']

    # 6. 构造底部表格
    headers = ["学校名称"] + [f"{y}年队伍数" for y in years] + ["五年总和"]
    rows = []
    for s in schools:
        row = [s] + [
            data_by_year[y].get(s, {}).get('team_count', 0)
            for y in years
        ] + [total_team_count[s]]
        rows.append(row)

    table = (
        Table()
        .add(headers, rows)
        .set_global_opts(
            title_opts=ComponentTitleOpts(title=f"{area} 赛区五年报名详情")
        )
    )
    return table

# def render_area_range_chart(
#     start_year: int,
#     end_year: int,
#     area: str,
#     stats_data=None,
#     use_cache: bool = True
# ) -> Page:
#     """
#     生成【start_year–end_year 区间】【area 赛区】的五年队伍数多年度对比
#     页面 HTML+JS（render_embed）。
#     :param start_year: 开始年份
#     :param end_year: 结束年份
#     :param area: 赛区名称
#     :param stats_data: 预先计算的统计数据，如果为None则自动计算，
#                      可以是get_multi_year_stats_data返回的完整统计数据，
#                      也可以是原始的data_by_year格式数据
#     :param use_cache: 是否使用缓存（当stats_data为None时有效）
#     """
#     # 创建图表
#     bar = build_range_year_area_report_participant_count_bar(
#         start_year, end_year, area, stats_data
#     )
#     table = build_range_year_area_report_participant_count_table(
#         start_year, end_year, area, stats_data
#     )
#
#     # 返回页面（不渲染为HTML）
#     return create_page_and_render([bar, table], render_embed=False)