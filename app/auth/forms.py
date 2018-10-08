from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

#登录表单
class LoginForm(FlaskForm):
    #验证函数----Length()   Email()
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    #属性为 type="password" 的 <input> 元素
    password = PasswordField('密码', validators=[DataRequired()])
    #复选框
    remember_me = BooleanField('保持登录状态')
    submit = SubmitField('登录')

#注册表单
class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email(message='非法的邮箱地址')])
    #^匹配输入字符串的开始位置 *匹配前面的子表达式零次或多次 $匹配输入字符串的结尾位置
    #Regexp后两个参数分别是正则表达式的旗标和验证失败时显示的错误消息
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名只能以字母开头，可以包含数字、下划线和点号')])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='密码必须一致')])
    submit = SubmitField('注册')

    #确保填写的值在数据库中没出现过
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册')

#修改密码表单
class ModifyPasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired()])
    new_password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('new_password', message='密码必须一致')])
    submit = SubmitField('提交')

#重设密码表单
class ResetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email(message='非法的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='密码必须一致')])
    submit = SubmitField('重设密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重设密码')


class PasswordResetForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重设密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('该邮箱未注册')

class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更新邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

