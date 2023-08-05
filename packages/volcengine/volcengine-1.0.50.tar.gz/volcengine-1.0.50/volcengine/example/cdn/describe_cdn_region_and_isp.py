#  -*- coding: utf-8 -*-
import datetime

from volcengine.example.cdn import ak, sk
from volcengine.cdn.service import CDNService

if __name__ == '__main__':
    svc = CDNService()
    svc.set_ak(ak)
    svc.set_sk(sk)
    body = {
        'Area': 'China'
    }
    print(body)

    resp = svc.describe_cdn_region_and_isp(body)
    print(resp)
