from flask_login import login_required, logout_user, current_user, login_user
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from .forms import LoginForm, RegistrationForm
from ..models import User, Permission
from app import db
from flask import request, render_template, redirect, url_for, flash, current_app
from ..decorators import admin_required
from ..email import send_email
from wtforms.validators import DataRequired
import gettext

#主URL  http://127.0.0.1:5000/admin/
#首页默认template='admin/index.html'，MyView1的index不可与此同名
# 否则会首页被默认调用
'''
class MyView1(BaseView):
    # URL是MyView1
    @expose('/')
    def index1(self):
        return self.render('admin/MyIndex.html')
        #首页出现index.html内容，MyView1报出错
        #return self.render('admin/index.html')

    # URL是MyView1/test/
    @expose('/test/')
    def test(self):
        #return self.render('admin/test.html')
        return 'Hello World!'
'''

#每个view类就是一个页面，在里面处理相关内容, 类名相当于蓝本
#创建处理登录和注册的自定义索引视图类
#AdminIndexView 首页视图
class MyView(AdminIndexView):
    # URL是MyView1
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login'))
        return self.render('admin/index.html')
        #return self.render('admin/index.html')
        #首页出现index.html内容，MyView1报出错
        #return self.render('admin/index.html')

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        form = LoginForm()  # 实例化登录表单
        # 当表单在 POST 请求中提交时，Flask-WTF中的validate_on_submit() 会验证表单数据，尝试登入用户
        if form.validate_on_submit():
            #user = 'test'
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                # 访问未授权的 URL 时会显示登录表单，Flask-Login会把原地址(未授权的 URL)保存在查询字符串的 next 参数中，
                # 这个参数可从 request.args 字典中读取,重定向到之前未授权的 URL（现在已登录授权）。如果查询字符串中没有next 参数，则重定向到首页
                return redirect(request.args.get('next') or url_for('.index'))  # flask-login 的 login_required 转到登录页面时会有 next 这个查询

            flash('非法的用户名或密码')
        # 当请求类型是 GET 时，视图函数直接渲染模板，即显示表单
        return self.render('admin/login.html', form=form)

    @expose('/register', methods=['GET', 'POST'])
    def register(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(email=form.email.data,
                        username=form.username.data,
                        confirmed=True,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
            '''
            token = user.generate_confirmation_token()
            #超级管理员确认注册帐户
            send_email(current_app.config['HELLO_ADMIN'], '请超级管理员确认新帐户',
                       'auth/email/confirm', user=user, token=token)
            flash('已发送邮件到超级管理员邮箱，请确认')
            '''
            flash('注册成功，请登录')
            login_user(user)
            return redirect(url_for('.login'))
            # flash('你现在可以登录了')
            # return redirect(url_for('auth.login'))
        return self.render('admin/register.html', form=form)

    @expose('/logout')
    @login_required  # 登录才可以退出
    def logout(self):
        logout_user()
        flash('你已经退出，请重新登录')
        return redirect(url_for('.index'))
#要求登录
class UserView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login', next=request.url))

    column_labels = dict(email='邮箱', username='用户名', confirmed='已确认', name='姓名', \
                         location='地址', about_me='关于我', member_since='注册时间', last_seen='登录时间', role_id='角色',comments='评论')
    #form_columns = ['email', 'username']

    #can_view_details = True
    column_exclude_list = ['password_hash', ]       #不在列表中显示
    column_searchable_list = ['email', 'username']  #可用于搜索
    column_filters = ['location']   #可用于增加过滤条件
    column_editable_list = ['name', 'username', 'confirmed']  #内联编辑  在原页面进行编辑和保存
    form_excluded_columns = ['password_hash']    #在创建和编辑表单中不显示
    #inline_models = ['post',]  #还要看定义理解一下
    can_export = True

    #指定WTForms字段参数  表单字段参数字典。请参阅WTForms文档可能的选项列表
    #此处要求字段必填
    form_args = {
        'name': {
            'label': 'First Name',
            'validators': [DataRequired()]
        }
    }
    #
    form_widget_args = {
        'name': {
            'rows': 10,
            'style': 'color: black'
        }
    }
    #定制批量操作  确认帐户
    @action('confirmed', '确认帐户', 'Are you sure you want to confirm selected users?')
    def action_confirm(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            for user in query.all():
                #确认帐户
                if not user.confirmed:
                    user.confirmed = True
                    count += 1
                    db.session.add(user)    #把改动写进数据库
            flash('%s users were successfully confirmed.' % count)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to confirm users. %s error' %str(ex))

#与其他表关联的外键？？？
class PostView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login', next=request.url))

    column_labels = dict(title='标题', body='正文', body_html='html正文',  \
                         timestamp='修改时间', author_id='作者', comments='评论')

    can_view_details = True  #需要显示的列太多时生效
    #添加和编辑表单是否显示在列表页面的模态窗口中，而不是专用的创建和编辑页面
    #在当前页面跳出窗口进行添加或编辑
    create_modal = True
    edit_modal = True
    #可以通过指定选择列表来限制文本字段的可能值
    form_choices = {
        'title': [
            ('MR', 'Mr'),
            ('MRS', 'Mrs'),
            ('MS', 'Ms'),
            ('DR', 'Dr'),
            ('PROF', 'Prof.')
        ]
    }


class FollowView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('.login', next=request.url))

    column_labels = dict(follower_id='关注', followed_id='粉丝', timestamp='关注时间')
    #column_searchable_list = ['users.id']  # 可用于搜索
    #inline_models = ['users.id']







