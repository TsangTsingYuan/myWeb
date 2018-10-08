import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    #在测试前运行
    def setUp(self):
        #创建测试环境，使用测试配置创建程序
        self.app = create_app('testing')
        #激活上下文，确保能在测试中使用current_app
        self.app_context = self.app.app_context()
        #推送程序上下文
        self.app_context.push()
        #创建数据库
        db.create_all()
    #测试后运行
    def tearDown(self):
        #删除数据库
        db.session.remove()
        db.drop_all()
        #删除程序上下文
        self.app_context.pop()
    #名字以test_ 开头的函数都作为测试执行
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])