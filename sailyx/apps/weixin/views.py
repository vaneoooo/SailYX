#coding=utf-8
import urllib
import hashlib,time
from lxml import etree
from uliweb import expose, functions
from uliweb.orm import get_model
from weixin.models import encrypt_password
from getlib import moviespider,weatherspider,wzspider,psbc

token = 'youxinweixinxuyongxiaozhan'#请自行填写你的微信taken
adinfo = u'|<a href="http://youxin.tv/ad">LANDER全球购 正品代购</a>'

try:
    import pylibmc
    mc = pylibmc.Client(["127.0.0.1"], binary=True)
except:
    mc = False

def validate(values):
    params = {}
    params['token'] = token
    params['timestamp'] = values['timestamp']
    params['nonce'] = values['nonce']

    signature = values['signature']
    echostr = values['echostr']
    a = sorted([v for k, v in params.items()])
    s = ''.join(a)
    res = hashlib.sha1(s).hexdigest()

    if res == signature:
        return echostr
    return False

@expose('/')
class FrontView(object):
    def __init__(self):
        self.PhoneNum = get_model('phonenumber')
        self.Tags = get_model('tags')

    @expose('/get_we')
    def gWeather(self):
        if mc:
            if mc.get('weather'):
                return mc.get('weather')
        import re
        weather = weatherspider()
        s = ''
        date = re.compile('(?P<date>\d+:\d\d)')
        for w in weather:
            s += w[0]
            s += '\b\n'
            s += w[1]
            s += '\b\n'
            s = date.sub(lambda m: m.groups()[0] + '\n\n', s)
            s = s.replace(' ','')
        if not mc:
            return (s)
        mc.set('weather',s,time=3600)
        return (mc.get('weather'))

    @expose('/get_movie')
    def gMovie(self):
        if mc:
            if mc.get('movie_list'):
                return mc.get('movie_list')
        content = moviespider()
        if len(content)<50:
            return (u'今天的电影信息还没有发布出来，您可以稍候再来查询。\b\n\b\n如果超过中午12:00仍未返回电影信息，则可能是电影院没有发布今日影讯，您可以直接致电大世界影院询问：6888686\b\n' + adinfo)
