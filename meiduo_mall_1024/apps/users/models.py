from django.db import models

# Create your models here.

"""
定义用户模型类
    继承重写，功能增加（手机号功能）
"""
# 方式1.自己定义模型
# 密码我们要加密，还要实现登录的时候密码的验证
# class User(models.Model):
#     username=models.CharField(max_length=20,unique=True)
#     password=models.CharField(max_length=20)
#     mobile=models.CharField(max_length=11,unique=True)

# 方式2. django 自带一个用户模型
# 这个用户模型 有密码的加密 和密码的验证

# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """数据库 User 表"""
    mobile=models.CharField(max_length=11,unique=True)
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
    #                                     on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table='md_users'
        verbose_name='用户管理'
        verbose_name_plural=verbose_name