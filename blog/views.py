import random
from django.shortcuts import render,HttpResponse,redirect
from django import forms
# Create your views here.
from blog.forms import  *
from blogCMS1 import settings
from django.contrib import auth

def index(request,*args,**kwargs):
    print('222222222222222222222')
    if kwargs:#用户点击超链接，显示指定小分类下的文章
        article_list=models.Article.objects.filter(site_article_category__name=kwargs.get("site_article_category"))
    else:#默认，显示全部文章
        article_list=models.Article.objects.all()
    cate_list=models.SiteCategory.objects.all()#所有大分类
    return render(request,'index.html',{'article_list':article_list,'cate_list':cate_list})

def log_out(request):
    auth.logout(request)
    return redirect("/login/")

def log_in(request):
    if request.is_ajax():
        username=request.POST.get('username')
        password=request.POST.get('password')
        validCode=request.POST.get('validCode')
        login_response={"is_login":False,"error_msg":None}
        if validCode.upper()==request.session.get("keepValidCode").upper():#检验验证码
            user=auth.authenticate(username=username,password=password)#验证码正确时校验用户
            if user:#用户正确
                login_response["is_login"]=True
                auth.login(request,user) #  session   request.session[is_login]=True
            else:#用户名或密码输入错误
                login_response["error_msg"] = "username or password error"
        else:#验证码错误
            login_response["error_msg"]='validCode error'
        import json
        #检验通过
        return HttpResponse(json.dumps(login_response))
    return render(request,"login.html")



def edituser(request,nid):
    user_obj=models.UserInfo.objects.get(nid=nid)
    return render(request,'edit_user.html',{'user_obj':user_obj})



#自己写的验证码
import random
def get_validCode_img(request):
    def random_color():#随机颜色
        the_color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        return the_color
    def random_int():#随机数字
        x_y=random.randint(0,150)
        return x_y
    from io import BytesIO
    from PIL import Image,ImageDraw,ImageFont
    img=Image.new(mode='RGB',size=(120,40),color=random_color())
    # img = Image.new(mode="RGB", size=(120, 40), color=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))

    draw=ImageDraw.Draw(img,mode='RGB')
    font=ImageFont.truetype("blog/static/font/kumo.ttf",25)
    valid_list=[]
    for i in range(5):
        random_num=str(random.randint(0,9))#数字
        random_lower=chr(random.randint(65,90))#小写字母
        random_upper=chr(random.randint(97,122))#大写字母
        random_char=random.choice([random_num,random_lower,random_upper])#随机选
        draw.text([5+i*24,10],random_char,random_color(),font=font)
                #（坐标，   随机文本 ，     随机颜色，      字体）
        for i in range(100):#画噪点
            draw.point([random_int(), random_int()], fill=random_color())
        for i in range(3):#画线
            draw.line((random_int(), random_int(), random_int(), random_int()), fill=random_color())

        valid_list.append(random_char)
        #写入内存中
    f = BytesIO()
    img.save(f, "png")#以png格式
    data = f.getvalue()
    valid_str = "".join(valid_list)
    request.session["keepValidCode"] = valid_str#将验证码的字符串写入session中，方便以后校验
    return HttpResponse(data)


def reg(request):
    if request.is_ajax():#ajax提交
        form_obj=RegForm(request.POST)#拿到页面提交的form对象
        print('................',form_obj)
        regResponse={"user":None,"errorsList":None}
        if form_obj.is_valid():#数据正常
            username=form_obj.cleaned_data["username"]
            password=form_obj.cleaned_data["password"]
            email=form_obj.cleaned_data.get("email")
            pic=request.FILES.get("pic")#头像
            #用户表中添加一条信息，即增加一条表记录
            user_obj=models.UserInfo.objects.create_user(username=username,password=password,email=email,avatar=pic,nickname=username)
            print(user_obj.avatar,"......")#路径
            regResponse["user"]=user_obj.username

        else:#数据异常
            regResponse["errorsList"]=form_obj.errors#异常信息
        import json
        #ajax返回的数据必须是json字符串
        return HttpResponse(json.dumps(regResponse))
    form=RegForm()#实例化组件
    return render(request,'reg.html',{'form':form})


