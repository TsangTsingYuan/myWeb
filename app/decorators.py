from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission
#自定义修饰器  视图函数只对具有特定的用户开放
#检查常规权限
def permission_required(permission):
    def decorator(f):
        #decorated_function =  wraps(decorated_function)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#检查管理员权限
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

'''
#例子  应放在views.py,此处仅为例子理解
from decorators import admin_required, permission_required 
from .models import Permission 
 
@main.route('/admin') 
@login_required 
@admin_required #需要管理员权限
def for_admins_only(): 
    return "For administrators!" 
 
@main.route('/moderator') 
@login_required 
@permission_required(Permission.MODERATE_COMMIT) 
def for_moderators_only(): 
    return "For comment moderators!"

'''

