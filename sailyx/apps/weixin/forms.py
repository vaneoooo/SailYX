#coding=utf-8
from uliweb.form import *
from uliweb.i18n import ugettext as _

class RegisterForm(Form):
    form_buttons = Submit(value=_('Register'), _class="btn btn-primary")
#    form_title = _('Register')

    username = StringField(label=_('Username'), required=True)
    password = PasswordField(label=_('Password'), required=True)
    password1 = PasswordField(label=_('Password again'), required=True)
    email = StringField(label=_('Email'),required=True)
    next = HiddenField()

    def validate_username(self, data):
        from uliweb.orm import get_model

        User = get_model('user')
        user = User.get(User.c.username==data)
        if user:
            return _('User "%s" is already existed!') % data

    def validate_email(self, data):
        from uliweb.orm import get_model
        User = get_model('user')
        user = User.get(User.c.email==data)
        if user:
            return _('Email "%s" is already existed!') % data


    def form_validate(self, all_data):
        if all_data.password != all_data.password1:
            return {'password1' : _('Passwords are not match.')}

class ArticleForm(Form):
    title = StringField(label='标题', required=True)
    column = format = SelectField(label='Format:', choices=[('rst', 'reStructureText'), ('text', 'Plain Text')], default='rst')
    special = format = SelectField(label='Format:', choices=[('rst', 'reStructureText'), ('text', 'Plain Text')], default='rst')
    content = TextField(label='正文')
    attribute = RadioSelectField(label='Format:', choices=[('rst', 'reStructureText'), ('text', 'Plain Text')], default='rst')

#class LoginForm(Form):
#    username = UnicodeField(label=_('Username'), class="span12", required=True)
#    password = PasswordField(label=_('Password'), class="span12", required=True)
#    rememberme = BooleanField(label=_('Remember Me'))
#
#    def form_validate(self, all_data):
#
