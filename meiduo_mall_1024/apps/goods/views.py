from django.shortcuts import render

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
from django.views import View
from utils.goods import get_categories
from apps.contents.models import ContentCategory
"""
首页的数据分为2部分
    1部分是 商品分类数据
    2部分是 广告数据
"""

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