def homeSite(request,username,**kwargs):
    # 查询当前用户站点
    current_user=models.UserInfo.objects.filter(username=username).first()
    if not current_user:#如果当前用户异常，返回404页面
        return render(request,'notFound.html')
    # 查询当前用户站点所有文章
    article_list=models.Article.objects.filter(user=current_user)

    # 查询 当前用户的分类归档，格式为：
    '''
            python(3)
            linux(5)
            go(1)
    '''
    from django.db.models import Count, Sum
    '''
     可先在视图函数中利用双下划綫查询的方式取出对象再渲染到模板中，
    本文用的方法是直接在模板中用.的方法进行取对象
    双下划线方式如下：
    current_blog=current_user.blog
    category_list = models.Category.objects.all().filter(blog=current_blog).annotate(
        c=Count("article__nid")).values_list("title", "c")
    print(category_list)  # <QuerySet [<Category: yuan的go>, <Category: yuan的java>]>

    '''
    # 查询当前用户的标签归档

    '''
        a(3)
        b(5)
        c(1)
    '''
    '''
    双下划线查询方式：
    tag_list = models.Tag.objects.all().filter(blog=current_blog).annotate(c=Count("article__nid")).values_list("title",
    print(tag_list)  # <QuerySet [('基础知识', 3), ('插件框架', 0), ('web开发', 1)]>

    '''
    # 查询当前用户的日期归档

    '''
    2016-12（2）
    2017-1（3）
    '''
    #因为时间对象用Django原生api方式取无法做到格式化输出，所以这里必须用到extra（数据库查询语句）
    date_list=models.Article.objects.filter(user=current_user).extra(select={"filter_create_date":"strftime('%%Y/%%m',create_time)"}).values_list("filter_create_date").annotate(Count("nid"))
    print(date_list)

    if kwargs:
        if kwargs.get("condition") == "category":
            #分类归档
            article_list = models.Article.objects.filter(user=current_user, category__nid=kwargs.get("para"))
            print(article_list)
        elif kwargs.get("condition") == "tag":
            #标签归档
            article_list = models.Article.objects.filter(user=current_user, tags__nid=kwargs.get("para"))
        elif kwargs.get("condition") == "date":
            #时间归档
            year, month = kwargs.get("para").split("/")
            article_list = models.Article.objects.filter(user=current_user, create_time__year=year,
                                                         create_time__month=month)

    return render(request,"homeSite.html",locals())


def article_detail(request,username,article_nid):
    # 查询当前用户
    current_user = models.UserInfo.objects.filter(username=username).first()
    if not current_user:#用户异常时返回404页面
        return render(request, 'notFound.html')
    from django.db.models import Count, Sum
    #前端渲染时间时依然需使用extra
    date_list = models.Article.objects.filter(user=current_user).extra(
        select={"filter_create_date": "strftime('%%Y/%%m',create_time)"}).values_list(
        "filter_create_date").annotate(Count("nid"))
    #得到用户点击的文章标题对应的文章详情
    current_article=models.Article.objects.filter(nid=article_nid).first()
    return render(request,'article_detail.html',locals())

import json
from django.db.models import F
def updown(request):
    updown_response={'state':True,'is_repeat':None,'is_login':True,'down':None}
    if not request.user.is_authenticated():
        #未登录状态下不可赞和踩
        updown_response['is_login']=False
        return HttpResponse(json.dumps(updown_response))

    user_id=request.user.nid#访客已登录，得到访客id
    article_id=request.POST.get('article_id')#得到访客查看的文章id
    # the_user=models.UserInfo.objects.filter(nid=user_id)
    # the_article=models.Article.objects.filter(nid=article_id)
    if request.POST.get('up')=='up':#判断点的是赞
        if models.ArticleUp.objects.filter(user_id=user_id, article_id=article_id):
            #若用户已点过赞，不允许再点
            updown_response['state']= False
            updown_response['is_repeat']=True
        else:
            try:#将用户的点赞请求录入数据库
                models.ArticleUp.objects.create(user_id=user_id, article_id=article_id)
                models.Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
                print('..........')
            except:#捕捉到异常返回
                updown_response["state"] = False
    elif request.POST.get('down')=='down':#踩请求（同理）
        if models.ArticleDown.objects.filter(user_id=user_id, article_id=article_id):
            updown_response['state']= False
            updown_response['is_repeat']=True
        else:
            try:
                models.ArticleDown.objects.create(user_id=user_id, article_id=article_id)
                models.Article.objects.filter(nid=article_id).update(down_count=F("up_count") + 1)
                print('..........')
            except:
                updown_response["state"] = False
    return HttpResponse(json.dumps(updown_response))

from django.db import transaction

