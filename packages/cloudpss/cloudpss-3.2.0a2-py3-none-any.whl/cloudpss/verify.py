import jwt
import os
import time

public_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDPN91AYRu5++yPvL1H1auWZFTh
L+rH9Aa3rDvChZKtPfVetvBsqf0DF0uraGGnyOzaXHvIVYYNWQYgI6YO8e8U3pOP
+qcUb+U22blkhXNo8x48uQkGrLMWO4Ppi5SMMiCsNXPSfpANpZ9E7301WSJdRQLj
XU0E2qmggJ2AwjRGNwIDAQAB
-----END PUBLIC KEY-----'''


def setToken(token):
    """
        设置 用户申请的 sdk token 

        :params: token token 

        >>> cloudpss.setToken(token)
    """
    result = verifyToken(token)
    os.environ['CLOUDPSS_TOKEN'] = token
    os.environ['USER_NAME'] = result['username']


def verifyToken(token):
    result = jwt.decode(token, public_key, algorithms='RS256')
    if result['exp'] - int(time.time()) < 0:
        raise Exception('token 已过期，请重新申请')
    return result
