import random,time
import os,sys
import platform as pf
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from time import sleep
import shutil
# print("###"+os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# print("###"+os.path.abspath(os.path.dirname(os.getcwd())))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))
from loguru import logger
from pywebio.input import input, FLOAT,NUMBER,input_group,select, textarea,file_upload,checkbox,radio,actions
import pywebio.pin as pin
from pywebio.output import close_popup, output, put_file, put_html, put_image, put_markdown, put_text,popup,put_link,put_code,put_row,put_processbar,set_processbar,put_error,put_warning,toast,put_grid,put_button,put_table,use_scope,span,clear,remove,get_scope
from pywebio import start_server,session,platform

import pywebio.output as output
import pywebio.input as inputs
import pywebio.pin as pin
from pywebio.session import hold

from multiprocessing import Process
import decimal,websockets,asyncio
import json
from functools import partial
from core.bladeTest.interactive_blade import oneCheck,onePageInput
from core.bladeTest.interactive_jmeter import jmeterScriptGen,jmeterRule,jmeterDownload,jmeterDeploy,jmeterRun
from core.bladeTest.interactive_testUtil import kafkaListener,mqttListener,toolGeter
from core.bladeTest.interactive_xmind import uploadXmind
import pyttsx3

# def clearAndCall(func):
#     clear('content')
#     use_scope('main',clear=True)
#     func()
#     use_scope('main',clear=True)


# def myapp3():
#     try:
#         put_table([
#             ['功能清单'],
#             ['功能相关',put_button("xmind转excel", onclick=lambda: uploadXmind())],
#             ['高可用(主机、docker)久未维护',put_button("混沌测试-交互式", onclick=lambda: oneCheck()),put_button("混沌测试-直输式", onclick=lambda: onePageInput())],
#             # put_button("xmind转excel", onclick=lambda: uploadXmind())],
#             # ['高可用(主机、docker)久未维护',put_button("混沌测试-交互式", onclick=lambda: oneCheck()),put_button("混沌测试-直输式", onclick=lambda: onePageInput())],
#             ['自动化相关',put_button("jmeter自动化", onclick=lambda: jmeterScriptGen())],
#             ['数据链路检查',put_button("kafka发送", onclick=lambda: kafkaSender()),put_button("kafka接收", onclick=lambda: kafkaGeter()),put_button("mqtt操作", onclick=lambda: mqttListener())],
#             ['测试辅助',put_button("测试数据",onclick=lambda: myFackData()),put_button("杂项",onclick=lambda: others())]
            
#         ])

#     except Exception as e:
#         toast(e)



@use_scope(name='main',clear=True,create_scope=True)
def myapp2():
    try:
        session.set_env(title='testToolKit')
        
        put_table([
            ['功能相关',span('高可用(主机、docker)久未维护',col=2),'自动化相关',span('数据链路检查',col=2),'测试辅助','其他'],
            [put_button("xmind转excel", onclick=lambda: uploadXmind()),
            put_button("混沌测试-交互式", onclick=lambda: oneCheck()),
            put_button("混沌测试-直输式", onclick=lambda: onePageInput()),
            put_button("jmeter自动化", onclick=lambda: jmeterScriptGen()),
            put_button("kafka操作", onclick=lambda: kafkaListener()),
            put_button("mqtt操作", onclick=lambda: mqttListener()),
            put_button("测试数据",onclick=lambda: toolGeter()),
            put_button("杂项",onclick=lambda: others())
            ]
        ])

    except Exception as e:
        # toast(e)
        output.popup(title="error",content=output.put_text(e))

# def myapp():
#     '''
#     this main function for enter the whole functions of pywebio
#     :return:
#     '''
#     session.set_env(title='testToolKit')

#     select_type = select("选择你要做的操作:",["xmind转excel","混沌测试-交互式","混沌测试-直接输入(推荐)","jmeter脚本生成","假数据构造","kafka操作","mqtt操作"])
#     try:
#         if select_type=="xmind转excel":
#             uploadXmind()
#         elif select_type=="混沌测试-交互式":
#             oneCheck()
#         elif select_type=="混沌测试-直接输入(推荐)":
#             onePageInput()
#         elif select_type=="jmeter脚本生成":
#             jmeterScriptGen()
#         elif select_type=="假数据构造":
#             myFackData()
#         elif select_type=="kafka操作":
#             kafkaListener()
#         elif select_type=="mqtt操作":
#             mqttListener()
#     except Exception as e:
#         put_text(e)


def others():
    session.set_env(title='testTools')
    clear('content')

    select_type = select("选择服务:",["播放语音","钉钉群组提醒测试","待定"])
    if select_type=="播放语音":
        userPath=os.path.expanduser('~')
        reportDir=userPath+os.sep+"report"
        if not os.path.exists(reportDir):
            os.mkdir(reportDir)

        voiceData=textarea('请粘贴文字到此处',rows=15)
        print(voiceData)

        from core.thirdPartInterface import mp3gen
        mp3gen(voiceData,reportDir+os.sep+"voice.mp3")

        libpath=sys.path
        print(f'libpath: {libpath}')
        for one in libpath:
            if one.endswith("site-packages"):
                location1Prefx=one
                print(f"location1Prefx: {location1Prefx}")
        mp3HtmlFileLocation=location1Prefx+os.sep+"core"+os.sep+"bladeTest"+os.sep+"templates"+os.sep+"play.html"

        if os.path.exists(reportDir+os.sep+"play.html"):
            os.remove(reportDir+os.sep+"play.html")
        shutil.move(mp3HtmlFileLocation, reportDir)
        put_link('点击播放语音',url='/static/play.html',new_window=True)
    elif select_type=="钉钉群组提醒测试":
        from core.thirdPartInterface import testDingGroupAlert
        put_warning("请期待")








def run(portNum=8999):
    '''
    running application by command
    :param portNum:
    :return:
    '''
    userPath=os.path.expanduser('~')
    reportDir=userPath+os.sep+"report"
    if not os.path.exists(reportDir):
        os.mkdir(reportDir)
    # shutil.rmtree(reportDir)
    start_server(myapp2, port=portNum,static_dir=reportDir,cdn=False,static_hash_cache=False,reconnect_timeout=3600,max_payload_size='500M')
    # start_server(myapp, port=portNum)





def test():
    output.put_markdown('# 输入')
    pin.put_input('one',label='请输入第一个：',type=input.NUMBER,value=3)
    pin.put_input('two',label='请输入第二个：',type=input.NUMBER,value=5)

    def call():
        one=pin.pin.one
        two=pin.pin.two
        ret=int(one)+int(two)
        # output.put_markdown(f'{one} + {two} = {ret}')
        output.toast(content=f'{one} + {two} = {ret}',color='grey')

    output.put_button(['提交'], onclick=lambda :call())
    hold()



if __name__ == '__main__':
    userPath=os.path.expanduser('~')
    reportDir=userPath+os.sep+"report"
    if not os.path.exists(reportDir):
        os.mkdir(reportDir)
    # shutil.rmtree(reportDir)
    start_server(myapp2, port=8999,debug=True,static_dir=reportDir,cdn=False,static_hash_cache=False,reconnect_timeout=3600,max_payload_size='500M')
    # start_server(myapp3,port=8080,debug=True,static_dir=reportDir,cdn=False,reconnect_timeout=3600,max_payload_size='500M',static_hash_cache=False)
    # myapp2()
    # jmeterRun()
    # mqttListener()
    # print(session.info["server_host"].split(":")[0])
    # kafkaListener()
    # myFackData()
