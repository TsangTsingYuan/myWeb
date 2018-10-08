#创建认证蓝本
from flask import Blueprint

ai = Blueprint('ai', __name__)  #实例化创建蓝本

from . import views