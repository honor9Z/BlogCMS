from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息，只存放最主要的字段，继承auth模块
    """
    nid = models.BigAutoField(primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    telephone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    avatar = models.FileField(verbose_name='头像', upload_to='avatar', default="/avatar/default.jpeg")
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    站点信息，每个注册用户有一个自己的个人站点
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客后缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    # 与用户信息表一对一关联，关联字段建在blog表中
    user = models.OneToOneField(to='UserInfo', to_field='nid')

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    文章表，存放着所有该用户站点发布的文章
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    #一个文章只能属于一个分类，而一个分类下有多个文章，所以外键建在文章表
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True)
    #一个用户可以发表多篇文章，而一个文章只能由一个用户发表
    user = models.ForeignKey(verbose_name='所属用户', to='UserInfo', to_field='nid')
    #文章中有关键字，关键字可以看做是标签，文章与标签的关系是多对多
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),#自己建的多对多关联的第三张表
    )
    #博客园首页的总的文章大分类下的小分类，与个人站点分类无关，该分类与文章也是一对多关系
    site_article_category=models.ForeignKey("SiteArticleCategory",null=True)

    def __str__(self):
        return self.title


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='文章内容', )
    #若文章表将所有文章内容存入，数据量会很大，所以我们用一个详情表存储，与文章表一对一
    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')
    def __str__(self):
        return self.article.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    #与站点进行多对一关联，外键必须建在多的一方
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'category'
        ordering = ['title']


class Tag(models.Model):
    """
    标签表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表，自己创第三张表的好处是可以自定义表的字段
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        #文章和标签联合唯一
        unique_together = [
            ('article', 'tag'),
        ]


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    up_count = models.IntegerField(default=0)#点赞数

    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    #自关联，用于判断该评论是对文章的评论还是对评论的评论
    parent_comment = models.ForeignKey('self', blank=True, null=True, verbose_name='父级评论')

    def __str__(self):
        return self.content


class CommentUp(models.Model):
    """
    点评论赞表
    """

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    comment = models.ForeignKey("Comment", null=True)


class ArticleUp(models.Model):
    """
    点文章赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    article = models.ForeignKey("Article", null=True)


class ArticleDown(models.Model):
    """
    点down表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    article = models.ForeignKey("Article", null=True)


class SiteCategory(models.Model):
    """
    首页的大分类表，与个人站点分类无关,该分类与文章不直接绑定关系，
    因为该分类下还有小分类，小分类才与文章绑定关系

    大分类（例如计算机编程语言）——>
                小分类（例如python——>文章1
                                        文章2
                                        ……
                            java——>文章（）
                                        ……
                            c++——>文章（）
                                        ……
                            ……）

    """
    name=models.CharField(max_length=32)


    def __str__(self):
        return self.name

class SiteArticleCategory(models.Model):
    """
    首页的大分类下的小分类表，与大分类是多对一关系，与个人站点的分类无关
    """
    name=models.CharField(max_length=32)
    site_category=models.ForeignKey('SiteCategory')


    def __str__(self):
        return self.name