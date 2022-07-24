import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View


# Create your views here.

############上传图片的代码################################
# from fdfs_client.client import Fdfs_client
#
# # 1. 创建客户端
# # 修改加载配置文件的路径
# # conf_path='/etc/fdfs/client.conf'
# client=Fdfs_client('utils/fastdfs/client.conf')
#
# # 2. 上传图片
# # 图片的绝对路径
# client.upload_by_filename('/home/lishao/io/hello/girl.png')
# client.append_by_filename('/home/lishao/图片/CMU.png')
# 3. 获取file_id .upload_by_filename 上传成功会返回字典数据
# 字典数据中 有file_id

"""
首页的数据分为2部分
    1部分是 商品分类数据
    2部分是 广告数据
"""
from utils.goods import get_categories
from apps.contents.models import ContentCategory

class IndexView(View):
    """首页"""
    def get(self,request):
        # 1.商品分类数据
        categories = get_categories()

        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories':categories,
            'contents':contents,
        }
        return render(request,'index.html', context)

"""
需求：
        根据点击的分类，来获取分类数据（有排序，有分页）
前端：
        前端会发送一个axios请求， 分类id 在路由中， 
        分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求          接收参数
    业务逻辑       根据需求查询数据，将对象数据转换为字典数据
    响应          JSON

    路由      GET     /list/category_id/skus/
             var url = this.host+'/list/'+this.cat+'/skus/'
            axios.get(url, {
    步骤
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from apps.goods.models import GoodsCategory, SKU
from utils.goods import get_breadcrumb

class ListView(View):
    """获取分类数据"""
    def get(self,request,category_id):
        # 1.接收请求，获取参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')

        # 验证参数
        if not all([page,page_size,ordering]):
            return JsonResponse({'code':400,'errmsg':'参数缺失！'})

        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失！'})

        # 4.获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 5.查询分类对应的sku数据，然后排序，然后分页  懒加载
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)

        from django.core.paginator import Paginator
        # object_list, per_page
        # object_list   列表数据
        # per_page      每页多少条数据
        paginator = Paginator(skus,per_page=page_size)
        # 获取指定页码的数据
        page_skus = paginator.page(page)

        # 将对象数据转换为字典数据
        sku_list = []
        for sku in page_skus.object_list:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        # 获取总页码
        total_num = paginator.num_pages

        # 6.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','count':total_num,'list':sku_list,'breadcrumb':breadcrumb})

"""
热销数据实现
    前端：var url = this.host+'/hot/'+this.cat + '/'
            axios.get(url, {
        this.hot_skus = response.data.hot_skus
    后端：
        1.接收请求，获取数据
        2.处理业务逻辑
        3.返回响应
"""

class HotSellView(View):
    """热销显示"""
    def get(self,request,category_id):
        # 1.接收请求，获取数据
        # 查询分类对应的sku数据，然后排序，然后分页  懒加载
        # skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        skus = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]

        # 2.处理业务逻辑
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'sales':sku.sales,
                'default_image_url': sku.default_image.url,
            })

        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'OK!','hot_skus':hot_skus})


"""
------------------------搜索---------------------------- 

1. 我们不使用like

2. 我们使用 全文检索
    全文检索即在指定的任意字段中进行检索查询

3. 全文检索方案需要配合搜索引擎来实现

4. 搜索引擎

    原理：  关键词与词条的对应关系，并记录词条的位置


        1  --- 我爱北京天安门                      我爱， 北京，天安门

        2 --- 王红，我爱你，我想你想的睡不着觉        王红，我爱，我爱你，睡不着觉，想你，

        3 ---  我睡不着觉                          我，睡不着觉 


        我爱


5. Elasticsearch
    进行分词操作 
    分词是指将一句话拆解成多个单字或词，这些字或词便是这句话的关键词

    下雨天 留客天 天留我不 留


6. 
    数据         <----------Haystack--------->             elasticsearch 

                        ORM(面向对象操作模型)                 mysql,oracle,sqlite,sql server
"""

"""
 我们/数据         <----------Haystack--------->             elasticsearch 

 我们是借助于 haystack 来对接 elasticsearch
 所以 haystack 可以帮助我们 查询数据
"""
from haystack.views import SearchView

class SKUSearchView(SearchView):
    """搜索逻辑"""
    def create_response(self):
        """Generates the actual HttpResponse to send back to the user."""
        # 继承重写
        context = self.get_context()
        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price':sku.object.price,
                'default_image_url':sku.object.default_image.url,
                'searchkey':context.get('query'),
                'page_size':context['page'].paginator.num_pages,
                'count':context['page'].paginator.count,
            })

        return JsonResponse(sku_list,safe=False)


"""
需求：
    详情页面

    1.分类数据
    2.面包屑
    3.SKU信息
    4.规格信息


    我们的详情页面也是需要静态化实现的。
    但是我们再讲解静态化之前，应该可以先把 详情页面的数据展示出来

"""
from utils.goods import get_categories,get_breadcrumb,get_goods_specs

class DetailView(View):
    """详情页面显示"""
    def get(self,request,sku_id):
        # 接收请求
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            pass
            # return JsonResponse({'code':400,'errmsg':'参数不全'})
        # 1.分类数据
        categories = get_categories()
        # 2.面包屑
        breadcrumb = get_breadcrumb(sku.category)
        # 3.SKU信息
        # 4.规格信息
        goods_specs = get_goods_specs(sku)

        context = {
            'categories':categories,
            'breadcrumb':breadcrumb,
            'sku':sku,
            'specs':goods_specs,
        }

        # 返回响应
        return render(request,'detail.html',context)

# """
# 页面静态化逻辑教学
# """
#
# import time
# def generic_meiduo_index():
#     print("-------------%s--------------"%time.ctime())
#     # 1.商品分类数据
#     categories = get_categories()
#
#     # 2.广告数据
#     contents = {}
#     content_categories = ContentCategory.objects.all()
#     for cat in content_categories:
#         contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
#
#     context = {
#         'categories':categories,
#         'contents':contents,
#     }
#     # return render(request,'index.html', context)  渲染
#
#     # 1.加载渲染模板
#     from django.template import loader
#     index_template = loader.get_template('index.html')
#
#     # 2.把数据给模板
#     index_html_data = index_template.render(context)
#
#     # 3.把渲染好的index.html给指定文件
#     from meiduo_mall_1024 import settings
#     import os
#     file_path = os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')
#     with open(file_path,'w',encoding='utf-8') as f:
#         f.write(index_html_data)

"""
需求：
    统计每一天的分类商品访问量
前端：
    当访问具体页面的时候，会发送一个axios请求。携带分类id
后端：
    请求：         接收请求，获取参数
    业务逻辑：       查询有没有，有的话更新数据，没有新建数据
    响应：         返回JSON

    路由：     POST    detail/visit/<category_id>/
            var url = this.host + '/detail/visit/' + this.cat + '/';
                axios.post(url, {}, {
    步骤：
        1.接收分类id
        2.验证参数（验证分类id）
        3.查询当天 这个分类的记录有没有
        4. 没有新建数据
        5. 有的话更新数据
        6. 返回响应
"""
from apps.goods.models import GoodsCategory,GoodsVisitCount
from datetime import date

class CategoryVisitCountView(View):
    """统计分类商品访问量"""
    def post(self,request,category_id):
        # 1.接收分类id  //接收请求 获取参数  验证参数
        # 2.验证参数（验证分类id）
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'没有此分类！'})

        # 3.查询当天 这个分类的记录有没有
        today = date.today()
        try:
            good_visit_count = GoodsVisitCount.objects.get(category=category,date=today)
        except GoodsVisitCount.DoesNotExist:
            # 4. 没有新建数据
            GoodsVisitCount.objects.create(
                category=category,
                date=today,
                count=1
            )
        # 5. 有的话更新数据
        else:
            good_visit_count.count += 1
            good_visit_count.save()

        # 6. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})












