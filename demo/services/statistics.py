from django.db import models
from django.utils import timezone
from demo.models import (
    Team, TeamMember, TeamAchievement,
    SchoolYearlyCache
)
from django.db.models import Count
from django.db import transaction
from typing import Dict, Any, List, Tuple

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


# 动态获取SchoolYearlyCache模型中的统计字段
def get_stat_fields():
    """获取SchoolYearlyCache模型中的统计字段列表，排除非统计相关字段"""
    # 排除这些字段，它们不是统计数据字段
    exclude_fields = {'id', 'year', 'area', 'school', 'updated_at'}
    
    # 获取模型的所有字段名
    all_fields = [field.name for field in SchoolYearlyCache._meta.get_fields()]
    
    # 过滤出统计字段
    stat_fields = [field for field in all_fields if field not in exclude_fields]
    return stat_fields

# 获取统计字段列表
STAT_FIELDS = get_stat_fields()


# TODO: 要补全的函数
def get_area_stats( ) -> dict:
    # """从 AreaStats 表查询某年各赛区 & 子项目的队伍和人数统计。"""
    # qs = AreaStats.objects.filter(year=year)
    # result = {}
    # for row in qs:
    #     area = row.area
    #     sub = row.subproject or "无子项目"
    #     result.setdefault(area, {})[sub] = {
    #         'team_count': row.team_count,
    #         'member_count': row.member_count,
    #     }
    # return result
    pass




def get_area_detail_stats(year: int, area: str) -> dict:
    """
    获取指定年份、指定赛区下各学校的参赛队伍数量统计，
    学校以队长的 school 字段为准。返回 {school_name: team_count, …}。
    异常情况（无队长、重复队长）会记录到日志并跳过或取第一条。
    """
    # 1. 计算指定赛区每个学校的参赛队伍，学校以队长的学校为准
    stats = {}
    # 2. 从数据库查询指定年份、指定赛区的队伍
    qs = Team.objects.filter(
        competition_zone=area,
        create_year=str(year)
    )
    for team in qs:
        # 1) 尝试按 member_type 找队长
        captain_qs = TeamMember.objects.filter(
            team_code=team.team_code,
            create_year=str(year),
            member_type='队长'
        )
        if not captain_qs.exists():
            # 2) 回退到 member_type_detail 包含 "队长"
            captain_qs = TeamMember.objects.filter(
                team_code=team.team_code,
                create_year=str(year),
            ).filter(
                models.Q(member_type_detail__contains='队长')
            )

        try:
            captain = captain_qs.get()
        except TeamMember.DoesNotExist:
            # 真正没找到队长，跳过
            print(f"队伍 {team.team_code} 无队长，跳过")
            continue
        except TeamMember.MultipleObjectsReturned:
            # 多条时取第一条
            captain = captain_qs.first()

        school = captain.school
        if not school:
            # 如果 school 为空，也跳过
            continue

        stats[school] = stats.get(school, 0) + 1

    # —— 按数量降序排序 —— 
    sorted_stats = dict(
        sorted(stats.items(), key=lambda kv: kv[1], reverse=True)
    )
    return sorted_stats

def get_area_full_stats(year: int, area: str, use_cache: bool = True) -> dict:
    """
    返回一个 school_stats：
    {
      school: {
        team_count: …,
        award_count: …,
        first_prize_count: …,
        second_prize_count: …,
        qualification_count: …,
        final_first_prize_count: …,
      }, …
    }
    其中仅保留属于指定 area 的学校。
    :param year: 年份
    :param area: 赛区名称
    :param use_cache: 是否使用缓存，默认为True
    """
    # 1) 从 area_detail_stats 拿到本区每校的 team_count
    area_team_counts = get_area_detail_stats(year, area)

    # 2) 拿到所有学校年度统计，传递use_cache参数
    all_stats = get_school_yearly_stats(year, area, use_cache=use_cache)

    # 3) 只保留本区学校，并把 team_count 覆盖到 school_stats 里
    school_stats = {}
    for school, stats in all_stats.items():
        if school in area_team_counts:
            stats['team_count'] = area_team_counts[school]
            school_stats[school] = stats

    return school_stats

# ---------- 1. 缓存读取 ---------- #
def _fetch_cached_stats(year: int, area: str) -> dict | None:
    """
    如缓存命中则返回 dict；未命中返回 None
    """
    qs = SchoolYearlyCache.objects.filter(year=str(year), area=area)
    if not qs.exists():
        return None

    return {
        c.school: {field: getattr(c, field) for field in STAT_FIELDS}
        for c in qs
    }


