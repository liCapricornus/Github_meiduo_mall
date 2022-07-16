import json
import re

from django.contrib.auth import login, logout
from django.views import View
from django.http import JsonResponse


"""
需求分析： 根据页面的功能（从上到下，从左到右），哪些功能需要和后端配合完成
如何确定 哪些功能需要和后端进行交互呢？？？
        1.经验
        2.关注类似网址的相似功能

"""

"""
判断用户名是否重复的功能。

前端(了解)：     当用户输入用户名之后，失去焦点， 发送一个axios(ajax)请求
            var url = this.host + '/usernames/' + this.username + '/count/';

后端（思路）：
    请求:         接收用户名 
    业务逻辑：     
                    根据用户名查询数据库，如果查询结果数量等于0，说明没有注册
                    如果查询结果数量等于1，说明有注册
    响应          JSON 
                {code:0,count:0/1,errmsg:ok}
    
    路由      GET         usernames/<username>/count/        
   步骤：
        1.  接收用户名
        2.  根据用户名查询数据库
        3.  返回响应         
"""
from apps.users.models import User

class UsernameCountView(View):
    """用户名是否重复逻辑"""
    def get(self,request,username):
        # 1.  接收用户名并re判断 //此部分可以用自定义转换器实现
        # if not re.match('[a-zA-Z0-9_-]{5,20}',username):
        #     return JsonResponse({'code':200,'errmsg':'用户名格式不满足需求'})
        # 2.  根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        if count == 0:
            # 3.  返回响应
            return JsonResponse({'code':200,'errmsg':'用户名未注册！'})
        else:
            return JsonResponse({'code':400,'errmsg':'用户名已注册！'})

class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        if count == 0:
            # 3.  返回响应
            return JsonResponse({'code':200,'errmsg':'手机号未注册！'})
        else:
            return JsonResponse({'code':400,'errmsg':'手机号已注册！'})
"""
我们不相信前端提交的任何数据！！！！

前端：     当用户输入 用户名，密码，确认密码，手机号，是否同意协议之后，会点击注册按钮
            前端会发送axios请求  axios.post(this.host + '/register/',

后端：
    请求：             接收请求（JSON）。获取数据
    业务逻辑：          验证数据。数据入库
    响应：             JSON {'code':0,'errmsg':'ok'}
                     响应码 0 表示成功 400表示失败

    路由：     POST    register/

    步骤：

        1. 接收请求（POST------JSON）
        2. 获取数据
            username: this.username,
            password: this.password,
            password2: this.password2,
            mobile: this.mobile,
            sms_code: this.sms_code, //短信验证码以及图片验证码功能后面实现
            allow: this.allow
        3. 验证数据
            3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
            3.2 用户名满足规则，用户名不能重复
            3.3 密码满足规则
            3.4 确认密码和密码要一致
            3.5 手机号满足规则，手机号也不能重复
            3.6 需要同意协议
        4. 数据入库
        5. 返回响应
"""

class RegisterView(View):
    """用户注册功能实现"""
    def post(self,request):
        # 1. 接收请求（POST------JSON）
        # data = json.loads(request.body.decode())
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)
        # 2. 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')
        sms_code = body_dict.get('sms_code')
        # 3. 验证数据

        #     3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        if not all([username,password,password2,mobile,allow,sms_code]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})

        #     3.2 用户名满足规则
        if not re.match('[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名不满足规则！'})
        #     判断用户名是否存在
        if User.objects.filter(username=username):
            return JsonResponse({'code':400,'errmsg':'用户名已存在！'})

        #     3.3 密码满足规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '密码不满足规则'})

        #     3.4 确认密码和密码要一致
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '密码输入不一致！'})

        #     3.5 手机号满足规则，手机号也不能重复
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号格式错误！'})
        #   判断手机号是否存在
        if User.objects.filter(mobile=mobile):
            return JsonResponse({'code':400,'errmsg':'手机号已注册！'})

        #   判断短信验证码是否正确
        #       1)获取数据
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('captcha_code')
        sms_code_redis = redis_cli.get(mobile)
        #       2对比数据
        if sms_code_redis is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码已过期'})
        # 3.3对比数据
        if sms_code_redis.decode() != sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码输入错误！'})
        #     3.6 需要同意协议
        if allow is False:
            return JsonResponse({'code': 400, 'errmsg': '请勾选用户协议！'})

        # 4. 数据入库  create_user实现加密
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 设置session信息
        # request.session['user_id'] = user.id
        # Django为我们提供了状态保持的方法
        from django.contrib.auth import login
        # user为已经登录的用户信息
        # def login(request, user, backend=None):
        login(request, user)

        # 5. 返回响应
        return JsonResponse({'code': 0, 'errmsg': '注册成功！'})


"""
登录

前端：
    当用户把用户名和密码输入完成之后，会点击登录按钮。这个时候前端应该发送一个axios请求

后端：
    请求    ：  接收数据，验证数据
    业务逻辑：   验证用户名和密码是否正确，session
    响应    ： 返回JSON数据 0 成功。 400 失败

    POST        /login/   axios.post(this.host + '/login/', {
步骤：
    1. 接收数据
    2. 验证数据
    3. 验证用户名和密码是否正确
    4. session
    5. 判断是否记住登录
    6. 返回响应
"""
from apps.users.models import User

class LoginView(View):
    """登录功能实现"""
    def post(self,request):
        # 1. 接收请求，获取数据
        data_dict = json.loads(request.body.decode())
        # 获取数据
        username = data_dict.get('username')
        password = data_dict.get('password')
        remembered = data_dict.get('remembered')
        # 2. 验证数据
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全！'})

        # 用户名/手机号登录
        if re.match(r'^1[345789]\d{9}$',username):  # 此处的132xx作为登录账户使用而非mobile
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 3. 验证用户名和密码是否正确
        # 方式1
        # user = User.objects.get(username=username)
        # 方式2 系统自带的认证系统
        from django.contrib.auth import authenticate
        # 如果用户名和密码正确，则返回 User信息
        # 如果用户名和密码不正确，则返回 None
        user = authenticate(username=username,password=password)

        if not user:  # 等同于 if user is None
            return JsonResponse({'code':400,'errmsg':'账号或密码错误'})
        # 4. session状态保持
        login(request,user)

        # 5. 判断是否记住登录
        if remembered: # 等同于 if remembered is not None
            request.session.set_expiry(None)  # session id 记住2周
        else:
            request.session.set_expiry(0)   # 不记住登录 关闭浏览器session 过期
        # 6. 返回响应
        response =  JsonResponse({'code':0,'errmsg':'登录成功！'})
        response.set_cookie('username',username)
        return response

"""
------------用户登录状态退出-------------

前端：
    当用户点击退出按钮的时候，前端发送一个axios delete请求
     var url = this.host + '/logout/';
            axios.get(url, {

后端：
    请求
    业务逻辑        退出
    响应      返回JSON数据
"""

class LogoutView(View):
    """用户登录状态退出"""
    def get(self,request):
        # 1.删除session信息
        logout(request)
        # 2.删除cookie信息
        response = JsonResponse({'code': 0, 'errmsg': '登录成功！'})
        response.delete_cookie('username')
        return response

"""
------------重写LoginRequiredMixin-----------
LoginRequiredMixin 未登录的用户 会返回 重定向并返回HttpResponse
重定向并不是JSON数据

我们需要是  返回JSON数据
"""
from utils.views import LoginRequiredJSONMixin

class CenterView(LoginRequiredJSONMixin,View):

    def get(self,request):

        info_data ={
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'hello world','info_data':info_data})




