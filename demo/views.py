from django.shortcuts import render
from django.http import HttpResponse
from demo.services.statistics import (
    get_area_stats,
    get_northwest_schools_stats,
    get_school_yearly_stats, get_school_yearly_stats_range
)
from demo.services.charts import render_area_detail_chart, render_area_range_chart
from pyecharts import options as opts
from pyecharts.charts import Bar, Page

AREAS = [
      '东北赛区','上海赛区','西南赛区','华东赛区',
      '西北赛区','华中赛区','华北赛区','华南赛区',
      '海外及港澳台赛区'
    ]

def navigation_view(request):
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    return render(request, 'demo/navigation.html', {
        'years': years,
        'areas': AREAS,
    })

def area_detail_view(request, year: int, area: str):
    """
    显示指定年份、地区的统计数据
    year: 年份
    area: 地区
    """
    if area not in AREAS:
        return HttpResponse(f"<h1>{year}年{area}不存在</h1>")

    # stats = get_area_detail_stats(year, area)
    stats = get_school_yearly_stats(year, area)
    if not stats:
        return HttpResponse(f"<h1>{year}年{area}暂无数据</h1>")

    # 只需一行调用，就能得到完整的 chart HTML
    chart_html = render_area_detail_chart(year, area, stats)
    return render(request, 'demo/area_detail.html', {
        'year': year,
        'area': area,
        'stats': stats,
        'chart_html': chart_html,
    })

def yearly_report(request, year: int):
    area_stats = get_area_stats(year)
    if not area_stats:
        return HttpResponse(f"<h1>{year}年赛区统计数据未找到</h1>")

    # 构造 pyecharts 图表
    areas = list(area_stats.keys())
    member_counts = [sum(sub['member_count'] for sub in area_stats[a].values()) for a in areas]
    team_counts   = [sum(sub['team_count']   for sub in area_stats[a].values()) for a in areas]

    bar1 = (
        Bar()
        .add_xaxis(areas)
        .add_yaxis("参赛人数", member_counts)
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{year}年各赛区参赛人数"))
    )
    bar2 = (
        Bar()
        .add_xaxis(areas)
        .add_yaxis("队伍数量", team_counts)
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{year}年各赛区队伍数量"))
    )
    bar3 = (
        Bar()
        .add_xaxis(list(get_northwest_schools_stats(year).keys()))
        .add_yaxis(f"{year}年西北赛区队伍数", list(get_northwest_schools_stats(year).values()))
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{year}年西北赛区各学校队伍数"))
    )

    page = Page(layout=Page.SimplePageLayout)
    page.add(bar1, bar2, bar3)
    return HttpResponse(page.render_embed())
    
def school_detail_view(request, year: int, school: str):
    return HttpResponse(f"<h1>{year}年{school}统计数据未找到</h1>")


def five_year_report(request):
    range_year_stats = get_school_yearly_stats_range(2019, 2024, '西北赛区');
    page = render_area_range_chart(2019, 2024, '西北赛区', range_year_stats);
    return HttpResponse(page.render_embed())