from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50,verbose_name='昵称',default="")
    birthday = models.DateField(verbose_name="生日",null=True,blank=True)
    gender = models.CharField('性别',choices=(('male','男'),('female','女')),max_length=10,default='female')
    address = models.CharField('地址',max_length=100,default='')
    mobile = models.CharField('手机号',max_length=11,null=True,blank=True)
    image = models.ImageField(upload_to='image/%Y/%m',default='image/default.png',max_length=100)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_unread_nums(self):
        #只能在这里引入，否则会循环引用,获取未读消息数量
        from operation.models import UserMessage
        return UserMessage.objects.filter(user=self.id,has_read=False).count()


class EmailVerifyRecord(models.Model):
    code = models.CharField("验证码",max_length=20)
    email = models.EmailField("邮箱",max_length=50)
    send_type = models.CharField('验证码类型',choices=(("register","注册"),("forget","找回密码"),('update_email','修改邮箱')),max_length=30)
    send_time = models.DateTimeField('发送时间',default=datetime.now)

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}{}'.format(self.code,self.email)



class Banner(models.Model):
    title = models.CharField("标题",max_length=100)
    image = models.ImageField("轮播图",upload_to='banner/%Y%m',max_length=100)
    url = models.URLField('访问地址',max_length=200)
    index = models.IntegerField('顺序',default=1)
    add_time =models.DateTimeField('添加时间',default=datetime.now)

    class Meta:
        verbose_name = "轮播图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title