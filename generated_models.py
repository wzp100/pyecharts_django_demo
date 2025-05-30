# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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


class TeamAchievement(models.Model):
    team_code = models.ForeignKey(Team, models.DO_NOTHING, db_column='team_code', blank=True, null=True, db_comment='团队代码')
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
