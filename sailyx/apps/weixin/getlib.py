#coding=utf-8
from bs4 import BeautifulSoup as bs
import urllib,urllib2,cookielib,json


def qc(seq, idfun=None):
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def moviespider():
    url = 'http://theater.mtime.com/China_Sichuan_Province_Luzhou_XuYongXian/3527/'
    page = urllib2.urlopen(url)
    soup = bs(page)
    result = ''
    script = soup.findAll('script')[6].string.split("cinemaShowtimesScriptVariables = ", 1)[-1]

    #去掉文末的\r\n
    script = script[:-2]

    script2=script.replace('new Date("','"')
    script2 = script2.replace('")','"')
    data = json.loads(script2)
    moviesCount = len(data['movies'])
    showOther = {}
    showCount = len(data['showtimes'])

    for i in range(0,moviesCount):
        movieId = data['movies'][i]['movieId']
        showOther[movieId] = []


    for i in range(0,showCount):
        movieId = data['showtimes'][i]['movieId']
        showOther[movieId].append([data['showtimes'][i]['realtime'],data['showtimes'][i]['movieEndTime'],data['showtimes'][i]['price']])

    for i in range(0,moviesCount):
        movieId = data['movies'][i]['movieId']
        result += data['movies'][i]['movieTitleCn']
        result +='\b\n'
        result += u'评分:'
        result += str(data['movies'][i]['bigRating'])+'.'+str(data['movies'][i]['smallRating'])
        result +='  '
        result += data['movies'][i]['runtime']
        result +='\b\n'
        result += data['movies'][i]['property'].replace('/',' ')
        result +='\b\n'

        for x in showOther[movieId]:
            result += x[0][-8:-3]
            result +='  '
            result += x[2]+u'￥'
            result +='\b\n'
    return result


#   old movisspider 2014-08-11
#def moviespider():
#    url = 'http://theater.mtime.com/China_Sichuan_Province_Luzhou_XuYongXian/3527/'
#
#    page = urllib2.urlopen(url)
#    soup = bs(page)
#
#    original = soup.find_all(class_='table')
#    m_count = len(original)
#    movie_list = []
#    movie_name = []
#    movie_time = []
#    movie_price = []
#
#    for i in range(0,m_count):
#        name_temp = []
#        time_temp = []
#        price_temp = []
#
#        name_temp.append(original[i].find(class_='c_000').text)
#
#        for t in original[i].find_all('strong'):
#            time_temp.append(t.text)
#        time_temp=qc(time_temp)
#        for p in original[i].find_all('em'):
#            price_temp.append(p.text)
#
#        movie_name.extend(name_temp)
#        movie_time.append(time_temp)
#        movie_price.append(price_temp)
#
#    movie_list.append(movie_name)
#    movie_list.append(movie_time)
#    movie_list.append(movie_price)
#
#    return movie_list

def wzspider(cp):
    connect = True
    res = ''
    url = 'http://www.sclzjj.gov.cn/inquiry/Transgress.aspx?number=%E5%B7%9D' + cp[3:] + '&type=02'
    try:
        resp = urllib2.urlopen(url,timeout=3)
        res = resp.read()
    except urllib2.URLError:
        connect = False
        return res,connect
    except urllib2.HTTPError, error:
        connect = False
        return res,connect

    soup = bs(res)
    original = soup.find_all('td')
    content_list = []
    arg = [u'车牌号',u'车型',u'违章原因',u'违章时间',u'地点',u'违章代码',u'采集部门']
    arg_list = arg*(len(original)/7)
    for c in original:
        temp = c.text
        if c.get('width') != '80':
            temp = temp.split()
        content_list.append(temp)
    result = zip(arg_list,content_list)
    return result,connect

def weatherspider():
    today_url = 'http://www.weather.com.cn/weather1d/101271005.shtml'
    d2_url = 'http://www.weather.com.cn/weather2d/101271005.shtml'
    page1 = urllib2.urlopen(today_url)
    page2 = urllib2.urlopen(d2_url)
    soup1 = bs(page1)
    soup2 = bs(page2)
    title = soup1.strong.text
    post_date = soup1.h3.text

    today = []
    d2 = []

    for d in soup1.find_all(id='today'):
        today.append(d.get_text().strip().replace('\n\n\n',''))
    for w in soup2.find_all(id='2_3d'):
        d2.append(w.get_text().strip().replace('\n\n\n',''))

    result = zip(today,d2)
    return result

