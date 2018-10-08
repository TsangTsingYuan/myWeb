from flask import Flask, render_template, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_babelex import Babel
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
import os.path as op

babel = Babel()
ckeditor = CKEditor()       #富文本编辑器
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
#不同安全等级  'strong'：记录客户端IP地址和浏览器的用户代理信息，如果发现异动就登出用户
login_manager.session_protection = 'strong'
#设置登录页面的端点  蓝本名.函数名
login_manager.login_view = 'auth.login'

# 文件上传
photos = UploadSet('photos', IMAGES)


#view放在顶部会报错ImportError: cannot import name 'login_manager'
from .admin.views import MyView, UserView, PostView, FollowView
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.fileadmin  import FileAdmin
#更改flask_admin默认首页导航栏信息  看源码AdminIndexView(默认视图)的默认参数
admin = Admin(name= '后台管理', index_view=MyView(name='首页'))


#创建程序   工厂函数返回创建的程序实例
def create_app(config_name):
    app = Flask(__name__)       #实例化主模块
    app.config.from_object(config[config_name])     #配置
    config[config_name].init_app(app)       #Config的初始化
    #Flask扩展自带的初始化
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    #login_manager_admin.init_app(app)
    admin.init_app(app)
    ckeditor.init_app(app)
    babel.init_app(app)
    # 上传的初始化
    configure_uploads(app, photos)
    ## 配置上传文件大小，默认64M，设置None则会采用config中MAX_CONTENT_LENGTH配置选项
    patch_request_class(app, size=None)

    #flask-admin本地化 中文
    @babel.localeselector
    def get_locale():
        override = 'zh_Hans_CN'
        if override:
            session['lang'] = override
        return session.get('lang', 'en')

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint    #.main---当前main文件夹   main---在__init__.py中的蓝本实例
    app.register_blueprint(main_blueprint)  #注册main蓝本

    from .auth import auth as auth_blueprint
    #url_prefix可选参数。注册后蓝本中定义的所有路由都会加上指定的前缀/auth
    #/login 路由会注册成 /auth/login，完整的URL---http://localhost:5000/auth/login
    app.register_blueprint(auth_blueprint, url_prefix='/auth')    #注册auth 蓝本

    from .AItencent import ai as ai_blueprint  # .main---当前main文件夹   main---在__init__.py中的蓝本实例
    app.register_blueprint(ai_blueprint, url_prefix='/ai')  # 注册main蓝本

    #增加导航栏栏目
    #admin.add_view(MyView(name= 'Hello 1'))
    from .models import User, Post, Follow
    admin.add_view(UserView(User, db.session, name='用户管理'))
    admin.add_view(PostView(Post, db.session, name='文章管理'))
    admin.add_view(FollowView(Follow, db.session, name='关注管理'))

    path = op.join(op.dirname(__file__), 'static')
    admin.add_view(FileAdmin(path, name='Static文件'))        #'/static/'是否包含  一样的效果
    #admin.add_view(FileAdmin(path, '/static/', name='Static Files'))

    return app