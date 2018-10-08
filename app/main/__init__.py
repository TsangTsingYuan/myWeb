#创建蓝本
from flask import Blueprint
#有两个必须指定的参数：蓝本的名字main 和蓝本所在的包或模块。
# 和程序一样，大多数情况下第二个参数使用Python的__name__ 变量即可
main = Blueprint('main', __name__)  #实例化创建蓝本
#路由保存在views.py，错误处理程序保存在errors.py
#末尾导入是为了避免循环导入依赖，因为在views.py errors.py还要导入蓝本
from . import views, errors
from ..models import Permission
#在模板中可能也需要检查权限,上下文处理器能让变量在所有模板中全局可访问
#把 Permission类加入模板上下文
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)