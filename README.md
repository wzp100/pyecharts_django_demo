# pyecharts_django_demo 项目

## 项目概述

pyecharts_django_demo 是一个基于 Django 和 pyecharts 的数据可视化项目，主要用于展示学科竞赛的统计数据。项目实现了对竞赛团队、成员和成绩的统计分析，并通过图表直观地展示各赛区、各学校的参赛情况和获奖情况。

## 项目架构

项目采用了典型的 Django MVC 架构，并结合了数据处理和可视化的模块化设计：

```
pyecharts_django_demo/
├── demo/                      # 主应用
│   ├── models.py              # 数据模型定义
│   ├── views.py               # 视图函数
│   ├── services/              # 服务层
│   │   ├── statistics.py      # 统计计算服务
│   │   ├── charts.py          # 图表生成服务
│   │   └── chartsPage.py      # 页面组合服务
│   ├── templates/             # 模板文件
│   └── static/                # 静态资源
├── pyecharts_django_demo/     # 项目配置
└── manage.py                  # Django管理脚本
```

## 核心模块

### 1. 数据模型 (models.py)

项目定义了以下主要数据模型：

- `Team`: 团队信息，包含团队代码、名称、赛区等
- `TeamMember`: 团队成员信息，包含成员代码、姓名、学校等
- `TeamAchievement`: 团队成绩信息，包含各类奖项
- `SchoolYearlyCache`: 学校年度统计缓存，用于提高查询性能

### 2. 统计服务 (statistics.py)

统计服务负责从数据库获取原始数据并进行计算，是整个项目的数据基础。主要功能包括：

#### 数据获取函数

- `get_area_detail_stats`: 获取指定年份、赛区的学校参赛队伍数量
- `get_area_full_stats`: 获取指定年份、赛区的完整学校统计数据
- `get_school_yearly_stats`: 获取指定年份、赛区的学校年度统计数据
- `get_school_yearly_stats_range`: 获取指定年份范围、赛区的学校多年度统计数据

#### 缓存管理函数

- `_fetch_cached_stats`: 从缓存中获取统计数据
- `_flush_cache`: 将统计数据写入缓存

#### 统计计算函数

- `_compute_stats`: 计算统计数据
- `_update_school_record`: 更新学校统计记录
- `_query_raw_data`: 查询原始数据
- `_pick_captain`: 选择队长

#### 图表数据准备函数

- `get_school_stats_data`: 获取单年度统计数据，用于单年度图表
- `get_multi_year_stats_data`: 获取多年度统计数据，用于多年度图表

#### 工具函数

- `calculate_percentage`: 计算百分比
- `extract_schools_from_data`: 从多年度数据中提取学校列表并排序
- `get_stat_fields`: 获取统计字段列表

### 3. 图表服务 (charts.py)

图表服务负责生成各类可视化图表，基于统计服务提供的数据。主要功能包括：

#### 通用工具函数

- `create_generic_bar`: 创建通用柱状图
- `create_generic_table`: 创建通用表格
- `create_page_and_render`: 创建页面并渲染

#### 单年度图表函数

- `build_area_detail_bar`: 构建赛区学校队伍数柱状图
- `build_area_participant_count_bar`: 构建赛区学校参赛人数柱状图
- `build_school_stats_table`: 构建学校统计表格

#### 多年度图表函数

- `build_range_year_report_first_prize_bar`: 构建多年度一等奖柱状图
- `build_range_year_report_first_prize_table`: 构建多年度一等奖表格
- `build_range_year_area_report_participant_count_bar`: 构建多年度参赛队伍数柱状图
- `build_range_year_area_report_participant_count_table`: 构建多年度参赛队伍数表格

#### 渲染函数

- `render_area_detail_chart`: 渲染赛区详情图表
- `render_first_prize_chart`: 渲染一等奖图表
- `render_area_range_chart`: 渲染多年度赛区图表

### 4. 页面组合服务 (chartsPage.py)

页面组合服务负责将多个图表组合成完整的页面，主要功能包括：

- `get_area_detail_page`: 获取赛区详情页面
- `get_range_year_area_report_page`: 获取多年度赛区报告页面

## 代码特点

1. **关注点分离**：
   - `statistics.py`: 负责数据计算和准备
   - `charts.py`: 负责单个图表的生成
   - `chartsPage.py`: 负责页面组合

2. **缓存机制**：
   - 使用 `SchoolYearlyCache` 模型缓存统计结果
   - 提供 `use_cache` 参数控制是否使用缓存

3. **灵活的数据处理**：
   - 所有图表函数都能处理两种格式的输入数据：
     - 完整的统计数据对象
     - 原始的统计数据格式

4. **错误处理**：
   - 在数据获取部分添加了错误处理机制
   - 函数会尝试不同的数据获取方式，确保稳定性

5. **动态字段管理**：
   - 使用 `get_stat_fields` 函数动态获取统计字段
   - 避免硬编码字段名称，提高可维护性

## 数据流程

1. 用户通过浏览器访问特定URL
2. Django视图函数接收请求并调用相应的服务
3. 统计服务从数据库获取原始数据并进行计算
4. 图表服务基于统计数据生成可视化图表
5. 页面组合服务将多个图表组合成完整页面
6. 视图函数将生成的HTML返回给用户

## 扩展性

项目设计具有良好的扩展性：

1. **添加新的统计指标**：
   - 在 `SchoolYearlyCache` 模型中添加新字段
   - 字段会被自动包含在统计计算中

2. **添加新的图表类型**：
   - 在 `charts.py` 中添加新的图表生成函数
   - 在 `chartsPage.py` 中组合新的图表

3. **支持新的数据源**：
   - 实现相应的数据获取函数
   - 确保返回格式与现有函数一致

## 安装与运行

### 环境要求

- Python 3.8+
- Django 5.0+
- pyecharts 2.0+

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/pyecharts_django_demo.git
   cd pyecharts_django_demo
   ```

2. 创建虚拟环境
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 运行迁移
   ```bash
   python manage.py migrate
   ```

5. 启动服务器
   ```bash
   python manage.py runserver
   ```

6. 访问应用
   在浏览器中打开 http://127.0.0.1:8000/

## 使用示例

### 查看单年度赛区统计

访问 `/demo/area/{year}/{area}/` 可以查看指定年份、指定赛区的统计数据，例如：
```
/demo/area/2023/上海赛区/
```

### 查看多年度赛区统计

访问 `/demo/range/{start_year}-{end_year}/{area}/` 可以查看指定年份范围、指定赛区的多年度统计数据，例如：
```
/demo/range/2019-2023/上海赛区/
```

## 许可证

[MIT License](LICENSE)

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


# 开发环境配置
使用.env来隔离开发环境和生产环境

'PASSWORD': 'rootpassword',
'HOST': '192.168.100.2',