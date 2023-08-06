import random,time
import os,sys
import platform as pf
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from time import sleep
import shutil

from loguru import logger
from pywebio.input import FLOAT,NUMBER,input_group,select, textarea,file_upload,checkbox,radio,actions
from pywebio.output import close_popup, output, put_file, put_html, put_image, put_markdown, put_text,popup,put_link,put_code,put_row,put_processbar,set_processbar,put_error,put_warning,toast,put_grid,put_button,put_table,use_scope,span,clear,remove
from pywebio import start_server,session,platform
from core.bladeTest.main import RemoteRunner,generateHtmlReport,running
from core.jmeterTool.swagger2jmeter import swagger2jmeter
from core.jmeterTool.har2jmeter import har2jmeter
from core.xmind2excel import makeCase
from core.utils import CFacker,getDateTime,parseJmeterXml,getTimeStamp,getDateTime,formatStr2Timestamp,timeStampStr2FormatTime
from core.mqttUtil import NormalMqttGetter,NormalMqttSender
from core.kafkaUtil import general_sender,continue_orderMsg,general_orderMsg,general_orderMsgWithFilter,kafkaFetchServerWithFilter,kafkaFetchServer
from functools import partial
from multiprocessing import Process
import decimal,websockets,asyncio
import json
from functools import partial

import pywebio.output as output
import pywebio.input as inputs
import pywebio.pin as pin
from pywebio.session import hold


@use_scope('content',clear=True)
def toolGeter():
    session.set_env(title='testToolKit')
    clear('content')
    select_type = select("选择你要做的操作:",["时间戳相关","数据构造"])
    if select_type=="时间戳相关":
        timeStampGetter()
    elif select_type=="数据构造":
        myFackData()



def timeStampGetter():
    output.put_markdown("# 当前时间：")
    output.put_markdown("- "+str(getDateTime()))
    output.put_markdown("# 当前时间戳：")
    output.put_markdown("- "+str(getTimeStamp()))
    output.put_markdown("## 时间转时间戳：")
    pin.put_input(name='curTime',label='请输入格式化时间',value="请输入格式化时间：2022-01-01 23:59:59.999")
    def time2stamp():
        curTime=pin.pin.curTime
        output.popup(title="时间戳为：",content=put_text(formatStr2Timestamp(curTime)))
    output.put_button(label='确定', onclick=lambda :time2stamp())


    output.put_markdown("## 时间戳转时间：")
    pin.put_input(name='timeStamp',label='请输入时间戳',value="请输入13位时间戳，不够时后三位可写位0")
    def stamp2time():
        timeStamp=pin.pin.timeStamp
        output.popup(title="时间为：",content=put_text(timeStampStr2FormatTime(timeStamp)))
    output.put_button(label='确定', onclick=lambda :stamp2time())




class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)

