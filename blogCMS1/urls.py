"""blogCMS1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.views.static import serve
from blog import views
from blogCMS1 import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),#Django自带

    url(r'^reg/', views.reg),  # 注册功能
    url(r'^login/', views.log_in),#登录功能
    url(r'^log_out/', views.log_out),#注销功能
    url(r'^get_validCode_img/', views.get_validCode_img),  # 验证码功能
    url(r'^index/', views.index),#首页功能
    url(r'^$', views.index),#只输入域名的情况下默认进入首页
    url(r'^cate/(?P<site_article_category>.*)/$', views.index),  # 首页的小分类
                                    #  index(requset,site_article_category=python)

    # 个人站点首页，将个人站点需要用到的路由下发到blog下的urls中
    url(r'^blog/', include('blog.urls')),#路由分发


    #media 配置：我们将网站中上传的文件放置于media文件夹中，
    #            因为该文件夹是新创建的
    #            所以我们需要在settings中进行相应配置，稍后会有配置的代码

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^uploadFile/$', views.uploadFile),#添加文章时上传图片


]
