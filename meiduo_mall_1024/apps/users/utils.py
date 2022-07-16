from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall_1024.settings import SECRET_KEY

def generic_email_verify_token(user_id):
    """加密"""
    s = Serializer(secret_key=SECRET_KEY,expires_in=3600)
    encode_data = s.dumps({'user_id':user_id})
    # access_token为二进制类型的数据 最好将byte类型的数据转换为str 该数据仍然是加密状态
    return encode_data.decode()

def check_access_token(token):
    """解密"""
    s = Serializer(secret_key=SECRET_KEY, expires_in=3600)
    try:
        s_decode = s.loads(token)
    except Exception:
        return None

    # result = {'user_id':user_id}
    return s_decode.get('user_id')
