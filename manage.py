#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
#自定义命令  函数名就是命令名  python manage.py test
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    #调用了unittest 包提供的测试运行函数
    tests = unittest.TestLoader().discover('tests')  #引号内tests为文件夹名字
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()