@use_scope('content',clear=True)
def myFackData():
    '''
    generate the fake data by using this app, when you test
    :return:
    '''
    
    try:
        session.set_env(title='testToolKit')
        clear('content')
        all_options={
        "city_suffix":"市，县",
        "country":"国家",
        "country_code":"国家编码",
        "district":"区",
        "latitude":"地理坐标(纬度)",
        "longitude":"地理坐标(经度)",
        "postcode":"邮编",
        "province":"省份 (zh_TW没有此方法)",
        "address":"详细地址",
        "street_address":"街道地址",
        "street_name":"街道名",
        "street_suffix":"街、路",
        "ssn":"生成身份证号",
        "bs":"随机公司服务名",
        "company":"随机公司名（长）",
        "company_prefix":"随机公司名（短）",
        "company_suffix":"公司性质",
        "credit_card_expire":"随机信用卡到期日",
        "credit_card_full":"生成完整信用卡信息",
        "credit_card_number":"信用卡号",
        "credit_card_provider":"信用卡类型",
        "credit_card_security_code":"信用卡安全码",
        "job":"随机职位",
        "first_name":"名",
        "first_name_female":"女性名",
        "first_name_male":"男性名",
        "first_romanized_name":"罗马名",
        "last_name":"姓",
        "last_name_female":"女姓",
        "last_name_male":"男姓",
        "last_romanized_name":"随机",
        "name":"随机生成全名",
        "name_female":"男性全名",
        "name_male":"女性全名",
        "romanized_name":"罗马名",
        "msisdn":"移动台国际用户识别码，即移动用户的ISDN号码",
        "phone_number":"随机生成手机号",
        "phonenumber_prefix":"随机生成手机号段",
        "ascii_company_email":"随机ASCII公司邮箱名",
        "ascii_email":"随机ASCII邮箱",
        "ascii_free_email":"二进制免费邮件",
        "ascii_safe_email":"二进制安全邮件",
        "company_email":"公司邮件",
        "email":"电子邮件",
        "free_email":"免费电子邮件",
        "free_email_domain":"免费电子邮件域名",
        "safe_email":"安全邮箱",
        "domain_name":"生成域名",
        "domain_word":"域词(即，不包含后缀)",
        "ipv4":"随机IP4地址",
        "ipv6":"随机IP6地址",
        "mac_address":"随机MAC地址",
        "tld":"网址域名后缀(.com,.net.cn,等等，不包括.)",
        "uri":"随机URI地址",
        "uri_extension":"网址文件后缀",
        "uri_page":"网址文件（不包含后缀）",
        "uri_path":"网址文件路径（不包含文件名）",
        "url":"随机URL地址",
        "user_name":"随机用户名",
        "image_url":"随机URL地址",
        "chrome":"随机生成Chrome的浏览器user_agent信息",
        "firefox":"随机生成FireFox的浏览器user_agent信息",
        "internet_explorer":"随机生成IE的浏览器user_agent信息",
        "opera":"随机生成Opera的浏览器user_agent信息",
        "safari":"随机生成Safari的浏览器user_agent信息",
        "linux_platform_token":"随机Linux信息",
        "user_agent":"随机user_agent信息",
        "file_extension":"随机文件扩展名",
        "file_name":"随机文件名（包含扩展名，不包含路径）",
        "file_path":"随机文件路径（包含文件名，扩展名）",
        "mime_type":"随机mime Type",
        "numerify":"三位随机数字",
        "random_digit":"0~9随机数",
        "random_digit_not_null":"1~9的随机数",
        "random_int":"随机数字，默认0~9999，可以通过设置min,max来设置",
        "random_number":"随机数字，参数digits设置生成的数字位数",
        "pyfloat":"left_digits=5 #生成的整数位数, right_digits=2 #生成的小数位数, positive=True #是否只有正数",
        "pyint":"随机Int数字（参考random_int=参数）",
        "pydecimal":"随机Decimal数字（参考pyfloat参数）",
        "pystr":"随机字符串",
        "random_element":"随机字母",
        "random_letter":"随机字母",
        "paragraph":"随机生成一个段落",
        "paragraphs":"随机生成多个段落，通过参数nb来控制段落数，返回数组",
        "sentence":"随机生成一句话",
        "sentences":"随机生成多句话，与段落类似",
        "text":"随机生成一篇文章（不要幻想着人工智能了，至今没完全看懂一句话是什么意思）",
        "word":"随机生成词语",
        "words":"随机生成多个词语，用法与段落，句子，类似",
        "binary":"随机生成二进制编码",
        "boolean":"True/False",
        "language_code":"随机生成两位语言编码",
        "locale":"随机生成语言/国际 信息",
        "md5":"随机生成MD5",
        "null_boolean":"NULL/True/False",
        "password":"随机生成密码,可选参数：length：密码长度；special_chars：是否能使用特殊字符；digits：是否包含数字；upper_case：是否包含大写字母；lower_case：是否包含小写字母",
        "sha1":"随机SHA1",
        "sha256":"随机SHA256",
        "uuid4":"随机UUID",
        "am_pm":"AM/PM",
        "century":"随机世纪",
        "date":"随机日期",
        "date_between":"随机生成指定范围内日期，参数：start_date，end_date取值：具体日期或者today,-30d,-30y类似",
        "date_between_dates":"随机生成指定范围内日期，用法同上",
        "date_object":"随机生产从1970-1-1到指定日期的随机日期。",
        "date_this_month":"当月",
        "date_this_year":"当年",
        "date_time":"随机生成指定时间（1970年1月1日至今）",
        "date_time_ad":"生成公元1年到现在的随机时间",
        "date_time_between":"用法同dates",
        "future_date":"未来日期",
        "future_datetime":"未来时间",
        "month":"随机月份",
        "month_name":"随机月份（英文）",
        "past_date":"随机生成已经过去的日期",
        "past_datetime":"随机生成已经过去的时间",
        "time":"随机24小时时间",
        "time_object":"随机24小时时间，time对象",
        "time_series":"随机TimeSeries对象",
        "timezone":"随机时区",
        "unix_time":"随机Unix时间",
        "year":"随机年份",
        "profile":"随机生成档案信息",
        "simple_profile":"随机生成简单档案信息",
        "currency_code":"货币编码",
        "color_name":"随机颜色名",
        "hex_color":"随机HEX颜色",
        "rgb_color":"随机RGB颜色",
        "safe_color_name":"随机安全色名",
        "safe_hex_color":"随机安全HEX颜色",
        "isbn10":"随机ISBN(10位)",
        "isbn13":"随机ISBN(13位)",
        "lexify":"替换所有问号?带有随机字母的事件"
        }
        
        num=inputs.input("生成几组数据，默认是1组", type=NUMBER, value=1)
        # print(f'num is {num}')
        myformat=inputs.radio(label='选择生成数据格式：支持csv,json',options=['csv','json'],value=['json'])
        # print(f'format is {myformat}')
        
        choose=inputs.checkbox(label='从下列选项中，选择你想生成的数据：',options=all_options.values())
        
        # put_row([input('自定义键值：'),checkbox(options=[''])])
        allDict={}
        for i in range(0,num):
            restDict={}
            for one in choose:
                funcName=list(all_options.keys())[list(all_options.values()).index(one)]
                restDict[one]=CFacker().get_it(funcName)
            allDict[i]=restDict
        
        # put_text(allDict)
        
        if myformat=='json':
            
            output.put_code(json.dumps(allDict,cls=DecimalEncoder, indent=4,ensure_ascii=False), language='json',rows=20) 
        elif myformat=='csv':
            
            outStr=""
            for k,v in allDict.items():
                for vv in v.values():
                    # print(f"vv {vv}")
                    outStr=outStr+str(vv)+","
                outStr=outStr+"\n"
                
            output.put_text(outStr) 
    except Exception as e:
        output.popup(title="error",content=output.put_text(e))
        clear('content')