#        if not content[0]:
#            return (u'哎哟~今天电影院还没发布电影信息~稍等会再来吧。\b\n' + adinfo)
#        s = ''
#        for i in range(0,len(content[0])):
#            s+=''.join(content[0][i])
#            s+='\b\n'
#            s+=',    '.join(content[1][i])
#            s+='\b\n'
#            s+=',    '.join(content[2][i])
#            s+='\b\n'
        content += u'\b\n省钱提示：\b\n购票出示邮储银行信用卡、储蓄卡，最高享受5折优惠！\b\n'
        content += adinfo
        mc.set('movie_list',content,time=7200)
        return (mc.get('movie_list'))

    @expose('/get_wz')
    def gWz(self,cp=None):
        if not cp:
            s=u'请输入一个车牌号码'
            return s
        else:
            cp = cp.encode('utf-8')
        content,connect = wzspider(cp)
        if not connect:
            return (u'交警系统查询接口超时，无法进行查询，请稍候再试。\b\n\b\n如果您在车牌中加入空格或其他汉字，标点符号，也可能导致查询超时，请检查您的车牌输入是否标准\b\n\b\n叙永小站其他查询服务正常工作中，欢迎使用')
        count = len(content)
        s = ''
        scaler = 1
        for i in range(0,count):
            s+=''.join(content[i][0])
            s+=':'
            temp = ''.join(content[i][1])
            s+=''.join(temp)
            s+='\n'
            if scaler == 7:
                s+='\n'
                scaler = 0
            scaler += 1
        s+=u'该车未处理违章合计'+str(count/7)+u'次'
        s += adinfo
        if len(s)>675:
            s=u'该车未处理违章合计'+str(count/7)+u'次，由于违章内容过多，微信字数限制，当前暂无法完整展示\b\n'
            s += adinfo
        return (s)

    @expose('/get_phonenumber')
    def get_phonenumber(self,phone=None):
        if not phone:
            return u'请输入一个查询关键字'
        s = ''
        phone = phone.replace(u'电话','')
        phone = phone.replace(u'号码','')
        tag = self.Tags.get(self.Tags.c.name==phone)
        if not tag:
            s = u'号码暂未收录。\b\n\b\n如果您知道这个号码，也可以回复我们。我们会尽快添加号码。\b\n\b\n您也可以检查输入文字是否正确，如“苏荷 电话”输入成了“苏河”，“富丽假日”输入为了“富力假日”\b\n\b\n查询不用添加“叙永”字样，例如输入“苏荷 电话”能够正确查询，输入“叙永苏荷 电话”则无法正确查询，谢谢您的使用，祝您天天开心。'
            s += adinfo
            return (s)
        phone_list = tag.tags.all()
        if phone_list:
            for p in phone_list:
                s += p.name
                s += ':\n'
                s += p.number1 + ','
                s += p.number2 + ','
                s += p.number3 + ''
                s += '\n'
        return (s + adinfo)

    @expose('/')
    def index(self):
        if request.method == 'GET' and request.values:
            echostr = validate(request.values)
            if echostr:
                return echostr
        if mc:
            if mc.get('is_test'):
                return mc.get('is_test')

        if request.method == 'POST':
            data = request.data
            root = etree.fromstring(data)
            child = list(root)
            recv = {}
            for i in child:
                recv[i.tag] = i.text

            is_movie = u'电影'
            is_weather = u'天气'
            is_phone = u'电话'
            is_number = u'号码'
            is_wz = u'川'
            is_welcome = 'subscribe'
            is_movie_num = '1'
            is_wz_num = '2'
            textTpl = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
            </xml>"""

            if recv['MsgType'] == 'text':
                psbcKey = psbc(recv['Content'])
                if is_movie in recv['Content'] or is_movie_num == recv['Content']:
                    recv['Content'] = self.gMovie()
                elif is_wz in recv['Content']:
                    recv['Content'] = self.gWz(recv['Content'])
                elif is_weather in recv['Content']:
                    recv['Content'] = self.gWeather()
                elif is_wz_num == recv['Content']:
                    recv['Content'] = u'请发送格式为“川E00000”的车牌号码，我们将马上为您查询是否违章'
                elif is_phone in recv['Content'] or is_number in recv['Content']:
                    recv['Content'] = self.get_phonenumber(recv['Content'])
                elif psbcKey:
                    recv['Content'] = psbcKey
                else:
                    recv['Content'] = u'收到您的消息啦!\b\n\b\n查电话，请记得添加“电话”或“号码”字样\b\n\b\n1：电影上映\b\n（输入文字“电影”或数字“1”）\b\n\b\n2：车辆违章\b\n（输入“川E00000”格式的车牌）\b\n\b\n3:电话查询，输入名称+号码（例如：东方明珠 电话，或 KTV 号码）\b\n\b\n（号码库仍在充实中，如有遗漏，欢迎告之~）\b\n\b\n如您需要广告服务，稍候我们会发消息联系您。'

            elif recv['MsgType'] == 'event':
                recv['MsgType'] = 'text'
                recv['Content'] = u"""嘿！就是你！等你好久啦！一眼就看出来你是天赋异禀骨骼清奇独具慧眼的人。为什么？！就因为万中无一的你添加了我们“叙永小站”。\b\n\b\n今后叙永大凡小事，我们都将点点滴滴悉数向您汇报，无论是好电影上映，还是寻访名小吃；不管是店铺有折扣，还是帅哥美女聚会搞活动。哪有新鲜有趣事，哪就有我们的存在。\b\n\b\n说好了就不许放手，乖，加了就不许删哟~~若爱，请深爱！哇哈哈哈哈~\b\n\b\n\b\n\b\nPS：对了！回复数字编码马上查询叙永资讯：\b\n\b\n1：电影上映资讯\b\n（或输入文字“电影”）\b\n\b\n2：车辆违章信息\b\n（或输入“川E00000”格式的车牌）\b\n\b\n3:输入 名称+号码，即可查询电话号码（例如：东方明珠 电话）\b\n赶快试试吧！\b\n\b\n（电话号码库目前还不是很充实，如有遗漏，请发消息告诉我们~）"""
            else:
                recv['MsgType'] = 'text'
                recv['Content'] = u"""我们已经收到了你的消息！可惜我们现在还不够聪明，暂时不能处理语音，图片，链接和地理位置信息，要不先和我们打字聊聊？等过段时间我们足够聪明了，再来语音聊？"""

    #以下为预留事件代码
    #        eventTpl="""<xml><ToUserName><![CDATA[%s]]></ToUserName>
    #            <FromUserName><![CDATA[%s]]></FromUserName>
    #            <CreateTime>%s</CreateTime>
    #            <MsgType><![CDATA[event]]></MsgType>
    #            <Event><![CDATA[EVENT]]></Event>
    #            <EventKey><![CDATA[EVENTKEY]]></EventKey>
    #            </xml>"""
            echostr = textTpl % (recv['FromUserName'], recv['ToUserName'],int(time.time()),recv['MsgType'],recv['Content'])
            return echostr
        if not mc:
            return (time.ctime())
        mc.set('is_test',time.ctime(),time=50)
        return mc.get('is_test')


    @expose('/login')
    def login(self):
        from uliweb.contrib.auth import login

        form = functions.get_form('auth.LoginForm')()

        if request.user:
            next = request.GET.get('next','/admin')
            if next:
                return redirect(next)

        if request.method == 'GET':
            form.next.data = request.GET.get('next', request.referrer or '/')
            return {'form':form, 'msg':''}
        if request.method == 'POST':
            flag = form.validate(request.params)
            if flag:
                f, d = functions.authenticate(username=form.username.data, password=form.password.data)
                if f:
                    request.session.remember = form.rememberme.data
                    login(form.username.data)
                    next = urllib.unquote(request.POST.get('next', '/admin'))
                    return redirect(next)
                else:
                    form.errors.update(d)
            msg = form.errors.get('_', '') or _('Login failed!')
            return {'msg':str(msg)}


    @expose('/register')
    def register(self):
        from uliweb.contrib.auth import create_user, login
        from uliweb.i18n import ugettext_lazy as _

        form = functions.get_form('RegisterForm')()

        if request.method == 'GET':
            form.next.data = request.GET.get('next', '/')
            return {'form':form, 'msg':''}
        if request.method == 'POST':
            flag = form.validate(request.params)
            if flag:
                f, d = create_user(username=form.username.data, password=form.password.data,email=form.email.data)
                if f:
                    #add auto login support 2012/03/23
                    login(d)
                    next = urllib.unquote(request.POST.get('next', '/'))
                    return redirect(next)
                else:
                    form.errors.update(d)

            msg = form.errors.get('_', '') or _('Register failed!')
            return {'form':form, 'msg':str(msg)}

    @expose('/ad')
    def ad(self):
        return {}


