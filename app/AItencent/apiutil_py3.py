#-*- coding: utf-8 -*-
import hashlib
import urllib.request
#import urllib2
import base64
import json
import time
import random

url_preffix='https://api.ai.qq.com/fcgi-bin/'

def setParams(array, key, value):
    array[key] = value

def genSignString(parser):
    uri_str = ''
    #print(sorted(parser.keys()))
    for key in sorted(parser.keys()):
        if key == 'app_key':
            continue
        uri_str += "%s=%s&" % (key, urllib.parse.quote_plus(str(parser[key]), safe = ''))
    sign_str = uri_str + 'app_key=' + parser['app_key']

    hash_md5 = hashlib.md5(sign_str.encode('utf8'))
    #print(hash_md5.hexdigest().upper())
    return hash_md5.hexdigest().upper()
'''
def genSignString(data):
    lst = [i[0]+'='+urllib.parse.quote_plus(str(i[1])) for i in data.items()]
    params = '&'.join(sorted(lst))
    s = params + '&app_key=' + data['app_key']
    h = hashlib.md5(s.encode('utf8'))
    return h.hexdigest().upper()
'''

class AiPlat(object):
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.data = {}

    def invoke(self, params):
        self.url_data = urllib.parse.urlencode(params).encode()          #POST data should be bytes,加encode
        #print(self.url_data)
        req = urllib.request.Request(self.url, self.url_data)   #POST data should be bytes
        #print(req)
        try:
            rsp = urllib.request.urlopen(req)
            #print(rsp)
            #str_rsp是byte类型
            str_rsp = rsp.read()
            #str_rsp = rsp.read().decode('utf8', 'ignore')
            #print('&&&&&',str_rsp)
            dict_rsp = json.loads(str_rsp)
            #print(type(dict_rsp))
            return dict_rsp
        except urllib.error.URLError as e:
            dict_error = {}
            if hasattr(e, "code"):
                dict_error = {}
                dict_error['ret'] = -1
                dict_error['httpcode'] = e.code
                dict_error['msg'] = "sdk http post err"
                return dict_error
            if hasattr(e,"reason"):
                dict_error['msg'] = 'sdk http post err'
                dict_error['httpcode'] = -1
                dict_error['ret'] = -1
                return dict_error
            else:
                dict_error = {}
                dict_error['ret'] = -1
                dict_error['httpcode'] = -1
                dict_error['msg'] = "system error"
                return dict_error

    #通用OCR
    def getOcrGeneralocr(self, image):
        self.url = url_preffix + 'ocr/ocr_generalocr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)    #图片的base64数据
        #print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  #image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #智能鉴黄
    def getVisionPorn(self, image):
        self.url = url_preffix + 'vision/vision_porn'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)    #图片的base64数据
        #print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  #image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 暴恐图片识别
    def getImageTerrorism(self, image):
            self.url = url_preffix + 'image/image_terrorism'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 身份证识别
    def getOcrIdcardocr(self, image, card_type):
        self.url = url_preffix + 'ocr/ocr_idcardocr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'card_type', card_type)
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 名片识别
    def getOcrBcocr(self, image):
            self.url = url_preffix + 'ocr/ocr_bcocr'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 行驶证驾驶证识别
    def getOcrDriverlicenseocr(self, image, type):
        self.url = url_preffix + 'ocr/ocr_driverlicenseocr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'type', type)
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 车牌识别
    def getOcrPlateocr(self, image):
            self.url = url_preffix + 'ocr/ocr_plateocr'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 营业执照识别
    def getOcrBizlicenseocr(self, image):
        self.url = url_preffix + 'ocr/ocr_bizlicenseocr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

        # 车牌识别

    #银行卡识别
    def getOcrCreditcardocr(self, image):
            self.url = url_preffix + 'ocr/ocr_creditcardocr'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    #手写体识别
    def getOcrHandwritingocr(self, image):
        self.url = url_preffix + 'ocr/ocr_handwritingocr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 人脸检测与分析	识别上传图像上面的人脸信息
    def getFaceDetectface(self, image, mode):
            self.url = url_preffix + 'face/face_detectface'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            setParams(self.data, 'mode', mode)
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 多人脸检测	识别上传图像上面的人脸位置，支持多人脸识别
    def getFaceDetectmultiface(self, image):
        self.url = url_preffix + 'face/face_detectmultiface'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 人脸对比	对请求图片进行人脸对比
    def getFaceFaceCompare(self, image_a, image_b):
            self.url = url_preffix + 'face/face_facecompare'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            image_a_data = base64.b64encode(image_a)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image_a', image_a_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            image_b_data = base64.b64encode(image_b)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image_b', image_b_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 跨年龄人脸识别	上传两张人脸照，返回最相似的两张人脸及相似度。
    # 支持多人合照、两张图片中的人处于不同年龄段的情况
    def getFaceDetectcrossageface(self, source_image, target_image):
        self.url = url_preffix + 'face/face_detectcrossageface'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        source_image_data = base64.b64encode(source_image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'source_image', source_image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        target_image_data = base64.b64encode(target_image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'target_image', target_image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 五官定位	对请求图片进行五官定位
    def getFaceFaceshape(self, image, mode):
            self.url = url_preffix + 'face/face_faceshape'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            setParams(self.data, 'mode', mode)
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 人脸识别	对请求图片中的人脸进行识别   需要创建个体
    def getFaceFaceidentify(self, image, group_id, topn):
        self.url = url_preffix + 'face/face_faceidentify'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'group_id', group_id)
        setParams(self.data, 'topn', topn)
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 人脸验证	对请求图片进行人脸验证   需要创建个体
    def getFaceFaceverify(self, image, person_id):
            self.url = url_preffix + 'face/face_faceverify'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            setParams(self.data, 'person_id', person_id)
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            sign_str = genSignString(self.data)
            #print(sign_str)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 个体创建	创建一个个体（Person）
    def getFaceNewperson(self, image, group_ids, person_id, person_name, tag):
        self.url = url_preffix + 'face/face_newperson'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'group_ids', group_ids)
        setParams(self.data, 'person_id', person_id)
        setParams(self.data, 'person_name', person_name)
        setParams(self.data, 'tag', tag)
        image_data = base64.b64encode(image)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        # print(sign_str)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 删除个体	删除一个个体（Person）
    def getFaceDelperson(self, person_id):
        self.url = url_preffix + 'face/face_delperson'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'person_id', person_id)
        sign_str = genSignString(self.data)
        # print(sign_str)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 增加人脸	将一组人脸（Face）加入到一个个体（Person）中
    def getFaceAddface(self, images, person_id, tag):
        self.url = url_preffix + 'face/face_addface'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'person_id', person_id)
        setParams(self.data, 'tag', tag)
        image_data = base64.b64encode(images)  # 图片的base64数据
        # print(image_data.decode())
        setParams(self.data, 'images', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
        sign_str = genSignString(self.data)
        # print(sign_str)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #文本翻译（AI Lab）
    def getNlpTextTrans(self, text, type):
        self.url = url_preffix + 'nlp/nlp_texttrans'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'text', text)
        setParams(self.data, 'type', type)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #文本翻译（翻译君）
    def getNlpTextTranslate(self, text, source, target):
        self.url = url_preffix + 'nlp/nlp_texttranslate'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'text', text)
        setParams(self.data, 'source', source)
        setParams(self.data, 'target', target)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 图片翻译（识别图片中的文字，并进行翻译）
    def getNlpImageTranslate(self, image, source, target, scene):
            self.url = url_preffix + 'nlp/nlp_imagetranslate'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            setParams(self.data, 'session_id', int(time.time()))
            image_data = base64.b64encode(image)  # 图片的base64数据
            # print(image_data.decode())
            setParams(self.data, 'image', image_data.decode())  # image类型要为string--decode，支持JPG、PNG、BMP格式
            setParams(self.data, 'source', source)
            setParams(self.data, 'target', target)
            setParams(self.data, 'scene', scene)
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 语音翻译（识别出音频中的文字，并进行翻译	）
    def getNlpSpeechTranslate(self, chunk, format, seq, end, source, target):
        self.url = url_preffix + 'nlp/nlp_speechtranslate'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'session_id', int(time.time()))
        speech_chunk = base64.b64encode(chunk)
        # print(type(speech_chunk.decode()))
        setParams(self.data, 'speech_chunk', speech_chunk.decode())  # speech_chunk类型为string
        setParams(self.data, 'format', format)
        setParams(self.data, 'seq', seq)
        setParams(self.data, 'end', end)
        setParams(self.data, 'source', source)
        setParams(self.data, 'target', target)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    # 语种识别（识别给出文本的语种	）
    def getNlpTextDetect(self, text, candidate_langs, force):
            self.url = url_preffix + 'nlp/nlp_textdetect'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            setParams(self.data, 'text', text)
            setParams(self.data, 'candidate_langs', candidate_langs)
            setParams(self.data, 'force', force)
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    # 语音识别-echo版    对音频进行语音识别，并返回语音的文字内容        测试识别不正确,不知道是不是音频问题
    def getAaiAsr(self, speech_echo, format, rate):
        self.url = url_preffix + 'aai/aai_asr'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        speech = base64.b64encode(speech_echo)
        setParams(self.data, 'speech', speech.decode())  # speech_chunk类型为string
        setParams(self.data, 'format', format)
        setParams(self.data, 'rate', rate)
        sign_str = genSignString(self.data)
        #print(sign_str)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

        # 语音识别-流式版(WeChat AI)

    # 语音识别-流式版（AI Lab）  对音频进行流式识别，轻松实现边录音边识别        测试识别不正确,不知道是不是音频问题
    def getAaiAsrs(self, chunk, speech_id, end_flag, format_id, rate, seq, chunk_len):
            self.url = url_preffix + 'aai/aai_asrs'
            setParams(self.data, 'app_id', self.app_id)
            setParams(self.data, 'app_key', self.app_key)
            setParams(self.data, 'time_stamp', int(time.time()))
            setParams(self.data, 'nonce_str', int(time.time()))
            speech_chunk = base64.b64encode(chunk)
            # print(type(speech_chunk.decode()))
            setParams(self.data, 'speech_chunk', speech_chunk.decode())  # speech_chunk类型为string
            setParams(self.data, 'speech_id', speech_id)
            setParams(self.data, 'end', end_flag)
            setParams(self.data, 'format', format_id)
            setParams(self.data, 'rate', rate)
            setParams(self.data, 'seq', seq)
            setParams(self.data, 'len', chunk_len)
            sign_str = genSignString(self.data)
            setParams(self.data, 'sign', sign_str)
            return self.invoke(self.data)

    #语音识别-流式版(WeChat AI)    对音频进行流式识别，轻松实现边录音边识别
    def getAaiWxAsrs(self, chunk, speech_id, end_flag, format_id, rate, bits, seq, chunk_len, cont_res):
        self.url = url_preffix + 'aai/aai_wxasrs'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        speech_chunk = base64.b64encode(chunk)
        #print(type(speech_chunk.decode()))
        setParams(self.data, 'speech_chunk', speech_chunk.decode()) #speech_chunk类型为string
        setParams(self.data, 'speech_id', speech_id)
        setParams(self.data, 'end', end_flag)
        setParams(self.data, 'format', format_id)
        setParams(self.data, 'rate', rate)
        setParams(self.data, 'bits', bits)
        setParams(self.data, 'seq', seq)
        setParams(self.data, 'len', chunk_len)
        setParams(self.data, 'cont_res', cont_res)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #有回应但分词不成功 主要在GBK编码问题 待解决
    def getNlpWordSeg(self, text):
        self.url = url_preffix + 'nlp/nlp_wordseg'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'text', text)
        sign_str = genSignString(self.data)
        #print('sign1', sign_str)     #鉴权没问题 在text的GBK编码
        #print(text, '***', text.encode('gbk'))
        setParams(self.data, 'sign', sign_str)
        #setParams(self.data, 'text', text.encode('gbk'))
        #print('sign2', sign_str)
        return self.invoke(self.data)

    #语义解析 意图成分识别
    def getNlpWordCom(self, text):
        self.url = url_preffix + 'nlp/nlp_wordcom'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'text', text)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #情感分析识别
    def getNlpTextPolar(self, text):
        self.url = url_preffix + 'nlp/nlp_textpolar'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'text', text)
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

    #智能闲聊 基础闲聊
    def getNlpTextChat(self, question):
        self.url = url_preffix + 'nlp/nlp_textchat'
        setParams(self.data, 'app_id', self.app_id)
        setParams(self.data, 'app_key', self.app_key)
        setParams(self.data, 'time_stamp', int(time.time()))
        setParams(self.data, 'nonce_str', int(time.time()))
        setParams(self.data, 'question', question)
        setParams(self.data, 'session', int(time.time()))
        sign_str = genSignString(self.data)
        setParams(self.data, 'sign', sign_str)
        return self.invoke(self.data)

