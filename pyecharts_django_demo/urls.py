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
from django.urls import include
from django.urls import re_path as url
from demo import admin
from demo import views

urlpatterns = [
    #    path('admin/', admin.site.urls),
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.navigation_view, name='home'),
    url(r'^demo/', include('demo.urls')),
    url(r'^report/(?P<year>\d+)/$', views.yearly_report, name='yearly_report')
]
