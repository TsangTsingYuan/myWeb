from flask import render_template, url_for, send_from_directory, current_app, request, make_response
from .forms import UploadForm, TextForm
from app import photos
from . import ai, apiutil_py3
import os, datetime
import json

@ai.route('/form',methods=['GET','POST'])
def form():
    ocr = 1
    msg = []
    form = UploadForm()
    if form.validate_on_submit():
        # 生成随机的文件名
        time_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        suffix = os.path.splitext(form.photo.data.filename)[1]
        filename = time_prefix + suffix
        photos.save(form.photo.data, name=filename)
        # 获取上传文件的URL
        #img_url = photos.url(filename)

        img = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        #print(img)
        with open(img, 'rb') as bin_data:
            image_data = bin_data.read()  # 读取文件内容，需转换为base64编码
        #image_data = form.photo.data.read()
        ai_obj = apiutil_py3.AiPlat('1107055682', 'UzHvJu0XoZymLbJZ')

        #print('----------------------SEND REQ----------------------')
        rsp = ai_obj.getOcrBcocr(image_data)

        if rsp['ret'] == 0:
            for i in rsp['data']['item_list']:
                msg.append(i['itemstring'])
                print(i['item'], i['itemstring'])
            #print('----------------------API SUCC----------------------')
            return render_template('ai/show.html', msg=msg, ocr=ocr)
        else:
            print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
            print('----------------------API FAIL----------------------')
        #请注意保存文件时是用了UploadSet对象调用了save方法，而且这个save方法的第一个参数是文件对象，第二个参数是文件名
    return render_template('ai/form.html',form=form)
'''
@ai.route('/show/<filename>')
def show(filename):
    path = current_app.config['UPLOADED_PHOTOS_DEST']
    return send_from_directory(path, filename)

# show photo
@ai.route('/show/<filename>', methods=['GET'])
def show(filename):
    path = current_app.config['UPLOADED_PHOTOS_DEST']
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(path, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass
'''

@ai.route('/trans',methods=['GET','POST'])
def trans():
    trans = 1
    type = 0
    form = TextForm()
    if form.validate_on_submit():
        text = form.text.data

        ai_obj = apiutil_py3.AiPlat('1107055682', 'UzHvJu0XoZymLbJZ')

        #print('----------------------SEND REQ----------------------')
        rsp = ai_obj.getNlpTextTrans(text, type)

        if rsp['ret'] == 0:
            org_text = rsp['data']['org_text']
            trans_text = rsp['data']['trans_text']
            #print('----------------------API SUCC----------------------')
            return render_template('ai/show.html', org_text=org_text, trans_text=trans_text, trans=trans)
        else:
            print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
            print('----------------------API FAIL----------------------')
        #请注意保存文件时是用了UploadSet对象调用了save方法，而且这个save方法的第一个参数是文件对象，第二个参数是文件名
    return render_template('ai/form.html',form=form)