# Generated by Django 5.2 on 2025-04-26 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(db_comment='年份', max_length=4)),
                ('area', models.CharField(db_comment='赛区', max_length=50)),
                ('team_count', models.IntegerField(db_comment='队伍数量')),
                ('member_count', models.IntegerField(db_comment='参赛人数')),
            ],
            options={
                'db_table': 'area_stats',
                'db_tablespace': 'yyds_mysql',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='NorthwestSchoolStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(db_comment='年份', max_length=4)),
                ('school', models.CharField(db_comment='学校', max_length=100)),
                ('team_count', models.IntegerField(db_comment='队伍数量')),
            ],
            options={
                'db_table': 'northwest_school_stats',
                'db_tablespace': 'yyds_mysql',
                'managed': True,
            },
        ),
    ]
