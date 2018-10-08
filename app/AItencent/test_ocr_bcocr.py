#-*- coding: UTF-8 -*-
import sys
sys.path.append('../SDK')
import optparse
import time
from . import apiutil_py3
import base64
import json

app_key = 'UzHvJu0XoZymLbJZ'
app_id = '1107055682'

if __name__ == '__main__':

    with open('../data/mingpian.jpg', 'rb') as bin_data:
        image_data = bin_data.read() #读取文件内容，需转换为base64编码


    ai_obj = apiutil_py3.AiPlat(app_id, app_key)

    print('----------------------SEND REQ----------------------')
    rsp = ai_obj.getOcrBcocr(image_data)

    if rsp['ret'] == 0:
        for i in rsp['data']['item_list']:
            print(i['item'], i['itemstring'])
        print('----------------------API SUCC----------------------')
    else:
        print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
        print('----------------------API FAIL----------------------')
