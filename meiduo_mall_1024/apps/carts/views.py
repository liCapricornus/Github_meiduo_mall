"""
1.  京东的网址 登录用户可以实现购物车，未登录用户可以实现购物车      v
    淘宝的网址 必须是登录用户才可以实现购物车

2.  登录用户数据保存在哪里？    服务器里        mysql/redis
                                        mysql
                                        redis           学习， 购物车频繁增删改查
                                        mysql+redis
    未登录用户数据保存在哪里？   客户端
                                        cookie      

3.  保存哪些数据？？？

    redis:
            user_id,sku_id(商品id),count(数量),selected（选中状态）

    cookie:
            sku_id,count,selected,

4.  数据的组织

    redis:
            user_id,    sku_id(商品id),count(数量),selected（选中状态）

            hash
            user_id:
                    sku_id:count
                    xxx_sku_id:selected

            1：  
                    1:10
                    xx_1: True

                    2:20
                    xx_2: False

                    3:30
                    xx_3: True
            13个地方的空间

            进一步优化！！！
            为什么要优化呢？？？
            redis的数据保存在 内存中  我们应该尽量少的占用redis的空间

            user_id:
                    sku_id:count


            selected 



            user_1:         sku_id:数量
                            1: 10 
                            2: 20
                            3: 30
            记录选中的商品
            1,3



            user_1
                    1: 10 
                    2: 20
                    3: 30
            selected_1: {1,3}

            10个空间


             user_1
                    1: 10 
                    2: -20
                    3: 30

            7个空间

    cookie:
        {
            sku_id: {count:xxx,selected:xxxx},
            sku_id: {count:xxx,selected:xxxx},
            sku_id: {count:xxx,selected:xxxx},
        }


5.
    cookie字典转换为字符串保存起来，数据没有加密


    base64：         6个比特位为一个单元

    1G=1024MB
    1MB=1024KB
    1KB=1024B

    1B=8bytes

    bytes 0 或者 1

    ASCII

    a 
    0110 0001

    a               a       a                   24比特位
    0110 0001  0110 0001   0110 0001 

    011000      010110      000101          100001 
    X               Y       Z                  N

    aaa --> XYZN

    base64模块使用：
        base64.b64encode()将bytes类型数据进行base64编码，返回编码后的bytes类型数据。
        base64.b64deocde()将base64编码后的bytes类型数据进行解码，返回解码后的bytes类型数据。



    字典 ----》 pickle ------二进制------》Base64编码

    pickle模块使用：
        pickle.dumps()将Python数据序列化为bytes类型数据。
        pickle.loads()将bytes类型数据反序列化为python数据。

#######################编码数据####################################
# 字典
carts = {
    '1': {'count':10,'selected':True},
    '2': {'count':20,'selected':False},
}


# 字典转换为 bytes类型
import pickle
b=pickle.dumps(carts)

# 对bytes类型的数据进行base64编码
import base64
encode=base64.b64encode(b)
#######################解码数据####################################

# 将base64编码的数据解码
decode_bytes=base64.b64decode(encode)

# 再对解码的数据转换为字典
pickle.loads(decode_bytes)

6.
请求
业务逻辑（数据的增删改查）
响应


增 （注册）
    1.接收数据
    2.验证数据
    3.数据入库
    4.返回响应

删 
    1.查询到指定记录
    2.删除数据（物理删除，逻辑删除）
    3.返回响应

改  （个人的邮箱）
    1.查询指定的记录
    2.接收数据
    3.验证数据
    4.数据更新
    5.返回响应

查   （个人中心的数据展示，省市区）
    1.查询指定数据
    2.将对象数据转换为字典数据
    3.返回响应

"""
import json

from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU

"""
需求：添加商品到购物车
前端：
    我们点击添加购物车之后， 前端将 商品id ，数量 发送给后端

后端：
    请求：         接收参数，验证参数
    业务逻辑：       根据商品id查询数据库看看商品id对不对
                  数据入库
                    登录用户入redis
                        连接redis
                        获取用户id
                        hash
                        set
                        返回响应
                    未登录用户入cookie
                        先有cookie字典
                        字典转换为bytes
                        bytes类型数据base64编码
                        设置cookie
                        返回响应
    响应：         返回JSON
    路由：     POST  /carts/
                 var url = this.host + '/carts/'
            axios.post(url, {
    步骤：
            1.接收数据
            2.验证数据
            3.判断用户的登录状态
            4.登录用户保存redis
                4.1 连接redis
                4.2 操作hash
                4.3 操作set
                4.4 返回响应
            5.未登录用户保存cookie
                5.1 先有cookie字典
                5.2 字典转换为bytes
                5.3 bytes类型数据base64编码
                5.4 设置cookie
                5.5 返回响应
"""
import pickle
import base64


class CartsView(View):
    """新增购物车"""
    def post(self,request):
        # 1.接受请求，获取数据
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')   # no字节串/str 为int型
        # 2.验证数据
        if not all([sku_id,count]):
            return JsonResponse({'code':400,'errmsg':'参数不全！'})
        sku = SKU.objects.get(id=sku_id)
        if not sku:  # 同try: except SKU.DoseNotExit:
            return JsonResponse({'code':400,'errmsg':'没有此商品！'})
        if count is None:
            return JsonResponse({'code':400,'errmsg':'商品添加失败！'})

        # 强制类型转换
        # try:
        #     count = int(count)
        # except Exception:
        #     count = 1

        # 3.判断用户登陆状态
        user = request.user
        if user.is_authenticated:
            # 3.1 登陆用户
            # 3.1.1 链接redis
            # redis_cli = get_redis_connection('carts')
            # 3.1.2 操作hash

            # 3.1.3 操作set
            # 3.1.4 返回响应
            return JsonResponse({})

        # 3.2 未登录用户
        else:
            # carts = {
            #     sku_id:{'count':count,'selected':True},
            # }
            # 3.2.1 读取cookie数据 加密的str
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                base64decode = base64.b64decode(cookie_carts)
                carts = pickle.loads(base64decode)
            else:
                carts = {}

            # 判断新增的商品是否在购物车里
            if sku_id in carts:
                # 在 count ++
                # 不在 carts[sku_id]={}
                origin_count = carts[sku_id]['count']
                count += origin_count
                carts[sku_id] = {
                    'count':count,
                    'selected': True,
                }
            else:
                carts[sku_id] = {
                    'count': count,
                    'selected': True,
                }
            # 3.2.2 pickle.dumps() ---> 字节流
            carts_bytes = pickle.dumps(carts)
            # 3.2.3 base64.b64encode() ---> 加密字节串
            base64encode = base64.b64encode(carts_bytes)
            response = JsonResponse({'code':0,'errmsg':'OK'})
            carts_str = base64encode.decode()
            response.set_cookie('carts',carts_str,max_age=3600)
            # 3.2.4 返回响应
            return response













