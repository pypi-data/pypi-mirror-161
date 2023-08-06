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
    :return:
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







from functools import partial
def filterPrint(oriStr,tarStr):
    if tarStr in oriStr:
        put_text(getDateTime()+" "+oriStr)

def noFilterPrint(oriStr):
    put_text(getDateTime()+" "+oriStr)




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
        clear('content')




def dataTransfer():
    pass
def kafkaTransfer():
    output.put_markdown("## 请输入需要转发的kafka信息")
    pin.put_input(name='host',label='源主机：端口')
    pin.put_input(name='topic',label='源主题')
    pin.put_input(name='user',label='源用户')
    pin.put_input(name='passwd',label='源密码')
    output.put_markdown("-----------------------------")
    pin.put_input(name='host2',label='目的主机：端口')
    pin.put_input(name='topic2',label='目的主题')
    pin.put_input(name='user2',label='目的用户')
    pin.put_input(name='passwd2',label='目的密码')

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

def mqttTransfer():
    output.put_markdown("## 请输入需要转发的kafka信息")
    pin.put_input(name='host',label='源主机')
    pin.put_input(name='port',lable="源端口")
    pin.put_input(name='topic',label='源主题')
    pin.put_input(name='user',label='源用户')
    pin.put_input(name='passwd',label='源密码')
    output.put_markdown("-----------------------------")
    pin.put_input(name='host2',label='目的主机')
    pin.put_input(name='port',lable="目的端口")
    pin.put_input(name='topic2',label='目的主题')
    pin.put_input(name='user2',label='目的用户')
    pin.put_input(name='passwd2',label='目的密码')

    def getValueAndCall():
        host=pin.pin.host
        port=pin.pin.port
        topic=pin.pin.topic
        user=pin.pin.user
        passwd=pin.pin.passwd

        host2=pin.pin.host2
        port2=pin.pin.port2
        topic2=pin.pin.topic2
        user2=pin.pin.user2
        passwd2=pin.pin.passwd2

        NormalMqttGetter(host=host, port=port, topic=topic,user=user,passwd=passwd).getClient(partial(filterPrint, tarStr=data['filter']))

    output.put_button(label='提交', onclick=lambda :getValueAndCall())



def timeStampGetter():
    output.put_markdown("# 当前时间：")
    output.put_markdown("- "+str(getDateTime()))
    output.put_markdown("# 当前时间戳：")
    output.put_markdown("- "+str(getTimeStamp()))
    output.put_markdown("## 时间转时间戳：")
    pin.put_input(name='curTime',label='请输入格式化时间',value="请输入格式化时间：2022-01-01 23:59:59.999")
    def time2stamp():
        curTime=pin.pin.curTime
        output.put_text(formatStr2Timestamp(curTime))
    output.put_button(label='确定', onclick=lambda :time2stamp())


    output.put_markdown("## 时间戳转时间：")
    pin.put_input(name='timeStamp',label='请输入时间戳',value="请输入13位时间戳，不够时后三位可写位0")
    def stamp2time():
        timeStamp=pin.pin.timeStamp
        output.put_text(timeStampStr2FormatTime(timeStamp))
    output.put_button(label='确定', onclick=lambda :stamp2time())
    







if __name__ == '__main__':
    start_server(timeStampGetter,port=8080,debug=True,cdn=False,auto_open_webbrowser=True)


