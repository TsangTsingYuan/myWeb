#-*- coding: UTF-8 -*-
import sys
#sys.path.append('../SDK')
import optparse
import time
from . import apiutil_py3
import json

app_key = 'UzHvJu0XoZymLbJZ'
app_id = '1107055682'

if __name__ == '__main__':
    str_text = '你叫啥'

    ai_obj = apiutil_py3.AiPlat(app_id, app_key)

    print('----------------------SEND REQ----------------------')
    rsp = ai_obj.getNlpTextChat(str_text)
    if rsp['ret'] == 0:
        print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
        print('----------------------API SUCC----------------------')
    else:
        print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
        # print rsp
        print('----------------------API FAIL----------------------')

