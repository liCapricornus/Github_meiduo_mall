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
    """个人中心显示功能实现"""
    def get(self,request):
        # request.user 就是 已经登录的用户信息  此处就是lishao用户的信息
        # request.user 是来源于 中间件
        # 系统会进行判断 如果我们确实是登录用户，则可以获取到 登录用户对应的 模型实例数据
        # 如果我们确实不是登录用户，则request.user = AnonymousUser()  匿名用户
        info_data ={
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'hello world','info_data':info_data})


"""
需求：     1.保存邮箱地址  2.发送一封激活邮件  3. 用户激活邮件

前端：
    当用户输入邮箱之后，点击保存。这个时候会发送axios请求。

后端：
    请求           接收请求，获取数据
    业务逻辑        保存邮箱地址  发送一封激活邮件
    响应           JSON  code=0

    路由          PUT //更新数据
    var url = this.host + '/emails/'
            axios.put(url,
    步骤
        1. 接收请求
        2. 获取数据
        3. 保存邮箱地址
        4. 发送一封激活邮件
        5. 返回响应


需求（要实现什么功能） --> 思路（ 请求。业务逻辑。响应） --> 步骤  --> 代码实现
"""

class EmailView(LoginRequiredJSONMixin,View):
    """添加验证邮箱"""
    def put(self,request):
        # 1. 接收请求
        data = json.loads(request.body.decode())

        # 2. 获取数据
        get_email = data.get('email')
        # 验证数据
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',get_email):
            return JsonResponse({'code':400,'errmsg':'邮箱格式错误！'})

        # 3. 保存邮箱地址
        user = request.user  # user即为登录用户
        user.email = get_email
        user.save()

        # 4. 发送一封激活邮件
        # from django.core.mail import send_mail
        # def send_mail(subject, message, from_email, recipient_list,
        subject = '---美多商城激活邮件---'  # 收件箱主题显示
        from_email = '美多商城<lishao_1024@163.com>'  # 发件人显示 ---美多商城---
        recipient_list = ['705567814@qq.com','285051863@qq.com']

        # 4.1 对a标签的连接数据进行加密处理
        from apps.users.utils import generic_email_verify_token
        token = generic_email_verify_token(request.user.id)  # 封装加密 绑定用户id

        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s" % token
        # 4.2 组织我们的激活邮件
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (get_email, verify_url, verify_url)

        # send_mail(
        #     subject=subject,
        #     message='',
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message,
        # )

        # 激活邮件实现celery异步发送
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(
            subject=subject,
            message='',
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
        )

        # 5. 返回响应
        return JsonResponse({'code':0,'errmsg':'OK!'})


"""

需求（知道我们要干什么？？？）：
    激活用户的邮件
前端(用户干了什么，传递了什么参数)：
        用户会点击那个激活连接。那个激活连接携带了token
后端：
    请求：         接收请求，获取参数，验证参数
    业务逻辑：       user_id, 根据用户id查询数据，修改数据
    响应：         返回响应JSON

    路由：         PUT     emails/verification/  说明： token并没有在body里
         axios.put(this.host+'/emails/verification/'+ window.location.search,
    步骤：

        1. 接收请求
        2. 获取参数
        3. 验证参数
        4. 获取user_id
        5. 根据用户id查询数据
        6. 修改数据
        7. 返回响应JSON

"""

class EmailVerifyView(View):
    """激活用户邮件"""
    def put(self,request):
        # 1. 接收请求  request.GET
        # 2. 获取参数  request.GET.get('token')
        token = request.GET.get('token')
        # 3. 验证参数
        if not token:
            return JsonResponse({'code':400,'errmsg':'参数缺失！'})
        # 4. 获取user_id  封装解密
        from apps.users.utils import check_access_token
        user_id = check_access_token(token)
        if not user_id:
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        # 5. 根据用户id查询数据
        user = User.objects.get(id=user_id)

        # 6. 修改数据
        user.email_active = True
        user.save()

        # 7. 返回响应JSON
        return JsonResponse({'code':0,'errmsg':'激活成功！'})