def kafkaSender():
    output.put_markdown("## 请输入kafka连接信息")
    pin.put_input(name='host',label='主机：端口')
    pin.put_input(name='topic',label='主题')
    pin.put_textarea(name='msg',label='消息',rows=10)
    pin.put_input(name='interval',label='发送间隔',value=0)
    def getValueAndCall():
        host=pin.pin.host
        topic=pin.pin.topic
        msg=pin.pin.msg
        interval=int(pin.pin.interval)
        
        if interval==0:
            general_sender(topic=topic,serverAndPort=host,message=msg)
            output.toast(content=f"发送成功: {host} \n {topic} \n {msg}")
        elif interval>0:
            while True:
                general_sender(topic=topic,serverAndPort=host,message=msg)
                output.toast(content=f"发送成功: {host} \n {topic} \n {msg}")
                sleep(int(interval))

    output.put_button(label='提交', onclick=lambda :getValueAndCall())


def kafkaGeter():
    put_text("json过滤如：data.deviceId")
    data = input_group("kafka连接配置", [
        inputs.input("kafka topic，必填", name="topic",value='testTopic'),
        inputs.input("kafka 地址，如ip:port，必填", name="address",value='192.168.xxx.xxx:9092'),
        inputs.input("过滤方式，仅支持填json或regx，非必填", name="filter",value='json'),
        inputs.input("过滤表达式，json使用jmeshpath方式，regx采用abc(.*)bbb的方式，非必填", name="pattern",value="payload.name"),
        inputs.input("过滤后比对关键字，过滤后的值是否等于输入的值，非必填", name="key",value="status"),
    ])
            
    for one in continue_orderMsg(data['topic'], data['address'], data['filter'], data['pattern'], data['key']):
        for a in one:
            if a is not None:
                put_text(f"{getDateTime()} : {data['topic']} --> {a}")

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


