# demo/services/charts.py
from typing import Dict, Any, List, Union, Optional, Tuple
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts, LabelOpts, AxisOpts


# 通用工具函数
def calculate_percentage(part: int, whole: int) -> str:
    """计算百分比，并格式化为字符串"""
    return f"{round(part / whole * 100, 2)}%" if whole else "0%"


def extract_schools_from_data(
    data_by_year: Dict[int, Dict[str, Dict[str, Any]]],
    years: List[int],
    sort_key_field: str = 'team_count',
    reverse: bool = True
) -> Tuple[List[str], Dict[str, int]]:
    """
    从多年度数据中提取学校列表并按指定字段排序
    
    :param data_by_year: 多年度数据
    :param years: 年份列表
    :param sort_key_field: 排序字段
    :param reverse: 是否降序排列
    :return: 学校列表和总和映射
    """
    # 提取所有学校
    schools = list({
        s for stats in data_by_year.values() for s in stats
    })
    
    # 计算总和映射
    total_map = {
        s: sum(data_by_year[y].get(s, {}).get(sort_key_field, 0) for y in years)
        for s in schools
    }
    
    # 按总和排序
    schools.sort(key=lambda s: total_map[s], reverse=reverse)
    
    return schools, total_map


def create_generic_bar(
    x_data: List[str],
    y_data_list: List[List[Any]],
    y_names: List[str],
    title: str,
    init_opts: Optional[opts.InitOpts] = None,
    label_show: bool = True,
    rotate_labels: int = 45,
    datazoom: bool = True
) -> Bar:
    """
    创建通用柱状图
    
    :param x_data: X轴数据
    :param y_data_list: Y轴数据列表（可多个系列）
    :param y_names: Y轴系列名称列表
    :param title: 图表标题
    :param init_opts: 初始化选项
    :param label_show: 是否显示标签
    :param rotate_labels: X轴标签旋转角度
    :param datazoom: 是否启用数据缩放
    :return: 柱状图对象
    """
    bar = Bar(init_opts=init_opts) if init_opts else Bar()
    bar.add_xaxis(x_data)
    
    for i, y_data in enumerate(y_data_list):
        bar.add_yaxis(
            y_names[i],
            y_data,
            label_opts=opts.LabelOpts(is_show=label_show)
        )
    
    global_opts = {
        "title_opts": opts.TitleOpts(title=title),
        "xaxis_opts": opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=rotate_labels)),
    }
    
    if datazoom:
        global_opts["datazoom_opts"] = [opts.DataZoomOpts()]
    
    bar.set_global_opts(**global_opts)
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


def create_page_and_render(
    charts: List[Union[Bar, Table, Line]],
    render_embed: bool = True
) -> Union[str, Page]:
    """
    创建页面并渲染
    
    :param charts: 图表对象列表
    :param render_embed: 是否返回嵌入式HTML
    :return: 嵌入式HTML或Page对象
    """
    page = Page(layout=Page.SimplePageLayout)
    page.add(*charts)
    
    if render_embed:
        return page.render_embed()
    return page


def build_school_stats_table(
        year: int,
        area: str,
        stats_data: Dict
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
    :param year: 年份
    :param area: 赛区
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {team_count: int, ...}, ...}
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

    # 兼容直接传入原始统计数据的情况
    if 'schools' not in stats_data:
        # 原始统计数据
        schools = list(stats_data.keys())
        schools.sort(key=lambda s: stats_data[s]['team_count'], reverse=True)
        
        rows = []
        for school in schools:
            data = stats_data[school]
            tc = data.get('team_count', 0)
            ac = data.get('award_count', 0)
            fp = data.get('first_prize_count', 0)
            sp = data.get('second_prize_count', 0)
            qc = data.get('qualification_count', 0)
            ff = data.get('final_first_prize_count', 0)
            
            # 计算比率
            award_rate = round(ac / tc * 100, 2) if tc else 0.0
            first_prize_rate = round(fp / tc * 100, 2) if tc else 0.0
            second_prize_rate = round(sp / tc * 100, 2) if tc else 0.0
            qualification_rate = round(qc / tc * 100, 2) if tc else 0.0
            final_first_prize_rate = round(ff / tc * 100, 2) if tc else 0.0
            
            rows.append([
                school,
                area,
                tc,
                f"{award_rate}%",
                fp,
                f"{first_prize_rate}%",
                sp,
                f"{second_prize_rate}%",
                f"{qualification_rate}%",
                f"{final_first_prize_rate}%",
            ])
    else:
        # 完整统计数据
        schools = stats_data['schools']
        team_counts = stats_data['team_counts']
        award_rates = stats_data['award_rates']
        first_prize_counts = stats_data['first_prize_counts']
        first_prize_rates = stats_data['first_prize_rates']
        second_prize_counts = stats_data['second_prize_counts']
        second_prize_rates = stats_data['second_prize_rates']
        qualification_rates = stats_data['qualification_rates']
        final_first_prize_rates = stats_data['final_first_prize_rates']

        rows = []
        for i, school in enumerate(schools):
            rows.append([
                school,
                area,
                team_counts[i],
                f"{award_rates[i]}%",
                first_prize_counts[i],
                f"{first_prize_rates[i]}%",
                second_prize_counts[i],
                f"{second_prize_rates[i]}%",
                f"{qualification_rates[i]}%",
                f"{final_first_prize_rates[i]}%",
            ])

    return create_generic_table(
        headers, 
        rows, 
        title=f"{year}年{area}学校统计表"
    )