# ---------- 2. 统计计算 ---------- #
def _query_raw_data(year: int, area: str):
    """
    一次性把原始 QuerySet 拿出来，避免函数间重复 IO
    :param year: 年份
    :param area: 赛区名称
    :return: (teams, participants_map)
        teams: Team QuerySet，包含指定赛区和年份的所有队伍
        participants_map: {school_name: participant_count, …} 计算每个学校的参赛人数
    """
    # 从团队表中查询指定赛区和年份的所有队伍
    teams = Team.objects.filter(competition_zone=area, create_year=str(year))
    # 然后查询所有队伍的 team_code
    codes = list(teams.values_list('team_code', flat=True))


    # 对每个分组（学校）做聚合计数：COUNT(member_code)，并把结果放在字段别名 count 里
    members_qs = (
        TeamMember.objects
        .filter(create_year=str(year), team_code__in=codes)
        .values('school')
        .annotate(count=Count('member_code'))
    )
    participants_map = {r['school']: r['count'] for r in members_qs}

    return teams, participants_map


def _pick_captain(team: Team, year: int):
    """选出队长；有两种标记方式时回退兜底"""
    base_qs = TeamMember.objects.filter(
        team_code=team.team_code,
        create_year=str(year),
    )
    cap_qs = base_qs.filter(member_type='队长')
    if not cap_qs.exists():
        cap_qs = base_qs.filter(member_type_detail__contains='队长')

    try:
        return cap_qs.get()
    except Exception:
        return cap_qs.first()


def _update_school_record(rec: dict, ach: TeamAchievement | None):
    """
    根据成绩更新学校汇总记录
    """
    if not ach:
        return

    # 预赛奖项
    if ach.preliminary_award:
        rec['award_count'] += 1
        pre = ach.preliminary_award
        if ('一等奖' in pre) or ('晋级' in pre):
            rec['first_prize_count'] += 1
        elif '二等奖' in pre:
            rec['second_prize_count'] += 1
        if '晋级' in pre:
            rec['qualification_count'] += 1
    else:
        # 没有预赛奖项，算没有获奖的队伍
        rec['no_award_team_count'] += 1

    # 总决赛一等奖
    final_one = (
        (ach.final_technology and '一等奖' in ach.final_technology) or
        (ach.final_business and '一等奖' in ach.final_business)
    )
    if final_one:
        rec['final_first_prize_count'] += 1





def _compute_stats(year: int, area: str) -> dict:
    """
    真正的统计入口，只关心计算逻辑
    """
    teams, participants_map = _query_raw_data(year, area)
    stats: dict[str, dict] = {}

    for team in teams:
        # 1) 找队长获得学校
        captain = _pick_captain(team, year)
        if not captain or not captain.school:
            continue
        sch = captain.school

        # 2) 初始化学校记录
        # 如果学校不存在，则初始化一个新记录
        if sch not in stats:
            # 使用STAT_FIELDS创建初始化字典
            stats[sch] = {field: 0 for field in STAT_FIELDS}
            # 根据之前的查询结果，获取该学校的参赛人数
            stats[sch]['participant_count'] = participants_map.get(sch, 0)

        # 统计队伍数量，如果学校已存在，则增加队伍数量
        stats[sch]['team_count'] += 1

        # 3) 更新成绩相关字段
        # 选择指定年份和学校的 TeamAchievement
        ach = TeamAchievement.objects.filter(
            team_code=team, year=str(year)
        ).first()
        _update_school_record(stats[sch], ach)

    # 计算一下每个学校的未获奖率
    # 遍历学校，获取未获奖数以及参赛队伍数
    for sch, data in stats.items():
        no_award_count = data['no_award_team_count']
        team_count = data['team_count']
        if team_count > 0:
            no_award_rate = no_award_count / team_count
        else:
            no_award_rate = 0.0
        data['no_award_rate'] = no_award_rate
        print(no_award_rate)
    return stats


# ---------- 3. 写回缓存 ---------- #
def _flush_cache(year: int, area: str, stats: dict):
    """
    全量覆盖式写回缓存：先删后插，保证一致性
    :param year: 年份
    :param area: 赛区名称
    :param stats: 计算得到的学校统计数据
    """
    objs = []
    now = timezone.now()
    for sch, data in stats.items():
        # 创建基础对象参数
        cache_data = {
            'year': str(year),
            'area': area,
            'school': sch,
            'updated_at': now,
        }
        
        # 从STAT_FIELDS添加统计字段
        for field in STAT_FIELDS:
            cache_data[field] = data.get(field, 0)
            
        objs.append(SchoolYearlyCache(**cache_data))

    with transaction.atomic():
        SchoolYearlyCache.objects.filter(year=str(year), area=area).delete()
        SchoolYearlyCache.objects.bulk_create(objs)


