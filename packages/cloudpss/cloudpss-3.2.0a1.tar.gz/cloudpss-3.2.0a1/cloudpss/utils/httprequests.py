# coding=UTF-8

import json
import requests
import os
from collections import OrderedDict


def request(method, uri, baseUrl=None, params={}, token=None, **kwargs):
    if baseUrl == None:
        baseUrl = os.environ.get('CLOUDPSS_API_URL', 'https://cloudpss.net/')
    url = requests.compat.urljoin(baseUrl, uri)
    token = os.environ.get('CLOUDPSS_TOKEN', None)
    if token:
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json; charset=utf-8'
        }
    else:
        raise Exception('token undefined')
    r = requests.request(method, url, params=params, headers=headers, **kwargs)

    if (uri.startswith('/graphql')):
        if 'X-Cloudpss-Version' not in r.headers:
            raise Exception(
                '当前SDK版本（ver 3.X.X）与服务器版本（3.0.0 以下）不兼容，请更换服务器地址或更换SDK版本。')
        if r.headers['X-Cloudpss-Version'] != '3':
            raise Exception('当前SDK版本（ver 3.X.X）与服务器版本（ver ' +
                            r.headers['X-Cloudpss-Version'] +
                            '.X.X）不兼容，请更换服务器地址或更换SDK版本。')

    try:
        r.raise_for_status()
    except Exception as e:
        raise Exception(r.text)
    return r
