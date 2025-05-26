# @file_name: demo/models.py


from django.shortcuts import render
from django.http import HttpResponse
from demo.services.statistics import (
    get_school_yearly_stats, get_school_yearly_stats_range
)
from demo.services.charts import render_area_detail_chart, render_area_range_chart

AREAS = [
      '东北赛区','上海赛区','西南赛区','华东赛区',
      '西北赛区','华中赛区','华北赛区','华南赛区',
      '海外及港澳台赛区'
    ]

def navigation_view(request):
    """
    显示导航页，包含年份和赛区选择
    :param request:
    :return:
    """
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    return render(request, 'demo/navigation.html', {
        'years': years,
        'areas': AREAS,
    })

def range_year_report_all_area_view(request):
    """
    显示2019-2023年各赛区的统计数据
    :param request:
    :return:
    """
    return HttpResponse(f"<h1>功能暂未开发</h1>")



def range_year_area_report_view(request, start_year: int, end_year: int, area: str):
    """
    显示指定年份范围、地区的统计数据
    :param request:
    :param start_year:
    :param end_year:
    :param area:
    :return:
    """
    # 获取了一个总的统计数据
    range_year_stats = get_school_yearly_stats_range(start_year, end_year, area)
    # 都是放在同一个页面里面的
    page = render_area_range_chart(start_year, end_year, area, range_year_stats)
    return HttpResponse(page.render_embed())


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

def yearly_report_view(request, year: int):
    """
    显示指定xx年份的所有赛区的分析
    :param request:
    :param year:
    :return:
    """
    return HttpResponse(f"<h1>{year}年xx赛区分析暂未开发</h1>")
    
def school_detail_view(request, year: int, school: str):
    return HttpResponse(f"<h1>{year}年{school}统计数据未找到</h1>")


