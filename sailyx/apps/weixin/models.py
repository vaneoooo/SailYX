#coding=utf-8

from uliweb.orm import *
from uliweb.utils.common import get_var

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)
    # The rest of the supported algorithms are supported by hashlib, but
    # hashlib is only available in Python 2.5.
    try:
        import hashlib
    except ImportError:
        if algorithm == 'md5':
            import md5
            return md5.new(salt + raw_password).hexdigest()
        elif algorithm == 'sha1':
            import sha
            return sha.new(salt + raw_password).hexdigest()
    else:
        if algorithm == 'md5':
            return hashlib.md5(salt + raw_password).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)

def encrypt_password(raw_password):
    import random
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, raw_password)
    return '%s$%s$%s' % (algo, salt, hsh)


class User(Model):
    username = Field(str, verbose_name=('用户名'), max_length=30, unique=True, index=True, nullable=False)
    nickname = Field(str, verbose_name=('Nick Name'), max_length=30)
    email = Field(str, verbose_name=('邮箱'), max_length=40, unique=True)
    password = Field(str, verbose_name=('密码'), max_length=128)
    is_superuser = Field(bool, verbose_name=('是否为管理员'))
    last_login = Field(datetime.datetime, verbose_name=('最后登录时间'))
    date_join = Field(datetime.datetime, verbose_name=('注册时间'), auto_now_add=True)
    image = Field(FILE, verbose_name=('头像'), max_length=256)
    active = Field(bool, verbose_name=('Active Status'))
    locked = Field(bool, verbose_name=('Lock Status'))
    ip_join = Field(str, verbose_name='注册IP')
    weibo = Field(str, verbose_name='微博')
    blog = Field(str, verbose_name='博客')
    qq = Field(str, verbose_name='QQ号', max_length=20)
    description = Field(TEXT, verbose_name='自我介绍')
    sex = Field(CHAR, verbose_name='性别', choices=get_var('PARA/SEX'))


    def set_password(self, raw_password):
        self.password = encrypt_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        return check_password(raw_password, self.password)

    def get_image_url(self):
        from uliweb.contrib.upload import get_url
        from uliweb.contrib.staticfiles import url_for_static

        if self.image:
            return get_href(self.image)
        else:
            return functions.url_for_static('images/user%dx%d.jpg' % (50, 50))

    def get_default_image_url(self, size=50):
        from uliweb.contrib.staticfiles import url_for_static
        return functions.url_for_static('images/user%dx%d.jpg' % (size, size))

    def __unicode__(self):
        return self.username

    class Meta:
        display_field = 'username'

    class AddForm:
        fields = ('username', 'nickname', 'email', 'weibo', 'blog', 'qq', 'description', 'is_superuser')

    class EditForm:
        fields = ('username', 'nickname', 'email', 'weibo', 'blog', 'qq', 'description', 'is_superuser')

    class DetailView:
        fields = ('username', 'nickname', 'email', 'weibo', 'blog', 'qq', 'description', 'is_superuser', 'date_join', 'last_login')


    class Table:
        fields = [
            {'name':'username'},
            {'name':'email'},
            {'name':'is_superuser'},
            {'name':'date_join'},
            {'name':'last_login'},
            {'name':'ip_join'},
        ]

class Tags(Model):
    name = Field(str,verbose_name='标签名称',unique=True)

    def __unicode__(self):
        return self.name


class PhoneNumber(Model):
    name = Field(str, verbose_name='名称',max_length=200,unique=True)
    ot = Field(str,verbose_name='原始标签', max_length=300)
    number1 = Field(str, verbose_name='电话号码1',max_length=20,unique=True)
    number2 = Field(str, verbose_name='电话号码2',max_length=20)
    number3 = Field(str, verbose_name='电话号码3',max_length=20)
    address = Field(str, verbose_name='地址',max_length=200)
    tag = ManyToMany(Tags,collection_name='tags',verbose_name='标签')
    level = Field(int,verbose_name='可查询范围',default=0)