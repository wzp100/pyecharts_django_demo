from django.shortcuts import render
from django.http import HttpResponse
from django.db import models
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar, Page
from .models import Team, TeamMember
import datetime
import json
import os
import time

# 配置模板环境
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./demo/templates"))


# 定义JSON数据文件路径
def get_data_file_path(filename):
    """获取数据文件的完整路径"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, filename)


def save_data_to_json(data, filename):
    """将数据保存到JSON文件"""
    file_path = get_data_file_path(filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return file_path


def load_data_from_json(filename, max_age_hours=24):
    """从JSON文件加载数据，如果文件不存在或过期则返回None"""
    file_path = get_data_file_path(filename)
    if not os.path.exists(file_path):
        return None
    
    # 检查文件是否过期
    file_age = time.time() - os.path.getmtime(file_path)
    if file_age > max_age_hours * 3600:  # 转换为秒
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_area_stats(year):
    """获取指定年份各赛区统计数据，全部通过AreaStats表ORM查询实现"""
    from .models import AreaStats
    # 查询该年份的所有赛区的队伍数和参赛人数
    area_stats_queryset = AreaStats.objects.using('yyds_mysql').filter(year=year)
    areas = list(area_stats_queryset.values_list('area', flat=True).order_by('area'))
    member_counts = {row.area: row.member_count for row in area_stats_queryset}
    team_counts = {row.area: row.team_count for row in area_stats_queryset}
    result = {
        'areas': areas,
        'member_counts': member_counts,
        'team_counts': team_counts,
    }
    return result


def get_northwest_schools_stats(year):
    """获取西北赛区各学校的统计数据，直接通过NorthwestSchoolStats表ORM查询实现"""
    from .models import NorthwestSchoolStats
    queryset = NorthwestSchoolStats.objects.using('yyds_mysql').filter(year=year).order_by('-team_count')
    return {row.school: row.team_count for row in queryset}


def navigation_view(request):
    """显示导航页面，链接到各年份的报告，仅依赖AreaStats表，不再使用Team表的聚合统计"""
    from .models import AreaStats
    years = range(2019, 2024)
    years_stats = {}
    for year in years:
        area_stats = AreaStats.objects.using('yyds_mysql').filter(year=year).order_by('area')
        stats = {
            'areas': [],
            'team_counts': {},
            'member_counts': {}
        }
        for row in area_stats:
            stats['areas'].append(row.area)
            stats['team_counts'][row.area] = row.team_count
            stats['member_counts'][row.area] = row.member_count
        stats['areas'].sort()
        years_stats[year] = stats
    context = {
        'years': years,
        'years_stats': years_stats
    }
    return render(request, 'demo/navigation.html', context)

def area_detail_view(request, year, area):
    """显示指定年份和赛区的学校详情"""
    if area == '西北赛区':
        schools_stats = get_northwest_schools_stats(year)
    else:
        # 对于其他赛区，暂时返回简单信息
        schools_stats = {f"{area}学校": 0}
    
    context = {
        'year': year,
        'area': area,
        'schools_stats': schools_stats
    }
    return render(request, 'demo/area_detail.html', context)


def yearly_report(request, year):
    """生成并显示指定年份的统计图表"""
    # 1. 获取赛区统计数据
    area_stats = get_area_stats(year)
    if not area_stats or not area_stats.get('areas'):
        return HttpResponse(f"<h1>{year}年赛区统计数据未找到</h1>")
        
    areas_sorted = area_stats['areas']
    member_counts = [area_stats['member_counts'].get(area, 0) for area in areas_sorted]
    team_counts_list = [area_stats['team_counts'].get(area, 0) for area in areas_sorted]

    # 2. 创建参赛人数柱状图
    bar_members = (
        Bar()
        .add_xaxis(list(areas_sorted))
        .add_yaxis("参赛人数", member_counts)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年各赛区参赛人数统计"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    )
    
    # 3. 创建队伍数量柱状图
    bar_teams = (
        Bar()
        .add_xaxis(list(areas_sorted))
        .add_yaxis("队伍数量", team_counts_list)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年各赛区队伍数量统计"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    )
    
    # 4. 统计西北赛区各学校的参赛队伍数量
    northwest_schools_data = get_northwest_schools_stats(year)
    
    # 5. 创建西北赛区学校参赛队伍数量柱状图
    bar_northwest = (
        Bar()
        .add_xaxis(list(northwest_schools_data.keys()))
        .add_yaxis(f"{year}年参赛队伍数", list(northwest_schools_data.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{year}年西北赛区各学校参赛队伍数量"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    )
    
    # 6. 创建页面对象，将图表添加到同一个页面
    page = Page(layout=Page.SimplePageLayout)
    page.add(bar_members, bar_teams, bar_northwest)
    
    # 7. 渲染页面并返回
    return HttpResponse(page.render_embed())


def get_northwest_schools_stats(year):
    """获取西北赛区各学校的统计数据，优先从JSON文件读取"""
    # 尝试从JSON文件加载数据
    filename = f'northwest_schools_{year}.json'
    data = load_data_from_json(filename)
    if data:
        return data
    
    # 如果没有缓存数据，则从数据库查询
    try:
        northwest_teams = Team.objects.using('yyds_mysql').filter(
            competition_zone='西北赛区',
            create_year=year  # 使用 create_year 字段进行年份筛选
        )
        
        # 统计每个学校的队伍数量
        school_team_counts = {}
        for team in northwest_teams:
            try:
                # 查找该团队的队长
                try:
                    captain = TeamMember.objects.using('yyds_mysql').get(
                        team_code=team.team_code,
                        member_type='队长',
                        create_year=year # 确保年份一致
                    )
                except TeamMember.DoesNotExist:
                    # 如果在member_type中找不到队长，尝试在member_type_detail中查找
                    captain = TeamMember.objects.using('yyds_mysql').filter(
                        team_code=team.team_code,
                        create_year=year
                    ).filter(
                        models.Q(member_type='队长') | models.Q(member_type_detail__contains='队长')
                    ).first()
                school_name = captain.school
                if school_name:
                    if school_name in school_team_counts:
                        school_team_counts[school_name] += 1
                    else:
                        school_team_counts[school_name] = 1
            except TeamMember.DoesNotExist:
                # 如果找不到队长信息，可以跳过或者记录日志
                print(f"警告：团队 {team.team_code} 在 {year} 年找不到队长信息。")
                pass
            except TeamMember.MultipleObjectsReturned:
                # 如果一个团队有多于一个队长，记录错误或选择第一个
                print(f"错误：团队 {team.team_code} 在 {year} 年有多于一个队长记录。")
                # 可以选择获取第一个队长信息
                captain = TeamMember.objects.using('yyds_mysql').filter(
                    team_code=team.team_code,
                    member_type='队长',
                    create_year=year
                ).first()
                if captain and captain.school:
                    school_name = captain.school
                    if school_name in school_team_counts:
                        school_team_counts[school_name] += 1
                    else:
                        school_team_counts[school_name] = 1
                else:
                     print(f"警告：团队 {team.team_code} 在 {year} 年的多个队长记录中也无法确定学校。")
        
        # 按队伍数量降序排序
        sorted_schools = dict(sorted(school_team_counts.items(), key=lambda x: x[1], reverse=True))
        
        # 保存到JSON文件
        save_data_to_json(sorted_schools, filename)
        
        return sorted_schools
    except Exception as e:
        print(f"获取西北赛区数据出错: {e}")
        # 如果出错，返回空字典
        return {}


def get_school_yearly_stats(year):
    """获取所有学校的年度统计数据，优先从JSON文件读取"""
    # 尝试从JSON文件加载数据
    filename = f'school_yearly_stats_{year}.json'
    data = load_data_from_json(filename)
    if data:
        # Data is already in the correct dictionary format
        return data
    
    # 如果没有缓存数据，则从数据库查询
    try:
        teams = Team.objects.using('yyds_mysql').filter(
            create_year=year  # 使用 create_year 字段进行年份筛选
        )
        
        # 按学校分组统计
        schools_stats = {}
        
        for team in teams:
            school_name = None
            try:
                # 查找该团队的队长
                try:
                    captain = TeamMember.objects.using('yyds_mysql').get(
                        team_code=team.team_code,
                        member_type='队长',
                        create_year=year # 确保年份一致
                    )
                except TeamMember.DoesNotExist:
                    # 如果在member_type中找不到队长，尝试在member_type_detail中查找
                    captain = TeamMember.objects.using('yyds_mysql').filter(
                        team_code=team.team_code,
                        create_year=year
                    ).filter(
                        models.Q(member_type='队长') | models.Q(member_type_detail__contains='队长')
                    ).first()
                school_name = captain.school
                competition_zone = team.competition_zone # 赛区信息从Team获取
            except TeamMember.DoesNotExist:
                print(f"警告：团队 {team.team_code} 在 {year} 年找不到队长信息，无法确定学校。")
                continue # 跳过没有队长信息的团队
            except TeamMember.MultipleObjectsReturned:
                print(f"错误：团队 {team.team_code} 在 {year} 年有多于一个队长记录。将尝试使用第一个队长信息。")
                captain = TeamMember.objects.using('yyds_mysql').filter(
                    team_code=team.team_code,
                    member_type='队长',
                    create_year=year
                ).first()
                if captain and captain.school:
                    school_name = captain.school
                    competition_zone = team.competition_zone
                else:
                    print(f"警告：团队 {team.team_code} 在 {year} 年的多个队长记录中也无法确定学校。")
                    continue # 跳过无法确定学校的团队

            if not school_name:
                print(f"警告：团队 {team.team_code} 在 {year} 年队长学校信息为空，跳过统计。")
                continue # 跳过学校名称为空的团队

            # 如果学校不在字典中，创建新的统计字典
            if school_name not in schools_stats:
                schools_stats[school_name] = {
                    'school_name': school_name,
                    'year': year,
                    'competition_zone': competition_zone, # 使用获取到的赛区信息
                    'team_count': 0,
                    'award_count': 0,
                    'first_prize_count': 0,
                    'second_prize_count': 0,
                    'final_qualification_count': 0,
                    'final_first_prize_count': 0
                }
            
            # 更新队伍数量
            schools_stats[school_name]['team_count'] += 1
            
            # 更新获奖信息（这里需要根据实际数据模型调整）
            if hasattr(team, 'is_awarded') and team.is_awarded:
                schools_stats[school_name]['award_count'] += 1
            
            if hasattr(team, 'award_level'):
                if team.award_level == '分赛区一等奖':
                    schools_stats[school_name]['first_prize_count'] += 1
                elif team.award_level == '分赛区二等奖':
                    schools_stats[school_name]['second_prize_count'] += 1
            
            if hasattr(team, 'is_qualified_for_final') and team.is_qualified_for_final:
                schools_stats[school_name]['final_qualification_count'] += 1
            
            if hasattr(team, 'final_award_level') and team.final_award_level == '决赛一等奖':
                schools_stats[school_name]['final_first_prize_count'] += 1
        
        # 保存到JSON文件 (schools_stats is already serializable)
        save_data_to_json(schools_stats, filename)
        
        return schools_stats
    except Exception as e:
        print(f"获取学校年度统计数据出错: {e}")
        # 如果出错，返回空字典
        return {}


def update_all_json_data(request):
    """手动更新所有年份（2019-2023）的JSON数据文件"""
    updated_files = []
    errors = []
    for year in range(2019, 2024):
        try:
            print(f"正在更新 {year} 年的数据...")
            # 更新赛区统计数据
            get_area_stats(year)
            updated_files.append(f'area_stats_{year}.json')
            
            # 更新西北赛区学校统计数据
            get_northwest_schools_stats(year)
            updated_files.append(f'northwest_schools_{year}.json')
            
            # 更新学校年度统计数据
            get_school_yearly_stats(year)
            updated_files.append(f'school_yearly_stats_{year}.json')
            print(f"{year} 年数据更新完成.")
        except Exception as e:
            error_msg = f"更新 {year} 年数据时出错: {e}"
            print(error_msg)
            errors.append(error_msg)

    if errors:
        response_message = "部分年份数据更新失败:\n" + "\n".join(errors)
        response_message += "\n\n成功更新的文件:\n" + "\n".join(updated_files)
        return HttpResponse(response_message, status=500)
    else:
        return HttpResponse(f"所有年份 (2019-2023) 的JSON数据文件已成功更新！\n成功更新的文件:\n" + "\n".join(updated_files))
