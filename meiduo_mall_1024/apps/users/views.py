import json
import re

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
        # 3. 验证数据

        #     3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        if not all([username,password,password2,mobile,allow]):
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






