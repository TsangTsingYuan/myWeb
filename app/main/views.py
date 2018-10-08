import datetime
from flask import request, current_app, render_template, session, redirect, url_for, abort, flash, send_from_directory, make_response
from app import db, ckeditor
from . import main #本目录 main在__init__里
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm #同一目录下的forms文件
from ..models import User, Role, Permission, Post, Comment  #导入上级目录的models文件中的User
from ..email import send_email
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from flask_ckeditor import upload_success, upload_fail
import os
import random

#分页显示博客文章的首页路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,
                    author=current_user._get_current_object())  #current_user 由 Flask-Login提供 数据库需要真正的用户对象
        db.session.add(post)
        return redirect(url_for('.index'))
    #显示所有博客文章或只显示所关注用户的文章
    show_followed = False
    if current_user.is_authenticated:
        #选项存储在 cookie 的 show_followed字段   该值在视图函数/路由中设置
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        #只显示所关注用户的文章
        query = current_user.followed_posts
    else:
        query = Post.query   #显示所有博客文章
        #获取get请求参数(获取地址栏中参数)  请求url地址里有?XX=XX字眼的，该参数就一定是通过request.args获取。
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination)


'''
#处理博客文章的首页路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,
                    author=current_user._get_current_object())  #current_user 由 Flask-Login提供 数据库需要真正的用户对象
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)
'''
'''
@main.route('/', methods=['GET', 'POST'])
def index():
    # name = None
    form = NameForm()
    if form.validate_on_submit():
        # 在数据库中查找提交的名字
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # 新数据添加到会话中  db.session与session[]没有关系，不一样
            user = User(username=form.name.data)
            db.session.add(user)
            # 没有找到就是新用户，不同的欢迎信息
            session['known'] = False
            # 新用户发邮件通知管理员
            if current_app.config['HELLO_ADMIN']:
                send_email(current_app.config['HELLO_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        # 数据存储在用户会话，在请求之间记住数据
        session['name'] = form.name.data
        form.name.data = ''
        # 刷新页面时浏览器会重新发送之前最后一个请求，如果是包含表单数据的POST请求
        # 刷新页面会再次提交交单，所以使用重定向，浏览器发起GET请求
        return redirect(url_for('.index'))
    # 对于不存在的键，get()会返回默认值None
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False), current_time=datetime.utcnow())
'''

#动态URL 尖括号内容为动态部分，匹配即可映射到该路由
#用户名存在则渲染模板user.html，并把用户名作为参数传入模板。不存在，则返回404错误
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)
    #return render_template('user.html', name=name)  #第一个name是模板中的占位变量，第二个name是真实值，带入替换

#编辑个人资料
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required     #用户登录才可以更改资料
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    #validate_on_submit返回false,使用 current_user 中保存的初始值
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    #id不正确，则会返回404错误
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('资料已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
'''
#current_app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
@main.route('/files/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)

#CKEditor根目录的配置文件config.js来设置upload路由
@main.route('/upload', methods=['POST'])
def upload():
    #current_app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
    f = request.files.get('upload')  # 获取上传图片文件对象
    extension = f.filename.split('.')[1].lower()
    # Add more validations here 对上传的图片进行验证和处理（大小、格式、文件名处理等)
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:  # 验证文件类型示例
        return upload_fail(message='请选择图片!')  # 返回upload_fail调用
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    url = url_for('.uploaded_files', filename=f.filename)
    return upload_success(url, f.filename)  # 返回upload_success调用
'''

#添加富文本编辑功能  开启图片上传功能
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
        return upload_fail(message=error)
    return upload_success(url, rnd_name)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('你的评论已提交')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

'''
#数据库分配的唯一id 字段
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    #，post.html 模板接收一个列表作为参数，必须传入列表，_posts.html 模板才能在这个页面中使用
    return render_template('post.html', posts=[post])
'''

#编辑博客文章
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

#“关注”路由和视图函数
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未知用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了此用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('你关注了 %s.' % username)
    return redirect(url_for('.user', username=username))

#“取消关注”路由和视图函数
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未知用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了此用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('你取消关注 %s.' % username)
    return redirect(url_for('.user', username=username))

#“关注者”路由和视图函数
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未知用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="粉丝列表",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

#“粉丝”路由和视图函数
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未知用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    followed = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="关注列表",
                           endpoint='.followed', pagination=pagination,
                           follows=followed)

#指向这两个路由的链接添加在首页模板中。点击这两个链接后会为
#cookie的show_followed字段设定适当的值，然后重定向到首页
@main.route('/all')
@login_required
def show_all():
    #cookie 只能在响应对象中设置 要使用 make_response()方法创建响应对象
    resp = make_response(redirect(url_for('.index')))       #响应对象
    #前两个参数分别是 cookie名和值    max_age为cookie的过期时间，单位秒
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp

#管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMIT)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

#显示/屏蔽评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMIT)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMIT)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')