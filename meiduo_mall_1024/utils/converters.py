# from django.urls import converters

class UsernameConverter:
    """创建自定义转换器 UsernameConverter"""
    # regex = '^[a-zA-Z0-9_-]{5,20}$'  //此句会导致RE句法失败
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        return value
        # return int(value)   //此句会导致用户名只能int型，虽然符合RE，比如itheima 依然404

# 判断手机号是否注册的转换器
class MobileConverter:
    regex = '1[345789]\d{9}'

    def to_python(self, value):
        return value