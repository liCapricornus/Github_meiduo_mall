"""
---------详情页面静态化----------
    详情页面 与 首页不同
    详情页面的内容变化比较少。一般也就是修改商品的价格

    1. 详情页面 应该在上线的时候 统一都生成一遍  目前做
    2. 应该是运营人员修改的时候生成 （定时任务） TODO
"""
#!/usr/bin/env python
# 指定是个py脚本

# ../ 当前目录的上一级目录，也就是 base_dir
import sys
sys.path.insert(0, '../')

# 告诉 os 我们的django的配置文件在哪里
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall_1024.settings")

# django setup
# 相当于 当前的文件 有了django的环境
import django
django.setup()

from apps.goods.models import SKU
from utils.goods import get_categories, get_breadcrumb, get_goods_specs


def generic_meiduo_detail(sku):
    # 接收请求
    # try:
    #     sku = SKU.objects.get(id=sku_id)
    # except SKU.DoesNotExist:
    #     pass
        # return JsonResponse({'code':400,'errmsg':'参数不全'})
    # 1.分类数据
    categories = get_categories()
    # 2.面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3.SKU信息
    # 4.规格信息
    goods_specs = get_goods_specs(sku)

    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }

    # 返回响应
    # return render(request, 'detail.html', context)

    # 1.加载渲染模板
    from django.template import loader
    detail_template = loader.get_template('detail.html')

    # 2.把数据给模板
    detail_html_data = detail_template.render(context)

    # 3.把渲染好的index.html给指定文件
    from meiduo_mall_1024 import settings
    import os
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/goods/%s.html'%sku.id)
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(detail_html_data)

    print(sku.id)

skus = SKU.objects.all()
for sku in skus:
    generic_meiduo_detail(sku)