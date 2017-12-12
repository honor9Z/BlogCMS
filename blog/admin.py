from django.contrib import admin
from blog.models import *
# Register your models here.
admin.site.register(UserInfo)
admin.site.register(Article)
admin.site.register(Blog)
admin.site.register(ArticleDetail)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(CommentUp)
admin.site.register(ArticleUp)
admin.site.register(SiteArticleCategory)
admin.site.register(SiteCategory)