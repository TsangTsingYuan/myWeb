from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import login_manager, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
import bleach
from markdown import markdown


#权限常量
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMIT = 0x08
    ADMINISTER = 0x80

#关注数据表
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#一（Role）对多(User)  一个角色可属多个用户
#定义模型Role       Model基类
class Role(db.Model):
    #数据库中使用的表名
    __tablename__ = 'roles'
    #db.Column类的实例  第一个参数是数据库列和模型属性的类型
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    #user设为True  默认的用户角色
    default = db.Column(db.Boolean, default=False, index=True)
    #操作的权限位标志(如001,010分别表示关注\评论操作)
    permissions = db.Column(db.Integer)
    #userList=Role.users返回与角色相关联的用户组成的列表
    #第一个参数表明这个关系的另一端是哪个模型
    #backref 参数向 User 模型中添加一个 role 属性，从而定义反向关系。*****????
    # 这一属性可替代role_id 访问Role 模型--User.role，此时获取的是模型对象，而不是外键的值
    users = db.relationship('User', backref='role')    #???????
    #添加新角色
    @staticmethod
    def insert_roles():
        #在角色列表里新增角色或修改权限
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE, False),
            #'Test': (0xff, False),  #新增的角色
            'Administrator': (0xff, False)
        }
        for r in roles:
            #通过角色名查找现有的角色
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)     #没有找到就创建新角色对象
            role.permissions = roles[r][0]   #每个用户的权限
            role.default = roles[r][1]      #注册时默认角色为User
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    #数据库表名
    __tablename__ = 'users'
    #主键   列
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)   #使用邮箱登录
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    #邮件确认
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    #注册时间   当前时间
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    #上次访问时间 访问时更新
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    #外键   roles.id：roles表中行的id值   roles是表名
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    #向Post类添加author属性  Post类中使用Post.author可访问User模型?????
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #使用两个一对多关系实现的多对多关系
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    #一对多关系  一个用户发表多个评论
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    #定义默认的用户角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.followed.append(Follow(followed=self))       #注册时设为自己的关注者
        #根据电子邮件地址决定将其设为管理员还是默认角色（user ）
        if self.role is None:
            if self.email == current_app.config['HELLO_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    #检查用户是否有指定的权限  指定权限(role.permissions)与用户权限(permissions)进行位与
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions
    #检查管理员权限较常用到
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username

    #get方法(此处为读取密码)变为属性只需要加上@property装饰器即可,
    # @property本身又会创建@password.setter,负责把set方法变成给属性赋值(设置密码)
    @property
    def password(self):
        raise AttributeError('密码不可读')  #不可读取密码

    @password.setter  #设置密码
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    #验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #生成一个令牌，有效期默认为一小时
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    #检验令牌，如果检验通过，则把新添加的 confirmed 属性设为 True
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 重设令牌
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
    #刷新最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    #生成虚拟用户
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    #关注
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    #取消关注
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    #正在关注
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    #被关注
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    #获取所关注用户的文章
    @property
    def followed_posts(self):
        #12.3章节 数据库联结查询
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    #把用户设为自己的关注者
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

#用户未登录时
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

#加载用户的回调函数  如果能找到用户必须返回用户对象；否则应该返回None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#文章模型
class Post(db.Model):
    __tablename__ = 'posts'     #数据库表
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))   #users是数据库表名 外键
    #一对多关系  一篇文章有多个评论
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    #生成虚拟博客文章
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(title = forgery_py.lorem_ipsum.sentences(randint(1, 2)),
                     body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    #把 body 字段中的文本渲染成 HTML 格式，结果保存在 body_html 中，
    # 自动且高效地完成Markdown 文本到HTML的转换
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class', 'style'],
            'a': ['href', 'rel'],
            'img': ['alt', 'src'],
        }
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, attributes=attrs, strip=True))
#on_changed_body 函数注册在 body 字段上，是 SQLAlchemy“set”事件的监听程序，
# 这意味着只要这个类实例的 body 字段设了新值，函数就会自动被调用
db.event.listen(Post.body, 'set', Post.on_changed_body)     #用法查看SQL文档


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)    #查禁不当评论
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


