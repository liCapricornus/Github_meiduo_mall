from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area

"""
需求：
    获取省份信息
前端：
    当页面加载的时候，会发送axios请求，来获取 省份信息
后端：
    请求：         不需要请求参数
    业务逻辑：       查询省份信息
    响应：         JSON

    路由：         areas/
        axios.get(this.host + '/areas/', {
    步骤：
        1.查询省份信息
        2.将对象转换为字典数据
        3.返回响应
"""

# 不经常发生变化的数据 我们最好缓存到redis（内容）中 减少数据库的查询
from django.core.cache import cache
class AreaView(View):
    """获取省份信息"""
    def get(self,request):
        # 查询缓存数据
        province_list = cache.get('province')
        if not province_list:
            # 1.查询省份信息
            provinces = Area.objects.filter(parent_id=None)
            # 查询结果集

            # 2.将对象转换为字典数据
            province_list = []
            for province in provinces:
                province_list.append({
                    'id':province.id,
                    'name':province.name
                })

            # 保存缓存数据
            cache.set('province',province_list,3600*24)

        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','province_list':province_list})

"""
需求：
    获取市、区县信息
前端：
    当页面修改省、市的时候，会发送axios请求，来获取 下一级的信息
后端：
    请求：         要传递省份id、市的id
    业务逻辑：       根据id查询信息，将查询结果集转换为字典列表
    响应：         JSON

    路由：         areas/id/
         axios.get(this.host + '/areas/' + this.form_address.city_id + '/', {
    步骤：
        1.获取省份id、市的id,查询信息
        2.将对象转换为字典数据
        3.返回响应
"""

class SubAreaView(View):
    """获取市区县信息"""
    def get(self,request,city_id):
        # redis查询是否有缓存数据
        district_list = cache.get('district_%s'%city_id)
        if not district_list:
            # 1.获取省份id、市的id,查询信息
            city = Area.objects.get(id=city_id)
            districts = city.subs.all()

            # 2.将对象转换为字典数据
            district_list = []
            for item in districts:
                district_list.append({
                    'id':item.id,
                    'name':item.name,
                })
            # redis保存缓存数据
            cache.set('district_%s'%city_id,district_list,3600*24)  # 24h

        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','sub_data':{'subs':district_list}})

# 举例： 美多商城
# 注册用户 1个亿
# 日活用户 1%     1百万
# 下单比例 1%       1w  10000
#  新增地址的概率 1%   100    300次   2次

# 不经常发生变化的数据 我们最好缓存到 redis（内容）中 减少数据库的查询

# 5分钟

