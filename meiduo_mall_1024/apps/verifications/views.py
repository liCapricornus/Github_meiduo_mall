import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.users.models import User

"""
前端
     拼接一个 url 。然后给 img 。img会发起请求
     url=http://mp-meiduo-python.itheima.net/image_codes/ca732354-08d0-416d-823b-14b1d77746d2/

     url=http://ip:port/image_codes/uuid/

后端
    请求              接收路由中的 uuid
    业务逻辑          生成图片验证码和图片二进制。通过redis把图片验证码保存起来
    响应              返回图片二进制

    路由：     GET     image_codes/uuid/
    步骤：         
            1. 接收路由中的 uuid
            2. 生成图片验证码和图片二进制
            3. 通过redis把图片验证码保存起来
            4. 返回图片二进制
"""

class ImageCodeView(View):
    """图片验证码功能实现"""
    def get(self,request,uuid):
        # 1. 接收路由中的uuid
        # 2. 生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 是图片验证码的内容 例如： yougizz
        # image 是图片二进制
        text, image = captcha.generate_captcha()
        # 3. 通过redis把图片验证码保存起来
        # 3.1 进行redis的连接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('captcha_code')
        # 3.2 指令操作
        # 设置键值及过期时间，以秒为单位
        # setex key seconds value
        redis_cli.setex(uuid,100,text)  # 100s
        # 4. 返回图片二进制
        # HttpResponse(content=响应体, content_type=响应体数据类型, status=状态码)
        # content_type 的语法形式是： 大类/小类
        return HttpResponse(image,content_type='image/jpeg')


"""
------------------容联云发送短信----------------

1.注册
我们提供免费开发测试，【免费开发测试前，请先 注册 成为平台用户】。

2.绑定测试号
免费开发测试需要在"控制台—管理—号码管理—测试号码"绑定 测试号码 。

3.开发测试
开发测试过程请参考 短信业务接口 及 Demo示例 / sdk参考（新版）示例。Java环境安装请参考"新版sdk"。

4.免费开发测试注意事项
    4.1.免费开发测试需要使用到"控制台首页"，开发者主账户相关信息，如主账号、应用ID等。

    4.2.免费开发测试使用的模板ID为1，具体内容：【云通讯】您的验证码是{1}，请于{2}分钟内正确输入。其中{1}和{2}为短信模板参数。

    4.3.测试成功后，即可申请短信模板并 正式使用 。
"""

"""
--------------------------短信验证码sms_code 功能实现-------------------
前端
            当用户输入完 手机号，图片验证码之后，前端发送一个axios请求
            sms_codes/18310820644/?image_code=knse&image_code_id=b7ef98bb-161b-437a-9af7-f434bb050643

后端

    请求：     接收请求，获取请求参数（路由有手机号， 用户的图片验证码和UUID在查询字符串中）
    业务逻辑：  验证参数， 验证图片验证码， 生成短信验证码，保存短信验证码，发送短信验证码
    响应：     返回响应
            {‘code’:0,'errmsg':'ok'}


    路由：     GET     sms_codes/18310820644/?image_code=knse&image_code_id=b7ef98bb-161b-437a-9af7-f434bb050643
        获取请求路径中的查询字符串参数（形如?k1=v1&k2=v2），可以通过request.GET属性获取，
    返回QueryDict对象。
    步骤：
            1. 获取请求参数
            2. 验证参数
            3. 验证图片验证码
            4. 生成短信验证码
            5. 保存短信验证码
            6. 发送短信验证码
            7. 返回响应

需求 --》 思路 --》 步骤 --》 代码

debug 模式 就是调试模式 （小虫子）
debug + 断点配合使用 这个我们看到程序执行的过程

添加断点 在函数体的第一行添加！！！！！
"""

class SmsCodeView(View):
    """短信验证码功能实现"""
    def get(self,request,mobile):  # 此句 mobile 已获取
        # 1. 获取请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2. 验证参数
        if not all([image_code,uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不足！'})

        # 3. 验证图片验证码
        # 3.1连接redis
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('captcha_code')
        # 3.2获取数据
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码已过期'})
        # 3.3对比数据
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        # 4. 生成短信验证码
        from random import randint
        sms_code = '%06d'%randint(0,999999)

        # 5. 保存短信验证码
        redis_cli.setex(mobile,300,sms_code)

        # 6. 发送短信验证码
        from libs.yuntongxun.sms import CCP
        #  ccp.send_template_sms('13203991352', ['331024', 3], 1)
        CCP().send_template_sms(mobile, [sms_code, 3], 1)  # 此句需处理2min 离谱！
        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK！'})