@use_scope('content',clear=True)
def kafkaListener():
    '''
    to send kafka message or listener the kafka topic
    
    '''
    try:
        session.set_env(title='testTools')
        clear('content')
        select_type = select("选择kafka操作:",["kafka发送消息","kafka持续接收消息","kafka消息转发"])

        if select_type=="kafka发送消息":
            kafkaSender()
        elif select_type=="kafka持续接收消息":
            kafkaGeter()
        elif select_type=="kafka消息转发":
            kafkaTransfer()
    except Exception as e:
        output.popup(title="error",content=put_text(e))
        clear('content')







def mqttSender():
    output.put_markdown("## 请输入mqtt连接信息")
    pin.put_input(name='host',label='mqtt主机，必填')
    pin.put_input(name='port',label='mqtt端口，必填（整数）')
    pin.put_input(name='topic',label='mqtt topic，必填')
    pin.put_input(name='user',label='mqtt 用户')
    pin.put_input(name='passwd',label='mqtt 密码')
    # pin.put_input(name='filter',label='mqtt 消息过滤字段')
    pin.put_textarea(name='msg',label='消息',rows=10)
    pin.put_input(name='interval',label='发送间隔',value=0)
    def getValueAndCall():
        host=pin.pin.host
        port=int(pin.pin.port)
        topic=pin.pin.topic
        user=pin.pin.user
        passwd=pin.pin.passwd
        msg=pin.pin.msg
        interval=int(pin.pin.interval)
        # myfilter=pin.pin.filter
        
        if interval==0:
            NormalMqttSender(host=host, port=port, topic=topic,user=user,passwd=passwd).getClient(msg)
            output.toast(content=f"发送成功: {host} \n {topic} \n {msg}")
        elif interval>0:
            while True:
                NormalMqttSender(host=host, port=port, topic=topic,user=user,passwd=passwd).getClient(msg)
                output.toast(content=f"发送成功: {host} \n {topic} \n {msg}")
                sleep(interval)
    output.put_button(label='提交', onclick=lambda :getValueAndCall())


def mqttGeter():
    data = input_group("mqtt信息",[
        inputs.input("mqtt主机，必填", name="host"),
        inputs.input("mqtt端口，必填（整数）", name="port"),
        inputs.input("mqtt topic，必填",name="topic"),
        inputs.input("mqtt用户", name="user"),
        inputs.input("mqtt密码", name="passwd"),
        inputs.input("消息包含", name="filter"),
                ])
            # put_button(label=f"{data['host']}:{data['port']}-{data['topic']}-{data['user']}:{data['passwd']}", onclick=NormalMqttGetter().close(client))
    if data['filter']=="" or data['filter']==None:
        NormalMqttGetter(host=data['host'], port=int(data['port']), topic=data['topic'],user=data['user'],passwd=data['passwd']).getClient(partial(filterPrint, tarStr=data['filter']))
    NormalMqttGetter(host=data['host'], port=int(data['port']), topic=data['topic'],user=data['user'],passwd=data['passwd']).getClient(noFilterPrint)




@use_scope('content',clear=True)
def mqttListener():
    try:
        session.set_env(title='testTools')
        clear('content')

        # select_type = select("选择mqtt服务:",["自定义发送服务","自定义接收服务","本地固定服务(待定)"])
        select_type = select("选择mqtt服务:",["自定义发送服务","自定义接收服务","本地固定服务(待定)","MQTT消息转发"])
        if select_type=="自定义接收服务":
            mqttGeter()
        elif select_type=="自定义发送服务":
            mqttSender()
        elif select_type == "本地固定服务(待定)":
            put_text('未暴露')
        elif select_type=="MQTT消息转发":
            mqttTransfer()
        
    except Exception as e:
        output.popup(title="error",content=put_text(e))
        
