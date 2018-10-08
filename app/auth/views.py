from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_login import current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ModifyPasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


#过滤未确认的账户  每次请求前运行
@auth.before_app_request
def before_request():
    # 用户已登录     帐户未确认       请求端点不在认证蓝本中（访问认证路由需要获取权限所以需先确认帐户）
    #满足以上条件会拦截请求
    if current_user.is_authenticated:
        #每次收到请求时都要调用 ping,更新已登录用户的访问时间
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.'\
        and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()    #实例化登录表单
    #当表单在 POST 请求中提交时，Flask-WTF中的validate_on_submit() 会验证表单数据，尝试登入用户
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            #访问未授权的 URL 时会显示登录表单，Flask-Login会把原地址(未授权的 URL)保存在查询字符串的 next 参数中，
            # 这个参数可从 request.args 字典中读取,重定向到之前未授权的 URL（现在已登录授权）。如果查询字符串中没有next 参数，则重定向到首页
            return redirect(request.args.get('next') or url_for('main.index'))     #flask-login 的 login_required 转到登录页面时会有 next 这个查询
        flash('非法的用户名或密码')
    #当请求类型是 GET 时，视图函数直接渲染模板，即显示表单
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required     #登录才可以退出
def logout():
    logout_user()
    flash('你已经退出，请重新登录')
    return redirect(url_for('main.index'))
#能发送确认邮件的注册路由
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认你的帐户',
                   'auth/email/confirm', user=user, token=token)
        flash('已发送邮件到注册邮箱，请确认')
        return redirect(url_for('main.index'))
        #flash('你现在可以登录了')
        #return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

#确认用户的帐户
@auth.route('/confirm/<token>')
@login_required     #用户点击确认邮件中的链接后，要先登录，然后才能执行这个视图函数
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('帐户已确认，谢谢!')
    else:
        flash('帐户确认链接非法或已过期')
    return redirect(url_for('main.index'))


#重定向到 /auth/unconfirmed 路由，显示一个确认账户相关信息的页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#重新发送确认邮件，以防之前的邮件丢失
@auth.route('/confirm')
@login_required     #需先登录，确保访问时知道请求再次发送邮件的是哪个用户
def resend_confirmation():
    #current_user（已登录用户即目标用户）重做注册路由中的操作
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认帐户',
               'auth/email/confirm', user=current_user, token=token)
    flash('已重新发送邮件到注册邮箱，请确认')
    return redirect(url_for('main.index'))

#修改密码
@auth.route('/modify_password', methods=['GET', 'POST'])
@login_required
def modify_password():
    form = ModifyPasswordForm()    #实例化登录表单
    #当表单在 POST 请求中提交时，Flask-WTF中的validate_on_submit() 会验证表单数据，尝试登入用户
    if form.validate_on_submit():
        #确认原密码正确
        if current_user.verify_password(form.old_password.data):
            #将新密码写入数据库
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('成功修改密码')
            return redirect(url_for('auth.logout'))
        flash('旧密码错误')
    #当请求类型是 GET 时，视图函数直接渲染模板，即显示表单
    return render_template('auth/modify_password.html', form=form)


#发送重设密码确认邮件 视图函数
@auth.route('/reset_password', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重设密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('确认重设密码请查看邮箱的邮件提示')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

#点击重设密码的确认地址进行新密码重设
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('已成功重设密码')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

#重设邮箱
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '确认邮箱地址',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('请登录邮箱查收确认邮件')
            return redirect(url_for('main.index'))
        else:
            flash('非法的邮箱或密码')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('邮箱已更新')
    else:
        flash('非法请求')
    return redirect(url_for('main.index'))
