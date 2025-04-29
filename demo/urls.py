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
    # path('', views.navigation_view, name='navigation'), # 根路径指向导航页
    # 五年汇总分析
    path(
        'report/2019-2023/',
        views.five_year_report,
        name='five_year_report'
    ),
    # 五年各赛区汇总分析
    path(
        'report/2019-2023/',
        views.five_year_report,
        name='five_year_report'
    ),
    # 按年份显示报告
    path('report/<int:year>/', views.yearly_report, name='yearly_report'),
    # 赛区详情页
    path('area/<int:year>/<str:area>/', views.area_detail_view, name='area_detail'), 
    # 学校详情页
    path('school/<int:year>/<str:school>/', views.school_detail_view, name='school_detail'), 
    # path('update-json-data/', views.update_all_json_data, name='update_json_data'),
]
