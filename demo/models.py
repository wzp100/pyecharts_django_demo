# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class YYDSManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('yyds_mysql')


class Team(models.Model):
    team_code = models.CharField(primary_key=True, max_length=50, db_comment='团队代码')
    team_name = models.CharField(max_length=100, blank=True, null=True, db_comment='团队名称')
    competition_zone = models.CharField(max_length=50, blank=True, null=True, db_comment='赛区')
    competition_topic = models.TextField(blank=True, null=True, db_comment='赛题')
    enterprise_proposition = models.TextField(blank=True, null=True, db_comment='企业命题')
    enterprise_tech_direction = models.TextField(blank=True, null=True, db_comment='企业命题技术方向')
    work_name = models.TextField(blank=True, null=True, db_comment='作品名称')
    create_year = models.CharField(max_length=4, blank=True, null=True)
    is_current = models.IntegerField(blank=True, null=True)
    previous_version_id = models.IntegerField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team'
        app_label = 'demo'  # 确保这是正确的应用名
        # 添加下面这行指定使用MySQL数据库
        db_tablespace = 'yyds_mysql'


class TeamAchievement(models.Model):
    team_code = models.OneToOneField(
        Team,
        on_delete=models.DO_NOTHING,
        db_column='team_code',
        primary_key=True,
        db_comment='团队代码'
    )
    preliminary_award = models.CharField(max_length=50, blank=True, null=True, db_comment='初赛奖项')
    enterprise_award = models.CharField(max_length=50, blank=True, null=True, db_comment='企业奖项')
    enterprise_advancement = models.IntegerField(blank=True, null=True, db_comment='企业晋级')
    final_technology = models.CharField(max_length=50, blank=True, null=True, db_comment='决赛技术')
    final_business = models.CharField(max_length=50, blank=True, null=True, db_comment='决赛商业')
    best_paper = models.IntegerField(blank=True, null=True, db_comment='最佳论文')
    best_investment_pitch = models.IntegerField(blank=True, null=True, db_comment='最具投资/最佳路演')
    year = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_achievement'
        app_label = 'demo'  # 确保这是正确的应用名
        # 添加下面这行指定使用MySQL数据库
        db_tablespace = 'yyds_mysql'


class TeamMember(models.Model):
    member_code = models.CharField(primary_key=True, max_length=50, db_comment='个人代码')
    team_code = models.CharField(max_length=50, blank=True, null=True, db_comment='团队代码')
    member_name = models.CharField(max_length=50, blank=True, null=True, db_comment='姓名')
    gender = models.CharField(max_length=10, blank=True, null=True, db_comment='性别')
    member_type = models.CharField(max_length=50, blank=True, null=True, db_comment='人员类型')
    member_type_detail = models.CharField(max_length=100, blank=True, null=True, db_comment='人员类型详细')
    school = models.CharField(max_length=100, blank=True, null=True, db_comment='参赛成员本人所在学校')
    email = models.CharField(max_length=100, blank=True, null=True, db_comment='电子邮箱')
    title = models.CharField(max_length=50, blank=True, null=True, db_comment='职称')
    position = models.CharField(max_length=50, blank=True, null=True, db_comment='行政职务')
    research_direction = models.TextField(blank=True, null=True, db_comment='研究方向')
    degree_level = models.CharField(max_length=50, blank=True, null=True, db_comment='学位层级')
    degree_type = models.CharField(max_length=50, blank=True, null=True, db_comment='学位类型')
    major = models.CharField(max_length=100, blank=True, null=True, db_comment='专业')
    grade = models.CharField(max_length=50, blank=True, null=True, db_comment='年级')
    enrollment_year = models.TextField(blank=True, null=True, db_comment='入学年份')  # This field type is a guess.
    expected_graduation_year = models.TextField(blank=True, null=True, db_comment='预计毕业年份')  # This field type is a guess.
    student_id = models.CharField(max_length=50, blank=True, null=True, db_comment='学号')
    qq_number = models.CharField(max_length=20, blank=True, null=True, db_comment='QQ号码')
    address = models.TextField(blank=True, null=True, db_comment='地址')
    team_order = models.IntegerField(blank=True, null=True, db_comment='团队顺序')
    create_year = models.CharField(max_length=4, blank=True, null=True, db_comment='创建年份')
    is_current = models.IntegerField(blank=True, null=True, db_comment='是否当前')
    previous_version_id = models.IntegerField(blank=True, null=True, db_comment='前一版本ID')

    class Meta:
        managed = False
        db_table = 'team_member'
        app_label = 'demo'  # 确保这是正确的应用名
        # 添加下面这行指定使用MySQL数据库
        db_tablespace = 'yyds_mysql'


