from django.conf.urls import url,include
from blogCMS1 import settings
from  blog import views
urlpatterns = [
    #用户修改个人资料功能
    url(r'^edituser/(\d+)$', views.edituser),
    #个人站点首页，需要渲染个人分类、标签和日期的归档，所以需要用到正则
    url(r'^(?P<username>.*)/(?P<condition>tag|category|date)/(?P<para>.*)', views.homeSite),
    #路由反向解析，在模板页面中直接用别名即可
    url(r'^(?P<username>.*)', views.homeSite,name="aaa"),
    #文章详情页面
    url(r'^(?P<username>.*)/article_detail/(?P<article_nid>\d+)', views.article_detail),
    #文章赞、踩功能
    url(r'^updown/$', views.updown),
    url(r'^comment/$', views.comment),    #文章评论功能
    #显示文章已发表的评论，树状结构
    url(r'^commentTree/(?P<article_id>\d+)$', views.commentTree),
    url(r'^backend/$', views.backendindex),#后台管理首页
    url(r'^backend/addarticle/$', views.addarticle),#后台管理添加新文章功能
    url(r'^backend/editarticle/(\d+)$', views.editarticle),#编辑文章
    url(r'^backend/del/(\d+)', views.delarticle),#删除文章

]