def kafkaTransfer():
    output.put_markdown("## 请输入需要转发的kafka信息")
    pin.put_input(name='host',label='源主机：端口')
    pin.put_input(name='topic',label='源主题')
    pin.put_input(name='user',label='源用户,非必填')
    pin.put_input(name='passwd',label='源密码,非必填')
    output.put_markdown("-----------------------------")
    pin.put_input(name='host2',label='目的主机：端口')
    pin.put_input(name='topic2',label='目的主题')
    pin.put_input(name='user2',label='目的用户,非必填')
    pin.put_input(name='passwd2',label='目的密码,非必填')

    def getValueAndCall():
        host=pin.pin.host
        topic=pin.pin.topic
        user=pin.pin.user
        passwd=pin.pin.passwd

        host2=pin.pin.host2
        topic2=pin.pin.topic2
        user2=pin.pin.user2
        passwd2=pin.pin.passwd2

        for one in continue_orderMsg(topic=topic, serverAndPort=host,flag="", pattern="", key=""):
            for msg in one:
                output.toast(content=msg)
                general_sender(topic=topic2,serverAndPort=host2,message=msg)

    output.put_button(label='提交', onclick=lambda :getValueAndCall())




from functools import partial
def filterPrint(oriStr,tarStr):
    if tarStr in oriStr:
        put_text(getDateTime()+" "+oriStr)

def filterSender(oriStr,tarStr,origStr,destStr,host,port,user,passwd,topic):
    if tarStr in oriStr:
        newStr=oriStr.replace(origStr,destStr)
        output.toast(content=newStr)
        NormalMqttSender(host=host,port=port,user=user,passwd=passwd,topic=topic).getClient(msg=newStr)
        

def noFilterPrint(oriStr):
    put_text(getDateTime()+" "+oriStr)

def mqttTransfer():
    output.put_markdown("## 请输入需要转发的，源MQTT信息")
    pin.put_input(name='host',label='源主机')
    pin.put_input(name='port',label="源端口")
    pin.put_input(name='topic',label='源主题')
    pin.put_input(name='user',label='源用户')
    pin.put_input(name='passwd',label='源密码')
    pin.put_input(name='filter',label='包含次字符串才被转发',value=None)
    output.put_markdown("## 请输入需要转发到的，目的MQTT信息")
    pin.put_input(name='host2',label='目的主机')
    pin.put_input(name='port2',label="目的端口")
    pin.put_input(name='topic2',label='目的主题')
    pin.put_input(name='user2',label='目的用户')
    pin.put_input(name='passwd2',label='目的密码')
    pin.put_input(name='origStr',label='转发时查找字符串',value=None)
    pin.put_input(name='destStr',label='转发时替换字符串',value=None)

    def getValueAndCall():
        host=pin.pin.host
        port=int(pin.pin.port)
        topic=pin.pin.topic
        user=pin.pin.user
        passwd=pin.pin.passwd
        myfilter=pin.pin.filter

        host2=pin.pin.host2
        port2=int(pin.pin.port2)
        topic2=pin.pin.topic2
        user2=pin.pin.user2
        passwd2=pin.pin.passwd2
        myOrig=pin.pin.origStr
        myDest=pin.pin.destStr

        NormalMqttGetter(host=host, port=port, topic=topic,user=user,passwd=passwd).getClient(partial(filterSender,tarStr=myfilter,origStr=myOrig,destStr=myDest,host=host2,port=port2,user=user2,passwd=passwd2,topic=topic2))

    output.put_button(label='提交', onclick=lambda :getValueAndCall())


if __name__ == '__main__':
    start_server(mqttListener,port=8999,debug=True,cdn=False,auto_open_webbrowser=True)


