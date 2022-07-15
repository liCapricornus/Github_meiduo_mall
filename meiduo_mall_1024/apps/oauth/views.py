import json
import re

from django.contrib.auth import login
from django.http import JsonResponse
from django.views import View


"""
第三方登录的步骤：
1. QQ互联开发平台申请成为开发者（可以不用做）
2. QQ互联创建应用（可以不用做）
3. 按照文档开发（看文档的）

3.1 准备工作                        -----------------------------------准备好了

    # QQ登录参数
    # 我们申请的 客户端id
    QQ_CLIENT_ID = '101474184'          appid
    # 我们申请的 客户端秘钥
    QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'   appkey
    # 我们申请时添加的: 登录成功后回调的路径
    QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'


3.2 放置 QQ登录的图标（目的： 让我们点击QQ图标来实现第三方登录）  ------------- 前端做好了

3.3 根据oauth2.0 来获取code 和 token                      ---------------我们要做的
    对于应用而言，需要进行两步：
    1. 获取Authorization Code；            表面是一个链接，实质是需要用户同意，然后获取code

    2. 通过Authorization Code获取Access Token

3.4 通过token换取 openid                                ----------------我们要做的
    openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份，
    或将其与用户在网站上的原有账号进行绑定。

把openid 和 用户信息 进行一一对应的绑定


生成用户绑定链接 ----------》获取code   ------------》获取token
 ------------》获取openid --------》保存openid

"""

"""
生成用户绑定链接

前端： 当用户点击QQ登录图标的时候，前端应该发送一个axios(Ajax)请求

后端：
    请求
    业务逻辑        调用QQLoginTool 生成跳转链接
    响应            返回跳转链接 {"code":0,"qq_login_url":"http://xxx"}
    路由          GET   qq/authorization/
        axios.get(this.host + '/qq/authorization/?next=' + next, {
    步骤      
            1. 生成 QQLoginTool 实例对象
            2. 调用对象的方法生成跳转链接
            3. 返回响应

404 路由不匹配
405 方法不被允许（你没有实现请求对应的方法）
"""
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall_1024 import settings

class QQLoginURLView(View):
    """生成QQ用户绑定链接"""
    def get(self,request):
        # 1. 生成 QQLoginTool 实例对象  初始化OAuthQQ对象
        # client_id=None, client_secret=None, redirect_uri=None, state=None
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URL,
            state='xxx',
        )
        # 2. 调用对象的方法生成跳转链接
        # 获取QQ登录扫码页面，扫码后得到Authorization Code
        qq_login_url = oauth.get_qq_url()

        # 3. 返回响应
        return JsonResponse({'code':0,'errmsg':'绑定成功！','login_url':qq_login_url})

"""
需求： 获取code，通过code换取token，再通过token换取openid

前端：
        应该获取 用户同意登录的code。把这个code发送给后端
后端：
    请求          获取code
    业务逻辑       通过code换取token，再通过token换取openid
                根据openid进行判断
                如果没有绑定过，则需
                要绑定
                如果绑定过，则直接登录
    响应          
    路由          GET         oauth_callback/?code=xxxxx
        axios.get(this.host + '/oauth_callback/?code=' + code, {
         axios.post(this.host + '/oauth_callback/', {
    步骤
        1. 获取code
        2. 通过code换取token
        3. 再通过token换取openid
        4. 根据openid进行判断
        5. 如果没有绑定过，则需要绑定
        6. 如果绑定过，则直接登录
"""
from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from django_redis import get_redis_connection


class OAuthQQView(View):

    def get(self,request):
        # 1.获取code
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'code':400,'errmsg':'参数不全！'})
        # 2. 通过code换取token
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URL,
            state='xxx',
        )
        token = oauth.get_access_token(code)
        # 'B04B30410AA13C4AE62C86D108D36907'

        # 3. 再通过token换取openid  openid相当于qq的唯一id 不会变
        openid = oauth.get_open_id(token)
        # 'CB9A2818793FEC30115A20AAA0BEE03C'

        # 4. 根据openid进行判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 不存在
            # 5. 如果没有绑定过，则需要绑定
            response = JsonResponse({'code':400,'access_token':openid})
            return response
        else:
            # 存在
            # 6. 如果绑定过，则直接登录,即状态保持
            # 设置session
            login(request,qquser.user)
            # 设置 cookie
            response =  JsonResponse({'code':0,'errmsg':'OK！'})
            response.set_cookie('username',qquser.user.username)
            return response

    """
    需求： 绑定账号信息

        QQ(openid) 和 美多的账号信息

    前端：
            当用户输入 手机号，密码，短信验证码之后就发送axios请求。请求需要携带 mobile,password,sms_code,access_token(openid)
    后端：

        请求：         接收请求，获取请求参数
        业务逻辑：       绑定，完成状态保持
        响应：         返回code=0 跳转到首页
        路由：          POST   oauth_callback/
        步骤：
                1. 接收请求
                2. 获取请求参数  openid
                try:
                    3. 根据手机号进行用户信息的查询
                except User.DoesNotExit:
                    4. 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定
                else:
                    5. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
                6. 完成状态保持
                session+cookie
                7. 返回响应

    """

    def post(self,request):
        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取请求参数  openid
        password = data.get('password')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        openid = data.get('access_token')

        # image_code = request.GET.get('image_code')
        # uuid = request.GET.get('image_code_id')
        # 前端传的json数据，不能用查询string形式接受 以上两个数据

        # 验证数据
        if not all([password,mobile,sms_code,openid]):
            return JsonResponse({'code':0,'errmsg':'参数不足！'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 0, 'errmsg': '请输入正确的手机号码！'})
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 0, 'errmsg': '请输入8-20位的密码！'})

        # 判断短信+图片验证码是否一致 程序会跑到verifications/views验证
        # x.1连接redis
        redis_cli = get_redis_connection('captcha_code')
        # x.2获取数据
        # redis_image_code = redis_cli.get(uuid)
        # if redis_image_code is None:
        #     return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})
        # # x.3对比数据
        # if redis_image_code.decode().lower() != image_code.lower():
        #     return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})

        # 验证短信验证码
        sms_code_redis = redis_cli.get(mobile)
        if not sms_code_redis:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码已过期！'})
        if sms_code_redis.decode() != sms_code:  # redis保存的是字节串 b'050473'
            return JsonResponse({'code': 400, 'errmsg': '短信验证码输入有误！'})

        try:
        #     3. 根据手机号进行用户信息的查询
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
        #     4. 查询到用户手机号没有注册。我们就创建一个user信息。然后再绑定 //一个用户可能有多个手机号
            user = User.objects.create_user(username=mobile,mobile=mobile,password=password)
        else:
        #     5. 查询到用户手机号已经注册了。判断密码是否正确。密码正确就可以直接保存（绑定） 用户和openid信息
            if not user.check_password(password):
                return JsonResponse({'code':400,'errmsg':'账号或密码错误'})
        OAuthQQUser.objects.create(user=user,openid=openid)

        # 6. 完成状态保持
        # session+cookie
        login(request,user)
        response = JsonResponse({'code':0,'errmsg':'ok'})
        response.set_cookie('username',user.username)
        # 7. 返回响应
        return response
