from flask_wtf import FlaskForm
#字段
from wtforms import SubmitField, StringField, TextAreaField, BooleanField, SelectField, widgets
#验证函数
from wtforms.validators import DataRequired, Length, ValidationError, Email, Regexp
from ..models import Role, User
from flask_ckeditor import CKEditorField

class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

class NameForm(FlaskForm):
    name = StringField('姓名', validators=[Length(0, 64)])
    submit = SubmitField('提交')

#管理员级别的资料编辑表单   可编辑其他用户资料
class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名只能以字母开头，可以包含数字')])
    confirmed = BooleanField('是否确认')
    role = SelectField('角色', coerce=int)      #下拉列表 选择用户角色   coerce=int把字段值（role.id）转换为整数
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        #SelectField 实例     两个元素：选项的标识符和显示在控件中的文本字符串   元组中的标识符是角色的 id
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user
    #验证字段值是否变化，没有则跳过验证，有则确认与其他用户相应字段没有重复
    #validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数(如Regexp)一起调用（理解为在表单提交数据时验证）
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

#富文本编辑器表单
class PostForm(FlaskForm):
    title = TextAreaField("输入标题", validators=[DataRequired()])
    #富文本编辑器
    body = CKEditorField("输入文章内容", validators=[DataRequired()])
    submit = SubmitField('提交')

'''
class PostForm(FlaskForm):
    title = TextAreaField("输入标题", validators=[DataRequired()])
    body = TextAreaField("输入文章内容", validators=[DataRequired()])
    submit = SubmitField('提交')
'''

#评论表单
class CommentForm(FlaskForm):
    body = StringField('请输入评论', validators=[DataRequired()])
    submit = SubmitField('提交')