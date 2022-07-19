from django.db import models

# Create your models here.
from utils.models import BaseModel

class GoodsCategory(BaseModel):
    """商品类别"""
    name = models.CharField(max_length=10,verbose_name='名称')
    parent = models.ForeignKey('self',related_name='subs',null=True,blank=True,
                               on_delete=models.CASCADE,verbose_name='父类别')

    class Meta:
        db_table = 'md_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    name = models.CharField(max_length=20,verbose_name='频道组名')

    class Meta:
        db_table = 'md_channel_group'
        verbose_name = '商品频道组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class GoodsChannel(BaseModel):
    """商品频道"""
    channel_group = models.ForeignKey('GoodsChannelGroup',on_delete=models.CASCADE,
                                      verbose_name='频道组名')
    goods_category = models.ForeignKey('GoodsCategory',on_delete=models.CASCADE,
                                       verbose_name='商品类别')
    url = models.CharField(max_length=50,verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name='组内排序')

    class Meta:
        db_table = 'md_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods_category.name

class Brand(BaseModel):
    """品牌"""
    name = models.CharField(max_length=20,verbose_name='名称')
    logo = models.ImageField(verbose_name='Logo图片')
    first_letter = models.CharField(max_length=1,verbose_name='品牌首字母')

    class Meta:
        db_table = 'md_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class SPU(BaseModel):   # 标准产品单位
    """商品SPU -> Standard Product Unit"""
    name = models.CharField(max_length=50,verbose_name='名称')
    brand = models.ForeignKey('Brand',on_delete=models.PROTECT,verbose_name='品牌')
    goods_category1 = models.ForeignKey('GoodsCategory',on_delete=models.PROTECT,
                                        related_name='category1_spu',verbose_name='一级类别')
    goods_category2 = models.ForeignKey('GoodsCategory',on_delete=models.PROTECT,
                                        related_name='category2_spu',verbose_name='二级类别')
    goods_category3 = models.ForeignKey('GoodsCategory',on_delete=models.PROTECT,
                                        related_name='category3_spu',verbose_name='三级类别')
    sales = models.IntegerField(default=0,verbose_name='销量')
    comments = models.IntegerField(default=0,verbose_name='评价数')
    desc_detail = models.TextField(default='',verbose_name='详细介绍')
    desc_pack = models.TextField(default='',verbose_name='包装信息')
    desc_service = models.TextField(default='',verbose_name='售后服务')

    class Meta:
        db_table = 'md_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class SKU(BaseModel):   # 库存量单位
    """商品SKU -> Stock Keeping Unit"""
    name = models.CharField(max_length=50,verbose_name='名称')
    caption = models.CharField(max_length=100,verbose_name='副标题')
    spu = models.ForeignKey('SPU',on_delete=models.CASCADE)
    goods_category = models.ForeignKey('GoodsCategory',on_delete=models.PROTECT,
                                       verbose_name='从属类别')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='单价')
    cost_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='进价')
    market_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='市场价')
    stock = models.IntegerField(default=0,verbose_name='库存')
    sales = models.IntegerField(default=0,verbose_name='销量')
    comments = models.IntegerField(default=0,verbose_name='评价数')
    is_launched = models.BooleanField(default=True,verbose_name='是否上架销售')
    default_image = models.ImageField(max_length=200,default='',null=True,blank=True,
                                      verbose_name='默认图片')

    class Meta:
        db_table = 'md_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s'%(self.id,self.name)

class SKUImage(BaseModel):
    """SKU图片"""
    sku = models.ForeignKey('SKU',on_delete=models.CASCADE,verbose_name='sku')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'md_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s_%s'%(self.sku.name,self.id)

class SPUSpecification(BaseModel):
    """商品SPU规格"""
    name = models.CharField(max_length=20,verbose_name='规格名称')
    spu = models.ForeignKey('SPU',on_delete=models.CASCADE,related_name='specs',
                            verbose_name='商品SPU')

    class Meta:
        db_table = 'md_spu_specification'
        verbose_name = '商品SPU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s'%(self.spu.name,self.name)

class SpecificationOption(BaseModel):
    """规格选项"""
    spu_spec = models.ForeignKey('SPUSpecification',on_delete=models.CASCADE,related_name='options',
                                 verbose_name='spu规格')
    value = models.CharField(max_length=20,verbose_name='选项值')

    class Meta:
        db_table = 'md_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s'%(self.spu_spec,self.value)

class SKUSpecification(BaseModel):
    """SKU具体规格"""
    sku = models.ForeignKey('SKU',on_delete=models.CASCADE,related_name='spec',
                            verbose_name='sku')
    spu_spec = models.ForeignKey('SPUSpecification',on_delete=models.PROTECT,verbose_name='spu规格')
    option = models.ForeignKey('SpecificationOption',on_delete=models.PROTECT,verbose_name='规格值')

    class Meta:
        db_table = 'md_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s'%(self.sku,self.spu_spec.name,self.option.value)
