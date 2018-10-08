from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length
from wtforms import SubmitField, StringField
from app import photos


# 文件上传表单
class UploadForm(FlaskForm):
    photo = FileField(validators=[FileRequired(message='未选择文件'),
                                  FileAllowed(photos, message='只能上传图片')])
    submit = SubmitField('上传')

class TextForm(FlaskForm):
    text = StringField('原文', validators=[DataRequired(), Length(1, 1024)])
    submit = SubmitField('提交')