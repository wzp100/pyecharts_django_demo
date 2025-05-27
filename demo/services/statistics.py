from django.db import models
from django.utils import timezone
from demo.models import (
    Team, TeamMember, TeamAchievement,
    SchoolYearlyCache
)
from django.db.models import Count
from django.db import transaction

STAT_FIELDS: list[str] = [
    'participant_count',
    'team_count',
    'award_count',
    'first_prize_count',
    'second_prize_count',
    'qualification_count',
    'final_first_prize_count',
    'no_award_team_count',      # ← 新增字段示例
]


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

def get_area_full_stats(year: int, area: str) -> dict:
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
    """
    # 1) 从 area_detail_stats 拿到本区每校的 team_count
    area_team_counts = get_area_detail_stats(year, area)

    # 2) 拿到所有学校年度统计
    all_stats = get_school_yearly_stats(year, area)

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
    """真正的统计入口，只关心计算逻辑"""
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
def get_school_yearly_stats(year: int, area: str) -> dict:
    """
    1) 命中缓存直接返回
    2) 否则计算 → 写缓存 → 返回
    :param year: 年份
    :param area: 赛区名称
    """
    cached = _fetch_cached_stats(year, area)
    if cached is not None:
        return cached

    stats = _compute_stats(year, area)
    _flush_cache(year, area, stats)
    return stats

def get_school_yearly_stats_range(
    start_year: int,
    end_year: int,
    area: str
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
    """
    results: dict[int, dict[str, dict[str, int]]] = {}
    for y in range(start_year, end_year + 1):
        # 复用单年函数
        yearly = get_school_yearly_stats(y, area)
        results[y] = yearly
    return results
