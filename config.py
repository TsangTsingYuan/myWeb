import os
#基地址
basedir = os.path.abspath(os.path.dirname(__file__))
#父类，通用配置     os.environ.get在环境变量中设置相应参数 
class Config:
    #在环境变量中设置SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    #新用户发送邮件通知 测试不行
    FLASKY_MAIL_SUBJECT_PREFIX = '[Hello,Internet]'
    FLASKY_MAIL_SENDER = 'Doyle <821978426@qq.com>'
    # 管理员地址--收件人
    HELLO_ADMIN = os.environ.get('HELLO_ADMIN')
    # 邮件主题的前缀
    FLASKY_MAIL_SUBJECT_PREFIX = '[Hello,Internet]'
    # 发件人的地址
    FLASKY_MAIL_SENDER = 'Doyle <821978426@qq.com>'
    #每页的记录值
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 10
    #
    #CKEDITOR_SERVE_LOCAL = True
    #UPLOADED_PATH = os.path.join(basedir, 'uploads')
    #文件上传地址
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'app/static/upload')
    ## 配置上传文件大小
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    #tencent AI
    app_key = 'UzHvJu0XoZymLbJZ'
    app_id = '1107055682'

    @staticmethod       #函数的静态方法
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}