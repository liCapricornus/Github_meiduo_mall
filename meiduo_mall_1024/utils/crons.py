"""
页面静态化+定时任务 功能实现
"""

import time

from apps.contents.models import ContentCategory
from utils.goods import get_categories


def generic_meiduo_index():
    print("-------------%s--------------"%time.ctime())
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
    # return render(request,'index.html', context)  渲染

    # 1.加载渲染模板
    from django.template import loader
    index_template = loader.get_template('index.html')

    # 2.把数据给模板
    index_html_data = index_template.render(context)

    # 3.把渲染好的index.html给指定文件
    from meiduo_mall_1024 import settings
    import os
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR),'front_end_pc/index.html')
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html_data)