@expose('/admin')
class AdminView(object):
    def __init__(self):
        from uliweb.utils.generic import AddView,ListView,EditView
        self.PhoneNum = get_model('phonenumber')
        self.Tags = get_model('tags')
        self.AddView = AddView
        self.ListView = ListView
        self.EditView = EditView

    def __begin__(self):
        functions.require_login()
        if not functions.has_role(request.user, 'superuser'):
            error("你没有权限访问此页面")

    @expose('/admin')
    def index(self):
        return {}

    @expose('/admin/phonenumber')
    def phonenumber(self):
        def name(value, obj):
            return '<a href="/admin/phonenumber/%d">%s</a>' % (obj.id, value)

        fields_convert_map = {'name':name}
        view = self.ListView(self.PhoneNum,rows_per_page=500,fields_convert_map=fields_convert_map)
        return view.run()

    def add_number(self):
        def post_save(obj, data):
            tags_list = data['ot'].split(' ')
            tags_list.append(obj.name)
            for i in tags_list:
                if not i:
                    continue
                tag = self.Tags.filter(self.Tags.c.name == i).one()
                if not tag:
                    tag = self.Tags(name=i)
                    tag.save()
                obj.tag.add(tag)

        view = self.AddView(self.PhoneNum,
                    ok_url='/admin/phonenumber',post_save=post_save
                    )
        return view.run()

    def add_tag(self):
        view = self.AddView(self.Tags,
                    ok_url='/admin/phonenumber',
                    )
        return view.run()

    @expose('/admin/phonenumber/<id>')
    def edit_number(self,id):
        def post_save(obj, data):
            tags_list = data['ot'].split(' ')
            tags_list.append(obj.name)
            for i in tags_list:
                if not i:
                    continue
                tag = self.Tags.filter(self.Tags.c.name == i).one()
                if not tag:
                    tag = self.Tags(name=i)
                    tag.save()
                obj.tag.add(tag)

        obj = self.PhoneNum.get_or_notfound(int(id))
        view = self.EditView(self.PhoneNum, obj=obj,ok_url='/admin/phonenumber',post_save=post_save)
        return view.run()