def comment(request):
    comment_response={'is_login':True}
    print(comment_response)
    if not request.user.is_authenticated():
        comment_response['is_login']=False
        return HttpResponse(json.dumps(comment_response))
    content=request.POST.get('content')
    article_id=request.POST.get('article_id')
    user_id=request.user.nid
    print('===================',content)
    if request.POST.get("parent_comment_id"):    #   处理子评论
        with transaction.atomic():
            pid=request.POST.get("parent_comment_id")
            comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_id,content=content,parent_comment_id=pid)
            comment_response["parent_comment_username"]=comment_obj.parent_comment.user.username
            comment_response["parent_comment_content"]=comment_obj.parent_comment.content

    else:   #  处理的文章评论，即根评论
        with transaction.atomic():
            comment_obj=models.Comment.objects.create(article_id=article_id,user_id=user_id,content=content)
            models.Article.objects.filter(nid=article_id).update(comment_count=F("comment_count")+1)

    comment_response["create_time"] = str(comment_obj.create_time)
    comment_response["comment_id"] = comment_obj.nid
    print('ok')
    return HttpResponse(json.dumps(comment_response))



def commentTree(request,article_id):

    print('s=====================')
    comment_list=models.Comment.objects.filter(article_id=article_id).values("nid","content","parent_comment_id","user__username","user__avatar",)
    j=0
    for i in comment_list:
        print('iiiiiiiiiiiiiii',i)
        create_times=models.Comment.objects.filter(nid=i['nid']).first()
        print(str(create_times.create_time)[:19])
        a=str(create_times.create_time)[:19]
        comment_list[j]['create_time']=a
        j+=1
        # print('jjj',comment_list[1])
    # for j in comment_list.length:
    #     comment_list[j]['create_time']=a
    print(comment_list)

    comment_dict = {}

    for comment in comment_list:

        comment["chidren_commentList"] = []
        comment_dict[comment["nid"]] = comment



    #====================================找父评论====================================================

    commentTree = []

    for comment in comment_list:  # comment :  {'id': 1, 'content': '...', 'Pid': None, 'chidren_commentList': [{'id': 5, 'content': '...', 'Pid': 1, 'chidren_commentList': []},]},
        pid = comment.get("parent_comment_id")
        if pid:
            print(comment)  # {'id': 4, 'content': '...', 'Pid': 1, 'chidren_commentList': []}
            comment_dict[pid]["chidren_commentList"].append(comment)
        else:
            commentTree.append(comment)

    print(commentTree)
    print('+++++',comment_dict)
    import json
    return HttpResponse(json.dumps(commentTree))



def backendindex(request):
    print('-------------------')
    if not request.user.is_authenticated():
        return redirect("/login/")

    article_list=models.Article.objects.filter(user=request.user).all()
    return  render(request,"backendindex.html",{"article_list":article_list})



import datetime
def addarticle(request):
    response={'result':None}
    if request.method=="POST":
        article_form = ArticleForm(request.POST)
        if article_form.is_valid():
            title=article_form.cleaned_data.get("title")
            content=article_form.cleaned_data.get("content")
            article_obj=models.Article.objects.create(title=title,desc=content[0:30],create_time=datetime.datetime.now(),user=request.user)
            models.ArticleDetail.objects.create(content=content,article=article_obj)
            response['result'] = '添加成功<a href="/blog/backend/">点击返回</a>'
        else:
            response['result']='添加失败'

        return HttpResponse(response['result'])

    article_form=ArticleForm()
    return render(request,"addarticle.html",{"article_form":article_form})




def uploadFile(request):

    file_obj=request.FILES.get("imgFile")
    file_name=file_obj.name

    from blogCMS1 import settings
    import os
    path=os.path.join(settings.MEDIA_ROOT,"article_uploads",file_name)
    with open(path,"wb") as f:
        for i in file_obj.chunks():
            f.write(i)

    response={
        "error":0,
        "url":"/media/article_uploads/"+file_name+"/"
    }

    import json
    return HttpResponse(json.dumps(response))


def delarticle(request,nid):
    models.Article.objects.filter(nid=nid).delete()
    return redirect('/blog/backend/')


def editarticle(request,nid):
    response={'result':None}
    if request.method=="POST":
        article_form = ArticleForm(request.POST)
        if article_form.is_valid():
            title=article_form.cleaned_data.get("title")
            content=article_form.cleaned_data.get("content")
            article_obj=models.Article.objects.filter(nid=nid).update(title=title,desc=content[0:30],create_time=datetime.datetime.now(),user=request.user)
            models.ArticleDetail.objects.update(content=content)
            response['result'] = '添加成功<a href="/blog/backend/">点击返回</a>'
        else:
            response['result']='添加失败'

        return HttpResponse(response['result'])
    article_obj=models.Article.objects.get(nid=nid)
    title=article_obj.title
    content=article_obj.articledetail.content
    article_form=ArticleForm({"title":title,"content":content})
    return render(request,"editarticle.html",{"article_form":article_form,'nid':nid})



