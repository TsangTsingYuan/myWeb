from app import mail
from flask_mail import Message
from flask import current_app, render_template
from threading import Thread
import os



#异步发送邮件
def send_async_email(app, msg):
    with app.app_context():     #激活程序上下文
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()     #开了一个线程就不能使用 current_app,在线程里面使用
    # current_app 将获取不到对象，因为他没有 flask 上下文
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr