"""
URL configuration for pyecharts_django_demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,re_path
from demo import views

app_name = 'demo'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.navigation_view, name='navigation'), # 根路径指向导航页
    # 指定年每年所有赛区汇总分析
    path(
        'range/2019-2023/all/',
        views.range_year_report_all_area_view,
        name='range_year_report_all_area'
    ),

    # 指定范围的各赛区汇总分析
    path(
        'range/<int:start_year>-<int:end_year>/<str:area>/',
        views.range_year_area_report_view,
        name='range_year_area_report'
    ),
    # 显示指定xx年份的所有赛区的分析
    path(
        'report/<int:year>/all/',
        views.yearly_report_view,
        name='yearly_report'
    ),
    # 赛区详情页
    path(
        'area/<int:year>/<str:area>/',
        views.area_detail_view,
        name='area_detail'
    ),
    # 学校详情页
    path(
        'school/<int:year>/<str:school>/',
        views.school_detail_view,
        name='school_detail'
    ),
    # path('update-json-data/', views.update_all_json_data, name='update_json_data'),
]