def psbc(psbcKey):
    bankCard = u'银行卡（Bank Card） 是商业银行等金融机构及邮政储汇机构向社会发行的，具有消费信用、转账结算、存取现金等全部或部分功能的信用支付工具。银行卡包括信用卡和借记卡两种。因为各种银行卡都是塑料制成的，又用于存取款和转帐支付，所以又称之为“塑料货币”。'
    creditCard = u'贷记卡（Credit card）：常称为信用卡，是指发卡银行给予持卡人一定的信用额度，持卡人可在信用额度内先消费，后还款的信用卡。它具有的特点：先消费后还款，享有免息缴款期，并设有最低还款额，客户出现透支可自主分期还款。客户需要向申请的银行交付一定数量的年费，各银行不相同。\b\n更多卡务信息请咨询邮储银行叙永支行：6222905，6236748，6722638'
    semiCreditCard = u'准贷记卡：是一种存款有息、刷卡消费以人民币结算的单币种单帐户信用卡，具有转账结算、存取现金、信用消费、网上银行交易等功能。当刷卡消费、取现帐户存款余额不足支付时，持卡人可在规定的有限信用额度内透支消费、取现，并收取一定的利息。不存在免息还款期。\b\n准贷记卡作为中国信用卡产业发展过程中的过渡产品正在逐步退出历史舞台，在我们现实生活中准贷记卡的使用量、使用意义都在逐步减小。\b\n更多卡务信息请咨询邮储银行叙永支行：6222905，6236748，6722638'
    eBank = u'电子银行业务是：商业银行等银行业金融机构利用面向社会公众开放的通讯通道或开放型公众网络，以及银行为特定自助服务设施或客户建立的专用网络，向客户提供的银行服务。主要包括网上银行、电话银行、手机银行、自助银行以及其他离柜业务。\b\n更多便捷信息请咨询邮储银行叙永支行：6222905，6236748，6722638'
    threeABank = u'网上银行又称网络银行、在线银行，是指银行利用Internet技术，通过Internet向客户提供开户、查询、对帐、行内转帐、跨行转账、信贷、网上证劵、投资理财等传统服务项目，使客户可以足不出户就能够安全便捷地管理活期和定期存款、支票、信用卡及个人投资等。可以说，网上银行是在Internet上的虚拟银行柜台。网上银行又被称为“3A银行”，因为它不受时间、空间限制，能够在任何时间(Anytime)、任何地点(Anywhere)、以任何方式(Anyway)为客户提供金融服务。\b\n更多便捷信息请咨询邮储银行叙永支行：6222905，6236748，6722638'
    appBank = u'手机银行是网上银行的延伸，也是继网上银行、电话银行之后又一种方便银行用户的金融业务服务方式，有贴身“电子钱包”之称，除了取款，几乎所有银行服务都可以在网上完成。它一方面延长了银行的服务时间，扩大了银行服务范围，另一方面无形地增加了许多银行经营业务网点，真正实现24小时全天候服务。\b\n更多贴心服务请咨询邮储银行叙永支行：6222905，6236748，6722638'
    phoneBank = u'它通过电话这种现代化的通信工具把用户与银行紧密相连，使用户不必去银行，无论何时何地，只要通过拨通电话银行的电话号码，就能够得到电话银行提供的其它服务（往来交易查询、转账汇款、利率查询等）\b\n更多贴心服务请咨询邮储银行叙永支行：6222905，6236748，6722638'
    demandDeposit = u'活期存款是一种不限存期，凭银行卡或存折及预留密码可在银行营业时间内通过柜面或通过银行自助设备随时存取现金的服务。\b\n人民币活期存款1元起存，外币活期存款起存金额为不低于人民币20元的等值外汇。\b\n更多贴心服务请咨询邮储银行叙永支行：6222905，6236748，6722638'
    moreDeposit = u'银行的一种存款，期限可以从3 个月到5年，10年以上不等。一般来说，存款期限越长，利率就越高。传统的定期存款除了有存单形式外，也有存折形式。存款方式有整存整取、零存整取、存本取息、整存零取。\b\n整存整取：是一种由客户选择存款期限，整笔存入，到期提取本息的一种定期储蓄。\b\n零存整取：是一种事先约定金额，逐月按约定金额存入，到期支取本息的定期储蓄。\b\n存本取息：是一种一次存入本金，分次支取利息，到期支取本金的定期储蓄。\b\n整存零取：是一种事先约定存期，整数金额一次存入，分期平均支取本金，到期支取利息的定期储蓄。\b\n更多贴心服务请咨询邮储银行叙永支行：6222905，6236748，6722638'
    interest = u'利息，从其形态上看，是货币所有者因为发出货币资金而从借款者手中获得的报酬；从另一方面看，它是借贷者使用货币资金必须支付的代价。利率表示一定时期内利息量与本金的比率，通常用百分比表示，按年计算则称为年利率。\b\n更多贴心服务请咨询邮储银行叙永支行：6222905，6236748，6722638'
    loans = u'贷款是银行或其他金融机构按一定利率和必须归还等条件出借货币资金的一种信用活动形式。广义的贷款指贷款、贴现 、透支等出贷资金的总称。银行通过贷款的方式将所集中的货币和货币资金投放出去，可以满足社会扩大再生产对补充资金的需要，促进经济的发展；同时，银行也可以由此取得贷款利息收入，增加银行自身的积累。\b\n更多贷款信息请咨询邮储银行叙永支行：6271371，6271456，6271116'
    microCredit = u'小额贷款（MicroCredit）是以个人或家庭为核心的经营类贷款，其主要的服务对象为广大工商个体户、小作坊、小业主。贷款的金额一般为1000元以上，1000万元以下。小额贷款在中国：主要是服务于三农、中小企业，有效地解决了三农、中小企业融资难的问题。特点是程序简单、放贷过程快、手续简便，还款方式灵活，贷款范围较广。\b\n更多贷款信息请咨询邮储银行叙永支行：6271371，6271456，6271116'
    mortgage = u'抵押贷款指借款者以一定的抵押品作为物品保证向银行取得的贷款，抵押物一般为房产、物资或符合条件的动产等。特点是放贷金额大、授信期限长、贷款品种丰富，手续需完备。\b\n更多贷款信息请咨询邮储银行叙永支行：6271371，6271456，6271116'
    smallLoans = u'中小企业贷款指银行向小企业法定代表人或控股股东（社会自然人，以下简称借款人）发放的，用于补充企业流动性资金周转等合法指定用途的贷款。\b\n更多贷款信息请咨询邮储银行叙永支行：6271371，6271456，6271116'
    financing = u'投资理财是指投资者通过合理安排资金，运用诸如储蓄、银行理财产品、债券、基金、股票、期货、外汇、房地产、保险以及黄金等投资理财工具对个人、家庭和企事业单位资产进行管理和分配，达到保值增值的目的，从而加速资产的增长。投资有风险，请谨慎购买。\b\n更多投资理财信息请咨询邮储银行叙永支行：6222905，6236748，6722638'

    keyTable = {u'银行卡':bankCard,u'信用卡':creditCard,u'贷记卡':creditCard,u'准贷记卡':semiCreditCard,u'电子银行':eBank,u'网上银行':threeABank,u'网银':threeABank,u'手机银行':appBank,u'电话银行':phoneBank,u'活期存款':demandDeposit,u'活期':demandDeposit,u'定期存款':moreDeposit,u'整存整取':moreDeposit,u'零存整取':moreDeposit,u'存本取息':moreDeposit,u'整存零取':moreDeposit,u'利息':interest,u'利率':interest,u'贷款':loans,u'小额贷款':microCredit,u'信用贷款':microCredit,u'担保贷款':microCredit,u'抵押贷款':mortgage,u'房产贷款':mortgage,u'中小企业贷款':smallLoans,u'理财':financing,u'投资':financing}

    if keyTable.has_key(psbcKey):
        return keyTable[psbcKey]
    return False
