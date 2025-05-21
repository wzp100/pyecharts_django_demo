# 网页分析

每个学校每年的情况（暂缓）
每个赛区每年的情况
每年赛区整体状况
指定年限范围的单个赛区
指定年限范围的所有赛区

-------

# 网页介绍
## 导航
根目录
![img.png](doc/assets/images/img.png)

## xx - xx 年分析
### xx - xx 年赛区分析
![img_1.png](img_1.png)
用于分析某个赛区在指定年限范围内的情况
#### 图表
- 指定年限范围内的各个学校参加队伍数量的统计图
- 指定年限范围内的各个学校参人数数量的表



## xx年分析
### xx年赛区分析
没想好写啥
### xx年xx赛区分析
![img.png](img.png)
可以看到每个学校当年的比赛情况
#### 图表
- 各个学校参加队伍数量的统计图
- 各个学校参人数数量的统计图
- 各个学校各个奖项获奖统计的表格


# 服务器需求
mysql 8
python 3.13
django 4.2
pyecharts 0.6.1

## 部署
ubuntu 24.04
1. 安装python3.13和pip
2. 安装mysql8
3. 部署mysql，传输数据库数据
这一步对于性能不好的机器比较耗时间
3. 安装django4.2
4. 安装pyecharts0.6.1
5. 安装


-------
# URL API

## demo

###  range_year_report
range/<int:start_year>-<int:end_year>/<str:area>/

### yearly_report
指定年份的报告

### area_detail

### school_detail
待定


-------

# 开发任务
- [x] 代码分离将画图的函数分解，方便添加图表易于维护