"""
需求：
    新增地址

前端：
    当用户填写完成地址信息后，前端应该发送一个axios请求，会携带 相关信息 （POST--body）
        var url = this.host + '/addresses/create/'
                    axios.post(url, this.form_address, {
后端：

    请求：         接收请求，获取参数,验证参数
    业务逻辑：      数据入库
    响应：         返回响应

    路由：     POST        /addresses/create/
    步骤： 
        1.接收请求
        2.获取参数，验证参数
        3.数据入库
        4.返回响应
"""
from apps.areas.models import Area
from apps.users.models import Address

class AddressCreateView(LoginRequiredJSONMixin, View):
    """新增地址功能实现"""
    def post(self,request):
        # 1.接收请求
        data = json.loads(request.body.decode())
        # {'receiver': '李绍', 'province_id': 340000, 'city_id': 340600,
        # 'district_id': 340621, 'place': '濉溪县第三人民医院',
        # 'mobile': '13203991352', 'tel': '0561-7035246',
        # 'email': '285051863@qq.com', 'title': '李绍'}

        # 2.获取参数，验证参数
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        title = data.get('title')

        user = request.user
        # 验证参数
        if not all([receiver,province_id,city_id,district_id,place,mobile]):
            return JsonResponse({'code':400,'errmsg':'参数不全！'})
        # 省市区的id是否正确（如果能在区表中查到市，根据市查到区/县说明id正确）
        province = Area.objects.get(id=province_id)
        city = Area.objects.get(id=city_id)
        district = Area.objects.get(id=district_id)
        if not all([province, city, district]):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的地区信息!'})
        # 详细地址的长度 max_length = 50
        if len(place) > 50:
            return JsonResponse({'code': 400, 'errmsg': '地址过长!'})
        # 验证手机号
        if not re.match(r'^1[345789]\d{9}$',mobile):
            return JsonResponse({'code': 400, 'errmsg': '手机号不正确，请重新输入!'})
        # 固定电话
        if len(tel) > 0:
            if not re.match(r'/^(\d{4}-)?\d{6,8}$', tel):
                return JsonResponse({'code': 400, 'errmsg': '电话格式不正确!'})
        # 邮箱
        if len(email) > 0:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
                return JsonResponse({'code': 400, 'errmsg': '邮箱格式不正确!'})

        # 3.数据入库
        address = Address.objects.create(
            user = user,
            receiver = receiver,
            province_id = province_id,
            city_id = city_id,
            district_id = district_id,
            place = place,
            mobile = mobile,
            tel = tel,
            email = email,
            title = title,
        )

        # 转为字典数据
        address_dict = {
            'id':address.id,
            'receiver':address.receiver,
            'province':address.province.name,
            'city':address.city.name,
            'district':address.district.name,
            'place':address.place,
            'mobile':address.mobile,
            'tel':address.tel,
            'email':address.email,
            'title':address.title,
        }

        # 4.返回响应
        return JsonResponse({'code':0,'errmsg':'收货地址保存成功！','address':address_dict})

"""
展示收货地址

    前端：axios.get(this.host + '/addresses/', {
        this.addresses = response.data.addresses;
        
    后端：
        1.接受请求
        2.处理业务逻辑
        3.返回响应  
"""

class AddressView(LoginRequiredJSONMixin,View):
    """展示收货地址界面"""
    def get(self,request):
        # 1.接受请求，获取数据
        user = request.user
        # addresses = user.addresses
        addresses = Address.objects.filter(user=user,is_deleted=False)

        # 2.将对象数据转换为字典数据
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email,
                'title': address.title,
            })

        # 3.返回响应   前端接收的 response.data.addresses 如果写错，则不会返回前端界面
        return JsonResponse({'code':0,'errmsg':'收货地址显示成功！','addresses':address_list})










