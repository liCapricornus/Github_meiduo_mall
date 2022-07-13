from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

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
