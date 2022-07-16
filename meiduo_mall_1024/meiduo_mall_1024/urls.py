"""meiduo_mall_1024 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

"""
注册转换器converter
    在URL层就可以验证RE
"""
from utils.converters import UsernameConverter,MobileConverter  # 1.将UsernameConverter转换器导入
from django.urls import register_converter  # 2. 再从django.urls中的resister_converter中导入转换器
# --->每个自定义转换器的需要
# 注册的方式类似源码中标记的 参数1：转换器类，参数2：以及转换器的名字
# ----->其中转换器的名字为自定义的，需要在app的对应子应用路由中使用
register_converter(UsernameConverter, 'username')
register_converter(MobileConverter, 'mobile')

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('apps.users.urls')),
    path('',include('apps.verifications.urls')),
    path('',include('apps.oauth.urls')),
    path('',include('apps.areas.urls')),
]