# ---------- 4. Facade：对外统一接口 ---------- #
def get_school_yearly_stats(year: int, area: str, use_cache: bool = True) -> dict:
    """
    1) 命中缓存直接返回（如果use_cache=True）
    2) 否则计算 → 写缓存 → 返回
    :param year: 年份
    :param area: 赛区名称
    :param use_cache: 是否使用缓存，默认为True。设置为False时将跳过缓存直接计算
    """
    if use_cache:
        cached = _fetch_cached_stats(year, area)
        if cached is not None:
            return cached

    stats = _compute_stats(year, area)
    
    # 即使不使用缓存读取，也要更新缓存
    _flush_cache(year, area, stats)
    return stats

def get_school_yearly_stats_range(
    start_year: int,
    end_year: int,
    area: str,
    use_cache: bool = True
) -> dict[int, dict[str, dict[str, int]]]:
    """
    返回指定赛区在 [start_year, end_year] 区间内，各年份的学校统计数据：
    {
      2019: { '北大': {...}, '清华': {...}, … },
      2020: { '北大': {...}, '清华': {...}, … },
      …
    }
    每个内层字典的结构与 get_school_yearly_stats(year, area) 相同。
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param use_cache: 是否使用缓存，默认为True
    """
    results: dict[int, dict[str, dict[str, int]]] = {}
    for y in range(start_year, end_year + 1):
        # 复用单年函数，传递use_cache参数
        yearly = get_school_yearly_stats(y, area, use_cache=False)
        results[y] = yearly
    return results

# ---------- 5. 图表数据准备 ---------- #

def get_school_stats_data(year: int, area: str, use_cache: bool = True) -> Dict:
    """
    获取指定年份、赛区的学校统计数据，用于单年度图表展示
    
    :param year: 年份
    :param area: 赛区名称
    :param use_cache: 是否使用缓存
    :return: 统计数据字典
    """
    # 获取学校统计数据
    stats = get_area_full_stats(year, area, use_cache)
    
    # 按队伍数量排序学校列表
    schools = list(stats.keys())
    schools.sort(key=lambda s: stats[s]['team_count'], reverse=True)
    
    # 提取各项指标数据
    team_counts = [stats[s]['team_count'] for s in schools]
    participant_counts = [stats[s]['participant_count'] for s in schools]
    
    # 计算各类获奖数量和比率
    award_counts = [stats[s]['award_count'] for s in schools]
    first_prize_counts = [stats[s]['first_prize_count'] for s in schools]
    second_prize_counts = [stats[s]['second_prize_count'] for s in schools]
    qualification_counts = [stats[s]['qualification_count'] for s in schools]
    final_first_prize_counts = [stats[s]['final_first_prize_count'] for s in schools]
    no_award_counts = [stats[s].get('no_award_team_count', 0) for s in schools]
    
    # 计算各类比率
    award_rates = []
    first_prize_rates = []
    second_prize_rates = []
    qualification_rates = []
    final_first_prize_rates = []
    no_award_rates = []
    
    for i, school in enumerate(schools):
        tc = team_counts[i]
        if tc > 0:
            award_rates.append(round(award_counts[i] / tc * 100, 2))
            first_prize_rates.append(round(first_prize_counts[i] / tc * 100, 2))
            second_prize_rates.append(round(second_prize_counts[i] / tc * 100, 2))
            qualification_rates.append(round(qualification_counts[i] / tc * 100, 2))
            final_first_prize_rates.append(round(final_first_prize_counts[i] / tc * 100, 2))
            no_award_rates.append(round(no_award_counts[i] / tc * 100, 2))
        else:
            award_rates.append(0.0)
            first_prize_rates.append(0.0)
            second_prize_rates.append(0.0)
            qualification_rates.append(0.0)
            final_first_prize_rates.append(0.0)
            no_award_rates.append(0.0)
    
    return {
        'year': year,
        'area': area,
        'schools': schools,
        'stats': stats,
        'team_counts': team_counts,
        'participant_counts': participant_counts,
        'award_counts': award_counts,
        'first_prize_counts': first_prize_counts,
        'second_prize_counts': second_prize_counts,
        'qualification_counts': qualification_counts,
        'final_first_prize_counts': final_first_prize_counts,
        'no_award_counts': no_award_counts,
        'award_rates': award_rates,
        'first_prize_rates': first_prize_rates,
        'second_prize_rates': second_prize_rates,
        'qualification_rates': qualification_rates,
        'final_first_prize_rates': final_first_prize_rates,
        'no_award_rates': no_award_rates
    }