def build_area_detail_bar(year: int, area: str, stats_data: Dict) -> Bar:
    """
    构造柱状图，显示各学校的参赛队伍数。
    :param year: 年份
    :param area: 赛区名称
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {team_count: int, ...}, ...}
    :return: 柱状图
    """
    # 兼容直接传入原始统计数据的情况
    if 'schools' not in stats_data:
        # 原始统计数据
        schools = list(stats_data.keys())
        schools.sort(key=lambda s: stats_data[s]['team_count'], reverse=True)
        team_counts = [stats_data[s]['team_count'] for s in schools]
    else:
        # 完整统计数据
        schools = stats_data['schools']
        team_counts = stats_data['team_counts']

    return create_generic_bar(
        x_data=schools,
        y_data_list=[team_counts],
        y_names=[f"{year}年{area}参赛队伍数"],
        title=f"{year}年{area}各学校参赛队伍数"
    )

def build_area_participant_count_bar(year: int, area: str, stats_data: Dict) -> Bar:
    """
    构造柱状图，显示各学校的参赛人员数。
    :param year: 年份
    :param area: 赛区名称
    :param stats_data: 统计数据，可以是从statistics.py的get_school_stats_data获取的完整数据，
                     也可以是原始统计数据格式 {school: {participant_count: int, ...}, ...}
    :return: 柱状图
    """
    # 兼容直接传入原始统计数据的情况
    if 'schools' not in stats_data:
        # 原始统计数据
        schools = list(stats_data.keys())
        schools.sort(key=lambda s: stats_data[s]['team_count'], reverse=True)
        participant_counts = [stats_data[s].get('participant_count', 0) for s in schools]
    else:
        # 完整统计数据
        schools = stats_data['schools']
        participant_counts = stats_data['participant_counts']

    return create_generic_bar(
        x_data=schools,
        y_data_list=[participant_counts],
        y_names=[f"{year}年{area}参赛人员数"],
        title=f"{year}年{area}各学校参赛人员数"
    )


def render_area_detail_chart(year: int, area: str, stats_data=None, use_cache: bool = True) -> str:
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
    from demo.services.statistics import get_school_stats_data, get_area_full_stats
    
    # 如果没有提供stats_data，则自动计算
    if stats_data is None:
        # 先尝试使用新的get_school_stats_data函数
        try:
            stats_data = get_school_stats_data(year, area, use_cache)
        except:
            # 如果失败，回退到使用get_area_full_stats函数
            stats_data = get_area_full_stats(year, area, use_cache)
        
    bar = build_area_detail_bar(year, area, stats_data)
    participant_count_bar = build_area_participant_count_bar(year, area, stats_data)
    table = build_school_stats_table(year, area, stats_data)

    return create_page_and_render([table, bar, participant_count_bar])

##############################################################################################################
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


def render_first_prize_chart(
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
    from demo.services.statistics import get_multi_year_stats_data
    
    # 如果没有提供stats_data，则自动计算
    if stats_data is None:
        stats_data = get_multi_year_stats_data(start_year, end_year, area, use_cache)
        
    bar = build_range_year_report_first_prize_bar(start_year, end_year, area, stats_data)
    table = build_range_year_report_first_prize_table(start_year, end_year, area, stats_data)
    return create_page_and_render([bar, table])

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
        legend_opts=opts.LegendOpts(pos_top="10%")
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
    """
    from demo.services.statistics import get_multi_year_stats_data
    
    # 如果没有提供stats_data，则自动计算
    if stats_data is None:
        stats_data = get_multi_year_stats_data(start_year, end_year, area, use_cache)
    
    # 创建图表
    bar = build_range_year_area_report_participant_count_bar(
        start_year, end_year, area, stats_data
    )
    table = build_range_year_area_report_participant_count_table(
        start_year, end_year, area, stats_data
    )
    
    # 返回页面（不渲染为HTML）
    return create_page_and_render([bar, table], render_embed=False)