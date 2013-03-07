#coding=utf-8
import hashlib,time,pylibmc
from lxml import etree
from uliweb import expose, functions
from get_movie import moviespider

token = ''#请自行填写你的微信taken
mc = pylibmc.Client()


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

@expose('/test')
def test():
    if mc.get('movie_list'):
        return mc.get('movie_list')
    content = moviespider()
    if not content[0]:
        return (u'哎哟~今天电影院还没发布电影信息~稍等会再来吧。')
    s = ''
    for i in range(0,len(content[0])):
        s+=''.join(content[0][i])
        s+='\b\n'
        s+=',    '.join(content[1][i])
        s+='\b\n'
        s+=',    '.join(content[2][i])
        s+='\b\n'
    mc.set('movie_list',s,time=3600)
    return (mc.get('movie_list'))

    

@expose('/')
def index():
    if mc.get('is_test'):
        return mc.get('is_test')
    if request.method == 'GET' and request.values:
        echostr = validate(request.values)
        if echostr:
            return echostr
    if request.method == 'POST':
#        soup = BeautifulSoup(request.values)
        data = request.data
        root = etree.fromstring(data)
        child = list(root)
        recv = {}
        for i in child:
            recv[i.tag] = i.text
        is_movie = u'电影'
        is_welcome = 'Hello2BizUser'
        if is_movie in recv['Content']:
            recv['Content'] = test()
        elif is_welcome == recv['Content']:
            recv['Content'] = u"""欢迎你加入哟~~"""
        else:
            recv['Content'] = u'好啦好啦，收到您的消息啦。稍等一会，我们待会就回复你哟~'

        textTpl = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            <FuncFlag>0</FuncFlag>
        </xml>"""
        
        echostr = textTpl % (recv['FromUserName'], recv['ToUserName'],int(time.time()),recv['MsgType'],recv['Content'])
        return echostr
    mc.set('is_test',time.ctime(),time=50)
    return mc.get('is_test')