class SchoolYearlyCache(models.Model):
    """
    缓存按 年+赛区+学校 汇总的统计数据
    """
    year       = models.CharField(max_length=4, db_comment='年份')
    area       = models.CharField(max_length=50, db_comment='赛区')
    school     = models.CharField(max_length=100, db_comment='学校名称')
    participant_count      = models.IntegerField(default=0, db_comment='参赛人数')
    team_count             = models.IntegerField(default=0, db_comment='参赛队伍数量')
    award_count            = models.IntegerField(default=0, db_comment='获奖数量')
    first_prize_count      = models.IntegerField(default=0, db_comment='一等奖数量')
    second_prize_count     = models.IntegerField(default=0, db_comment='二等奖数量')
    third_prize_count = models.IntegerField(default=0, db_comment='三等奖数量')
    qualification_count    = models.IntegerField(default=0, db_comment='晋级决赛数量')
    final_first_prize_count= models.IntegerField(default=0, db_comment='决赛一等奖数量')
    no_award_team_count    = models.IntegerField(default=0, db_comment='失败的队伍数量')
    no_award_rate          = models.FloatField(default=0.0, db_comment='未获奖率')
    award_rate = models.FloatField(default=0.0, db_comment='获奖率')
    first_prize_rate = models.FloatField(default=0.0, db_comment='一等奖率')
    second_prize_rate = models.FloatField(default=0.0, db_comment='二等奖率')
    qualification_rate = models.FloatField(default=0.0, db_comment='晋级决赛率')
    final_first_prize_rate = models.FloatField(default=0.0, db_comment='决赛一等奖率')
    updated_at = models.DateTimeField(auto_now=True, db_comment='最后更新时间')


    class Meta:
        unique_together = (("year", "area", "school"),)
        indexes = [
            models.Index(fields=["year", "area"]),
        ]
        verbose_name = "学校年度统计缓存"
        verbose_name_plural = verbose_name

# class AreaStats(models.Model):
#     """
#     赛区年度统计信息ORM模型（主要用于导航及数据聚合）
#     新增subproject（子项目/专项/题目组）字段
#     """
#     year = models.CharField(max_length=4, db_comment='年份')
#     area = models.CharField(max_length=50, db_comment='赛区')
#     subproject = models.CharField(max_length=100, blank=True, null=True, db_comment='子项目/专项/题目组')
#     team_count = models.IntegerField(db_comment='队伍数量')
#     member_count = models.IntegerField(db_comment='参赛人数')
#
#     class Meta:
#         managed = True
#         db_table = 'area_stats'
#         app_label = 'demo'
#         db_tablespace = 'yyds_mysql'
#
# class NorthwestSchoolStats(models.Model):
#     """
#     西北赛区各学校年度统计ORM模型
#     """
#     year = models.CharField(max_length=4, db_comment='年份')
#     school = models.CharField(max_length=100, db_comment='学校')
#     team_count = models.IntegerField(db_comment='队伍数量')
#
#     class Meta:
#         managed = True
#         db_table = 'northwest_school_stats'
#         app_label = 'demo'
#         db_tablespace = 'yyds_mysql'