def get_multi_year_stats_data(
    start_year: int,
    end_year: int,
    area: str,
    use_cache: bool = True
) -> Dict:
    """
    获取多年度统计数据，用于多年度图表展示
    
    :param start_year: 起始年份
    :param end_year: 结束年份
    :param area: 赛区名称
    :param use_cache: 是否使用缓存
    :return: 多年度统计数据字典
    """
    # 获取多年度数据
    data_by_year = get_school_yearly_stats_range(start_year, end_year, area, use_cache)
    years = list(range(start_year, end_year + 1))
    
    # 获取所有学校
    all_schools = set()
    for year_data in data_by_year.values():
        all_schools.update(year_data.keys())
    all_schools = list(all_schools)
    
    # 计算各项指标的总和
    total_team_count = {
        s: sum(data_by_year[y].get(s, {}).get('team_count', 0) for y in years)
        for s in all_schools
    }
    
    total_participant_count = {
        s: sum(data_by_year[y].get(s, {}).get('participant_count', 0) for y in years)
        for s in all_schools
    }
    
    total_award_count = {
        s: sum(data_by_year[y].get(s, {}).get('award_count', 0) for y in years)
        for s in all_schools
    }
    
    total_first_prize = {
        s: sum(data_by_year[y].get(s, {}).get('first_prize_count', 0) for y in years)
        for s in all_schools
    }
    
    total_second_prize = {
        s: sum(data_by_year[y].get(s, {}).get('second_prize_count', 0) for y in years)
        for s in all_schools
    }
    
    total_qualification = {
        s: sum(data_by_year[y].get(s, {}).get('qualification_count', 0) for y in years)
        for s in all_schools
    }
    
    total_final_first_prize = {
        s: sum(data_by_year[y].get(s, {}).get('final_first_prize_count', 0) for y in years)
        for s in all_schools
    }
    
    # 计算平均获奖率
    avg_award_rate = {
        s: round(total_award_count[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in all_schools
    }
    
    avg_first_prize_rate = {
        s: round(total_first_prize[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in all_schools
    }
    
    avg_second_prize_rate = {
        s: round(total_second_prize[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in all_schools
    }
    
    avg_qualification_rate = {
        s: round(total_qualification[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in all_schools
    }
    
    avg_final_first_prize_rate = {
        s: round(total_final_first_prize[s] / total_team_count[s] * 100, 2) if total_team_count[s] else 0.0
        for s in all_schools
    }
    
    # 按队伍总数排序学校
    schools_by_team_count = sorted(all_schools, key=lambda s: total_team_count[s], reverse=True)
    
    # 按一等奖总数排序学校
    schools_by_first_prize = sorted(all_schools, key=lambda s: total_first_prize[s], reverse=True)
    
    # 按二等奖总数排序学校
    schools_by_second_prize = sorted(all_schools, key=lambda s: total_second_prize[s], reverse=True)
    
    # 按晋级总数排序学校
    schools_by_qualification = sorted(all_schools, key=lambda s: total_qualification[s], reverse=True)
    
    # 按决赛一等奖总数排序学校
    schools_by_final_first_prize = sorted(all_schools, key=lambda s: total_final_first_prize[s], reverse=True)
    
    return {
        'start_year': start_year,
        'end_year': end_year,
        'area': area,
        'years': years,
        'data_by_year': data_by_year,
        'all_schools': all_schools,
        'schools_by_team_count': schools_by_team_count,
        'schools_by_first_prize': schools_by_first_prize,
        'schools_by_second_prize': schools_by_second_prize,
        'schools_by_qualification': schools_by_qualification,
        'schools_by_final_first_prize': schools_by_final_first_prize,
        'total_team_count': total_team_count,
        'total_participant_count': total_participant_count,
        'total_award_count': total_award_count,
        'total_first_prize': total_first_prize,
        'total_second_prize': total_second_prize,
        'total_qualification': total_qualification,
        'total_final_first_prize': total_final_first_prize,
        'avg_award_rate': avg_award_rate,
        'avg_first_prize_rate': avg_first_prize_rate,
        'avg_second_prize_rate': avg_second_prize_rate,
        'avg_qualification_rate': avg_qualification_rate,
        'avg_final_first_prize_rate': avg_final_first_prize_rate
    }
