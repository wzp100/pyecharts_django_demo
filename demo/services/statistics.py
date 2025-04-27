from demo.models import AreaStats, NorthwestSchoolStats
from django.db import models
from demo.models import Team, TeamMember, TeamAchievement
from .cache import load_data_from_json, save_data_to_json

def get_area_stats(year: int) -> dict:
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

def get_northwest_schools_stats(year: int) -> dict:
    # """先尝试读缓存；否则从 NorthwestSchoolStats 表（或原 Team/TeamMember 逻辑）拉取并缓存。"""
    # filename = f'northwest_schools_{year}.json'
    # data = load_data_from_json(filename)
    # if data:
    #     return data
    #
    # qs = NorthwestSchoolStats.objects.filter(year=year).order_by('-team_count')
    # stats = {row.school: row.team_count for row in qs}
    #
    # # 如果你还需要原先的多表查询逻辑，也可以额外写一个函数，
    # # 在这里回退到那个函数并最终 save_data_to_json(stats, filename)
    # save_data_to_json(stats, filename)
    # return stats
    pass

# demo/services/statistics.py



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
        create_year=year
    )
    for team in qs:
        # 1) 尝试按 member_type 找队长
        captain_qs = TeamMember.objects.filter(
            team_code=team.team_code,
            create_year=str(year),
            member_type='队长'
        )
        if not captain_qs.exists():
            # 2) 回退到 member_type_detail 包含 “队长”
            captain_qs = TeamMember.objects.filter(
                team_code=team.team_code,
                create_year=str(year),
            ).filter(
                models.Q(member_type_detail__contains='队长')
            )

        captain = None
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
    all_stats = get_school_yearly_stats(year)

    # 3) 只保留本区学校，并把 team_count 覆盖到 school_stats 里
    school_stats = {}
    for school, stats in all_stats.items():
        if school in area_team_counts:
            stats['team_count'] = area_team_counts[school]
            school_stats[school] = stats

    return school_stats


def get_school_yearly_stats(year: int, area: str) -> dict:
    """
    返回指定年份、指定赛区的各学校统计：
    {
      school_name: {
        'team_count': int,
        'award_count': int,
        'first_prize_count': int,   # 分赛区一等奖，包括“晋级”
        'second_prize_count': int,
        'qualification_count': int, # 晋级总数
        'final_first_prize_count': int,  # 决赛一等奖
      }, …
    }
    """
    cache_key = f'school_yearly_stats_{area}_{year}.json'
    data = load_data_from_json(cache_key)
    if data is not None:
        return data

    stats: dict = {}

    # 1. 只取本区、本年的团队
    teams = Team.objects.filter(
        competition_zone=area,
        create_year=str(year)
    )

    for team in teams:
        # 2. 找队长（优先 member_type='队长'，否则 member_type_detail 包含“队长”）
        captain_qs = TeamMember.objects.filter(
            team_code=team.team_code,
            create_year=str(year),
            member_type='队长'
        )
        if not captain_qs.exists():
            captain_qs = TeamMember.objects.filter(
                team_code=team.team_code,
                create_year=str(year),
                member_type_detail__contains='队长'
            )
        try:
            captain = captain_qs.get()
        except (TeamMember.DoesNotExist, TeamMember.MultipleObjectsReturned):
            captain = captain_qs.first() if captain_qs else None

        if not captain or not captain.school:
            # 跳过无队长或无学校信息的团队
            continue

        school = captain.school

        # 3. 初始化
        if school not in stats:
            stats[school] = {
                'team_count': 0,
                'award_count': 0,
                'first_prize_count': 0,
                'second_prize_count': 0,
                'qualification_count': 0,
                'final_first_prize_count': 0,
            }
        stats[school]['team_count'] += 1

        # 4. 拉成绩
        try:
            ach = TeamAchievement.objects.get(
                team_code=team,
                year=str(year)
            )
        except TeamAchievement.DoesNotExist:
            ach = None

        # 5. 初赛奖项（“一等奖”或“晋级”都算 first_prize）
        if ach and ach.preliminary_award:
            stats[school]['award_count'] += 1
            pre = ach.preliminary_award or ""
            if '一等奖' in pre or '晋级' in pre:
                stats[school]['first_prize_count'] += 1
            elif '二等奖' in pre:
                stats[school]['second_prize_count'] += 1

        # 6. 晋级总数
        if ach and ach.enterprise_advancement:
            stats[school]['qualification_count'] += 1

        # 7. 决赛一等奖
        if ach and (
            (ach.final_technology and '一等奖' in ach.final_technology) or
            (ach.final_business   and '一等奖' in ach.final_business)
        ):
            stats[school]['final_first_prize_count'] += 1

    # 8. 按队伍数降序
    stats = dict(
        sorted(stats.items(),
               key=lambda kv: kv[1]['team_count'],
               reverse=True)
    )

    # 9. 缓存并返回
    save_data_to_json(stats, cache_key)
    return stats