from django import forms
from django.forms import widgets,ValidationError
from blog import models


class LoginForm(forms.Form):#必须继承
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)
    def clean_username(self):#钩子函数
        if len(self.cleaned_data.get("username"))>5:
            print(self.cleaned_data.get("password"))
            return self.cleaned_data.get("username")
        else:
            raise
    def clean_password(self):
        pass
    def clean(self):
        if self.cleaned_data["password"] == self.cleaned_data["repeat_password"]:
            return self.cleaned_data

#注册页面的form组件
class RegForm(forms.Form):#必须继承
    username=forms.CharField(max_length=32,
                             min_length=5,
                             error_messages={'required':'用户名不能为空'},
                             widget=widgets.TextInput(attrs={"class":"form-control","placeholder":"请输入用户名"})
                             )
    password=forms.CharField(max_length=32,
                             min_length=6,
                             widget=widgets.PasswordInput(
                                 attrs={"class": "form-control", "placeholder": "请输入密码"}
                             ))
    repeat_pwd = forms.CharField(min_length=6, widget=widgets.PasswordInput(
        attrs={"class": "form-control", "placeholder": "请再次输入密码"}
    ))

    email = forms.EmailField(widget=widgets.EmailInput(
        attrs={"class": "form-control", "placeholder": "请输入邮箱"}
    ))

    def clean_username(self):
        """
        钩子函数,判断用户名是否已存在
        :return:
        """
        ret = models.UserInfo.objects.filter(username=self.cleaned_data.get("username"))
        if not ret:
            return self.cleaned_data.get("username")
        else:
            raise ValidationError("用户名已注册")

    def clean_password(self):
        """
        钩子函数，规定密码不能是全数字或全字母
        :return:
        """
        ret = self.cleaned_data.get("password")
        if ret.isdigit():
            raise ValidationError("密码不能全是数字")
        elif ret.isalpha():
            raise ValidationError("密码不能全是字母")
        else:
            return ret

    # def clean_validCode(self):
    #     if self.cleaned_data.get("validCode") == self.request.session.get("validCode"):
    #         return self.cleaned_data.get("validCode")
    #     else:
    #         raise ValidationError("验证码错误")

    def clean(self):
        """
        全局钩子函数，判断两次密码是否一致
        :return:
        """
        if self.cleaned_data.get("password") == self.cleaned_data.get("repeat_pwd"):
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致")

    # def __init__(self, request, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.request = request



from blog.plugins import xss_plugin
class ArticleForm(forms.Form):

    title=forms.CharField(max_length=20,error_messages={
        "required":"不能为空",
    },widget=widgets.Input(attrs={"class":"form-control"}))

    content=forms.CharField(error_messages={
        "required":"不能为空",
    },widget=widgets.Textarea(attrs={"id":"id_content"}))

    def clean_content(self):

        html_str=self.cleaned_data.get("content")
        clean_content=xss_plugin.filter_xss(html_str)#过滤非法标签和属性
        self.cleaned_data["content"]=clean_content

        return self.cleaned_data.get("content")

