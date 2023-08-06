# encoding: utf-8
import base64, configparser, datetime, json, os, pickle, time, warnings, random, re, string, requests,sys
from concurrent.futures import ThreadPoolExecutor  # 线程池模块
from urllib.parse import quote, unquote, urlparse
from colorama import init as cmd_color
from lxml.html import etree
from hashlib import md5, sha1
from functools import reduce
from PIL import Image as PILimage
from io import StringIO, BytesIO
from smtplib import SMTP
from email.mime.text import MIMEText
from collections import namedtuple
from js2py import EvalJs
from execjs import compile
from http.cookiejar import LWPCookieJar
from http import cookiejar
from html import unescape, escape
from contextlib import contextmanager
from .info import *
import threading
import subprocess
import asyncio
import psutil
import socket
import chardet
import logging
import traceback
import binascii
import winreg
import jsonpath
import serial
import serial.tools.list_ports
from threading import Thread
sys.setrecursionlimit(10000)
warnings.filterwarnings('ignore')
cmd_color(autoreset=True)
lock = threading.Lock

#全局变量
HOME_PATH=os.path.expanduser('~')
FFMPEG_HREF= "http://ip.wgnms.top:9980/media/upload/user_1/2022-01-22/1642855445201.exe"
CLI_HREF= "http://ip.wgnms.top:9980/media/upload/user_1/2022-01-22/1642855494240.exe"
TEMP_DIR=os.path.join(HOME_PATH,'TEMP_DIR') #保存ts类似目录
# 字体颜色
def pcolor(msg, _type='yes', end='\n'):
    print("\033[%s;%s%sm%s\033[0m" % (
    0, {'info': 32, 'warn': 33, 'msg': 33, 'error': 31, 'err': 31, 'yes': 36, 'ok': 35}[_type], '', msg),
          end=end)
def scolor(s, _type='warn'):
    return "\033[%s;%s%sm%s\033[0m" % (
    0, {'info': 32, 'warn': 33, 'msg': 33, 'error': 31, 'err': 31, 'yes': 36, 'ok': 35}[_type], '', s)
def 跟踪函数(n:int=None)->str:
    '''
    :param n: 倒数第几行
    :param _type: 输出颜色
    '''
    if n!=None:
        x=traceback.extract_stack()
        if abs(n)>len(x):
            return ''
        x=x[n]
        return f'{os.path.split(x.filename)[1]}/{x.name}/{x.lineno}'
    else:
        return '\n'.join([f'{os.path.split(x.filename)[1]}/{x.name}/{x.lineno}' for x in traceback.extract_stack()])

def 获取_编码(content):
    assert isinstance(content,bytes),'非bytes类型'
    coding=chardet.detect(content)
    return coding['encoding']
def 转编码(文本: str, 编码='utf-8') -> str:
    return 文本.encode(编码, 'ignore').decode(编码)
# 装饰器
@contextmanager
def error(错误提示:str='',抛出异常=False,递归=1,ignore=False)->None:
    '''
    with sx.try_error(抛出异常=1):
        1/0 #try里面的代码
    '''
    try:
        yield
    except BaseException as e:
        if ignore:
            return
        elif 抛出异常:
            raise e
        else:
            if 递归:
                err = e.__traceback__  # 获取当前错误 赋值err
                while True:
                    if err.tb_next:
                        err = err.tb_next
                    else:
                        lno = err.tb_lineno
                        break

            else:
                lno = e.__traceback__.tb_next.tb_lineno
            if lno!=e.__traceback__.tb_lineno and 递归:
                pcolor('[{}>{}] 错误: {}'.format(e.__traceback__.tb_next.tb_lineno, lno, 错误提示 if 错误提示 else e), 'err')
            # pcolor('[错误 {}] : {}'.format(sys.exc_info()[2].tb_next.tb_lineno ,error if error else e.args),'err')
            else:
                pcolor('[{}] 错误: {}'.format(lno, 错误提示 if 错误提示 else e), 'err')
def 打印错误(e: BaseException, 递归=1):
    if 递归:
        err = e.__traceback__  # 获取当前错误 赋值err
        while True:
            if err.tb_next:
                err = err.tb_next
            else:
                lno = err.tb_lineno
                break
    else:
        lno = e.__traceback__.tb_lineno
    if lno!=e.__traceback__.tb_lineno and 递归:
        pcolor('[{}>{}] 错误: {}'.format(e.__traceback__.tb_lineno, lno, e), 'err')
    else:
        pcolor('[{}] 错误: {}'.format(lno, e), 'err')
def zsq_again_return(num=5, cback=None, sleep=0, 显示错误=True, 过滤错误=False, last_err=True):
    过滤错误列表 = ['ProxyError', 'SSLError', 'IncompleteRead']  # 过滤错误

    def rt(func):
        def wear(*args, **keyargs):
            for i in range(num):
                try:
                    return func(*args, **keyargs)
                except BaseException as e:
                    lno = e.__traceback__.tb_next.tb_lineno if e.__traceback__.tb_next else e.__traceback__.tb_lineno
                    放行 = False
                    for item in 过滤错误列表:
                        if item in str(e.args):
                            放行 = True
                            break
                    if 放行:
                        if 过滤错误:
                            pcolor('[{}][{}] 错误: {}'.format(lno,func.__name__, e), 'error')
                    else:
                        if 显示错误:
                            if last_err:
                                if i == num - 1:
                                    pcolor('[{}][{}] 错误: {}'.format(lno,func.__name__, e), 'error')
                            else:
                                pcolor('->{}  [{}][{}] 错误: {}'.format(i + 1, lno, func.__name__, e), 'error' if i == num - 1 else 'warn')
                    time.sleep(sleep)
            return cback
        return wear
    return rt
def zsq_try(func):
    '''    错误装饰器    '''
    def rt(*args, **keyargs):
        try:
            return func(*args, **keyargs)
        except BaseException as e:
            lno = e.__traceback__.tb_next.tb_lineno if e.__traceback__.tb_next else e.__traceback__.tb_lineno
            msg = '[{}][{}] 错误: {}'.format(lno,func.__name__,e)
            pcolor(msg, 'error')
    return rt
def zsq_try_Exception(error: str = None, 递归=1) -> None:
    '''自定义错误装饰器'''
    def rt(func):
        def wear(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                if 递归:
                    err = e.__traceback__  # 获取当前错误 赋值err
                    while True:
                        if err.tb_next:
                            err = err.tb_next
                        else:
                            lno = err.tb_lineno
                            break
                else:
                    lno = e.__traceback__.tb_next.tb_lineno
                if lno !=e.__traceback__.tb_lineno:
                    pcolor('[{}>{}][{}] 错误: {}'.format(e.__traceback__.tb_next.tb_lineno, lno, func.__name__, error if error else e), 'err')
                else:
                    pcolor('[{}][{}] 错误: {}'.format(lno, func.__name__, error if error else e), 'err')
        return wear
    return rt
def zsq_thread(func):
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.setDaemon(True)  # 跟随程序关闭
        thr.start()
    return wrapper
def config_logging(文件路径: str='logging.log', 输出级别: int = logging.INFO, 写入级别: int = logging.DEBUG):
    '''
    #sx.config_logging('a.txt')
    logger = logging.getLogger(__name__)
    logger=logging.getLogger()
    logger.info("⼀般⽇志")
    logger.warning("警告⽇志")
    logger.error("错误⽇志")
    logger.debug("错误⽇志")

    %(levelno)s：打印⽇志级别的数值
    %(levelname)s：打印⽇志级别的名称
    %(pathname)s：打印当前执⾏程序的路径，其实就是sys.argv[0]
    %(filename)s：打印当前执⾏程序名
    %(funcName)s：打印⽇志的当前函数
    %(lineno)d：打印⽇志的当前⾏号
    %(asctime)s：打印⽇志的时间
    %(thread)d：打印线程ID
    %(threadName)s：打印线程名称
    %(process)d：打印进程ID
    %(message)s：打印⽇志信息
    '''
    file_handler = logging.FileHandler(文件路径, mode='a', encoding="utf8")
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s LINE:%(lineno)d %(levelname)s >> %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
    file_handler.setLevel(写入级别)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(filename)s LINE:%(lineno)d %(levelname)s >> %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
    console_handler.setLevel(输出级别)

    logging.basicConfig(level=min(输出级别, 写入级别), handlers=[file_handler, console_handler])
def get_fake_agent(浏览器='chrome'):
    '''chrome opera firefox internetexplorer safari'''
    return random.choice(fake_UserAgent['browsers'][浏览器])
def get_headers(浏览器=None):
    '''chrome opera firefox internetexplorer safari'''
    if 浏览器:
        agent = get_fake_agent(浏览器)
    else:
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
    return {'User-Agent'.lower(): agent}
def 退出(信息:str='',类型=1)->None:
    if 类型 and 信息:  # 抛出异常退出
        sys.exit("异常退出 : {}".format(信息)) if 信息 else sys.exit(0)
    else:     # 强制退出
        os._exit(0)
# 功能函数
def 读取文件(文件路径: str) -> bytes:
    if os.path.exists(文件路径):
        with open(文件路径, 'rb') as f:
            return f.read()
    else:
        pcolor(f'{文件路径} 文件不存在。', 'error')
        return None
def 写入文件(文件路径, 字节流) -> None:
    with open(文件路径, 'wb') as f:
        f.write(字节流)
def 写入文件a(文件路径, 字节流) -> None:
    with open(文件路径, 'ab') as f:
        f.write(字节流)
def 加载文件(文件路径: str, 编码: str = 'utf-8-sig')->str:
    try:
        with open(文件路径, 'r', encoding=编码) as f:
            return f.read()
    except Exception as e:
        with open(文件路径, 'r', encoding='ANSI') as f:
            return f.read()
def 加载文件_创建(文件路径:str,编码:str='utf-8-sig')->str:
    '''自动创建文件 返回'''
    if os.path.exists(文件路径):
        return 加载文件(文件路径,编码)
    else:
        with open(文件路径,mode='w',encoding=编码) as f:
            f.write('')
            return ''
def 保存文件(文件路径, 字符串, 编码='utf-8-sig')->None:
    with open(文件路径, 'w', encoding=编码) as f:
        f.write(字符串)
def 保存文件a(文件路径, 字符串, 编码='utf-8-sig')->None:
    with open(文件路径, 'a', encoding=编码) as f:
        f.write(字符串)
def 加载对象(文件路径)->object:
    with open(文件路径, 'rb') as f:
        return pickle.load(f)
def 保存对象(文件路径, 对象) -> None:
    with open(文件路径, 'wb') as f:
        pickle.dump(对象, f)
def 加载JSON(文件路径, 编码='utf-8-sig'):
    try:
        with open(文件路径, 'r', encoding=编码) as f:
            return json.load(f)
    except Exception as e:
        with open(文件路径, 'r', encoding='ANSI') as f:
            return json.load(f)
def 保存JSON(文件路径, JSON对象, 编码='utf-8-sig', indent=4):
    '''indent=None不格式化'''
    with open(文件路径, 'w', encoding=编码) as f:
        json.dump(JSON对象, f, ensure_ascii=False, indent=indent)
def 字符串转日期格式(时间字符串, 中文=False):
    if 中文:
        return '{:%Y年%m月%d日 %H时%M分%S秒}'.format(datetime.datetime.strptime(时间字符串, "%Y-%m-%d %H:%M:%S"))
    else:
        return datetime.datetime.strptime(时间字符串, "%Y-%m-%d %H:%M:%S")
def 日期格式转时间戳(日期格式=None):
    if 日期格式:
        return 日期格式.timestamp()
    else:
        return datetime.datetime.today().timestamp()
def 时间戳转日期格式(时间戳, 中文=False):
    if 中文:
        dateArray = datetime.datetime.fromtimestamp(时间戳)
        return dateArray.strftime("%Y年%m月%d %H时%M分%S秒")
    else:
        return datetime.datetime.utcfromtimestamp(时间戳)
def 隧道代理(proxyMeta="http://user:pwd@host:port") -> dict:
    '''代理服务器 阿布云 或者 亿牛云代理'''
    return {"http": proxyMeta, "https": proxyMeta, }
def 列表分组(列表: list, step: int) -> list:
    return [列表[i:i + step] for i in range(0, len(列表), step)]
def 合并列表(*a, default=None) -> list:
    '''[1],[2],[3],...'''
    lst = []
    L = max([len(x) for x in a])
    for i in range(L):
        r = []
        for j in range(len(a)):
            try:
                r.append(a[j][i])
            except:
                r.append(default)
        lst.append(r)
    return lst
def base64加密(input_: str or bytes, 编码='utf-8')->str:
    if type(input_)==bytes:
        return base64.encodebytes(input_).decode(编码).strip()
    elif type(input_)==str:
        return base64.b64encode(input_.encode(编码)).decode(编码)
    else:
        raise Exception('base64加密 输入类型错误')
def base64解密(字符串: str,编码='utf-8')->str:
    字符串 = 字符串.strip('=')
    for i in range(3):
        字符串 += '=' * i
        try:
            return base64.b64decode(字符串).decode(编码)
        except:
            pass
def base64加密图片(字节流: bytes, 图片类型='jpg') -> str:
    '''图片转字符串  图片类型gif png jpeg x-icon'''
    return ','.join(['data:image/{};base64'.format(图片类型), base64.b64encode(字节流).decode()])
def base64解密图片(字符串: str) -> bytes:
    '''字符串转成图片  图片类型jpg 或者 png'''
    return base64.b64decode(re.sub('data:image/.*?;base64,', '', 字符串))
def base64图片转PIL(base64字符串:str)->PILimage:
    return PILimage.open(BytesIO(base64解密图片(base64字符串)))
def url编码(s):
    return quote(s)
def url解码(s):
    return unquote(s)
def params_From_dict(query:dict)->str:
    result = []
    for k, v in query.items():
        result.append(f'{k}={v}')
    return '&'.join(result)
def str_From_dict(d: dict, 分隔1: str = ':', 分隔2: str = '\n') -> str:
    return f'{分隔2}'.join(['{}{}{}'.format(k.strip(), 分隔1, v.strip()) for k, v in d.items()])
def dict_From_Str(s: str, 分隔1: str = ':', 分隔2: str = '\n') -> dict:
    '''a:1\nb:2'''
    return dict([[y.strip() for y in x.strip().split(分隔1, 1)] for x in s.strip().split(分隔2) if x.strip()])
def dict_From_HeadersStr(head: str = '', 浏览器=None) -> dict:
    ''' s="host:xxx.com"  '''
    headers = get_headers(浏览器)
    head = head.strip()
    if head:
        for row in head.split('\n'):
            row = row.strip()
            if row:
                y = row.split(':', 1)
                if len(y) == 2:
                    headers[y[0].lower().strip()] = y[1].strip()
    return headers
def dict_From_DataStr(s: str) -> dict:
    ''' s="a=1&b=2"   '''
    return dict([x.strip().split('=', 1) for x in s.strip().split('&') if x.strip()])
def dict_From_CookieStr(s: str) -> dict:
    '''a=b;b=c;'''
    return dict([x.strip().split('=', 1) for x in s.strip().split(';') if x.strip()])
def dict_From_Cookiejar_Str(cookie_str: str = None, 列=[0, 1]) -> dict:
    ''' cookie_From_Cookiejar_Str('AIDUID	CCB5060E627C5BD5804CDD46A7C050FF:FG=1	.baidu.com	/	2022-08-17T02:14:53.615Z	44			') '''
    rt_dict = {}
    for x in cookie_str.strip().split('\n'):
        if x.strip():
            c = x.split('\t')
            rt_dict[c[列[0]].strip()] = c[列[1]].strip()
    return rt_dict
def dict_From_DataStr_QueryStr(s: str) -> dict:
    return dict_From_Str(s, ':', '\n')
def cookie_From_Cookies(cook: object) -> str:
    '''cook对象转字符串'''
    xx = []
    for k, v in cook.items():
        xx.append('{}={}'.format(k, v))
    return ';'.join(xx)
def cookie_From_Application_Cookies(cookie:str)->str:
    return str_From_dict(dict_From_Cookiejar_Str(cookie), '=',';')
def 保存Cookiejar_From_CookiejarStr(文件路径: str = None, cookie_str: str = None) -> str or None:
    '''
    cookiejar_From_Str("cookie.txt",'AIDUID	CCB5060E627C5BD5804CDD46A7C050FF:FG=1	.baidu.com	/	2022-08-17T02:14:53.615Z	44			')
    :param 文件路径: cookie保存的路径
    :param cookie_str: 复制f12 application cookies的表格字符串
    :return:如果有文件路径直接保存返回空 如果没有则返回字符串
    '''
    # 字符串列
    keys = ['name', 'value', 'domain', 'path', 'expires-max-age', 'size', 'http', 'secure', 'samesite']
    rt_s = ''
    if cookie_str:
        for x in cookie_str.strip().split('\n'):
            if x.strip():
                values = x.split('\t')
                c = dict(合并列表(keys, values))
                # 保留一级域名如 .bilibili.com
                domain = c['domain'].split('.')
                domain[0] = ''
                domain = '.'.join(domain)
                row = [domain, 'TRUE', c['path'], 'FALSE', '4788470561', c['name'], c['value']]  # 过期时间100年
                rt_s += '\t'.join(row) + '\n'
    if 文件路径:
        with open(文件路径, 'w') as f:
            f.write(rt_s)
    else:
        return rt_s
def 保存LWPCookieJar_From_CookiejarStr(文件路径: str, cookie_str: str) -> None:
    '''cookiejar_From_Str("cookie.txt",'AIDUID	CCB5060E627C5BD5804CDD46A7C050FF:FG=1	.baidu.com	/	2022-08-17T02:14:53.615Z	44			')'''
    jar = LWPCookieJar()
    keys = ['name', 'value', 'domain', 'path', 'expires-max-age', 'size', 'http', 'secure', 'samesite']
    for x in cookie_str.split('\n'):
        if x.strip():
            values = x.split('\t')
            c = dict(合并列表(keys, values))
            c['expires-max-age'] = '4788470561'  # 过期时间100年
            jar.set_cookie(
                cookiejar.Cookie(version=0, name=c['name'], value=c['value'], domain=c['domain'], path=c['path'],
                                 secure=c['secure'],
                                 expires=c['expires-max-age'] if "expires-max-age" in c else None,
                                 domain_specified=True, domain_initial_dot=False,
                                 path_specified=True,
                                 rest={}, discard=False, comment=None, comment_url=None, rfc2109=False,
                                 port='80', port_specified=False,
                                 ))
    jar.save(文件路径)
def 加载配置文件(默认配置: dict, 文件路径='conf.ini', 编码='utf-8-sig') -> dict:
    config = configparser.ConfigParser()
    if not os.path.exists(文件路径):
        config['conf'] = 默认配置
        with open(文件路径, 'w', encoding=编码) as f:
            config.write(f)
    try:
        config.read(文件路径, encoding=编码)
    except Exception as e:
        config.read(文件路径, encoding='ANSI')
    return config['conf']
def 保存配置文件(配置对象: configparser.SectionProxy, 文件路径='conf.ini', 编码='utf-8-sig') -> None:
    config = configparser.ConfigParser()
    config['conf'] = 配置对象
    with open(文件路径, 'w', encoding=编码) as f:
        config.write(f)
def CMD_POPEN(*cmd) -> str:
    '''文本方式'''
    with os.popen(*cmd) as f:
        return f.read()  # 获取管道信息
def CMD_SYSTEM(*cmd) -> int:
    '''
    返回命令执行结果的返回值  阻塞
    返回0 运行成功 1没有这个命令'''
    return os.system(*cmd)
def CMD_SUBPROCESS_CALL(cmd, 类型=1):
    '''返回0 运行成功 1没有这个命令 '''
    # 不允许创建窗口
    if 类型 == 1:
        CREATE_NO_WINDOW = 0x08000000
        return subprocess.call(cmd, creationflags=CREATE_NO_WINDOW)
    # 隐藏窗口
    elif 类型 == 2:
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        return subprocess.call(cmd, startupinfo=si)
    # 不允许子窗口
    else:
        DETACHED_PROCESS = 0x00000008
        return subprocess.call(cmd, creationflags=DETACHED_PROCESS)
def 设置_临时环境变量(k, v):
    os.environ[k] = v
def 设置_永久环境变量(k, v, tp=1):
    '''tp  1用户变量 2系统变量 '''
    if tp == 1:
        CMD_SUBPROCESS_CALL('setx {} {}'.format(k, v))  # 用户变量
    else:
        CMD_SUBPROCESS_CALL('setx {} {} /m'.format(k, v))  # 系统变量
def 随机字符串(长度=6, 类型=3):
    '''1 数字 2 字母 3字母数字 4字母数字特殊符号'''
    if 类型 == 1:
        s = string.digits
    elif 类型 == 2:
        s = string.ascii_letters
    elif 类型 == 3:
        s = string.ascii_letters + string.digits
    else:
        s = string.ascii_letters + string.digits + string.punctuation
    rt = []
    for i in range(长度):
        rt.append(random.choice(s))
    return ''.join(rt)
def 执行代码(python代码):
    '''
    print("hello")
    '''
    exec(python代码)
def 进制转换(进制对象: str, 当前进制: int, 转为进制: int, 去符号: bool = True) -> str:
    ''' print(进制转换(96,16,8)) print(进制转换('0x96',16,8)) '''
    try:
        十进制 = int(str(进制对象), 当前进制)
        if 转为进制 == 10:
            return str(十进制)
        elif 转为进制 == 2:
            rt = bin(十进制)
        elif 转为进制 == 8:
            rt = oct(十进制)
        elif 转为进制 == 16:
            rt = hex(十进制)
        return rt[2:] if 去符号 else rt
    except Exception as e:
        raise Exception('进制转换错误')
def 进制转换_16TO字符串(s16, 编码='utf-8'):
    from binascii import a2b_hex
    s16 = s16 if type(s16) == bytes else s16.encode(编码)
    return a2b_hex(s16).decode(编码)
def 进制转换_字符串TO16(s, 编码='utf-8'):
    from binascii import b2a_hex
    s = s if type(s) == bytes else s.encode(编码)
    return b2a_hex(s).decode(编码)
def get_uuid():
    import uuid
    return uuid.uuid1()
def byte_to_hex(b:bytes)->bytes:
    return binascii.b2a_hex(b)
    #return binascii.hexlify(b)
def hex_to_byte(b:bytes)->bytes:
    return binascii.a2b_hex(b)
    #return binascii.unhexlify(s)
def hex_to_str(b:bytes,编码='utf-8')->str:
    return binascii.a2b_hex(b).decode(编码)
def str_to_hex(s:str,编码='utf-8')->bytes:
    return binascii.b2a_hex(s.encode(编码))
def byte_to_base64(b:bytes)->bytes:
    return binascii.b2a_base64(b).strip()
def base64_to_byte(b:bytes)->bytes:
    return binascii.a2b_base64(b)
def base64_to_hex(b: bytes or str) -> bytes:#base64->bytes->hex
    if isinstance(b, str):
        b=binascii.a2b_base64(b)
    return binascii.b2a_hex(b)
def byte_to_uint8array(b: bytes) -> list:
    # import numpy as np
    # np.asarray(bytearray(b), dtype="uint8")
    return [x for x in bytearray(b)]
def uint8array_to_byte(lst: list) -> bytes:
    return bytes(lst)
def hex_to_base64(b:bytes)->bytes: #h2x->bytes->base64
    return  binascii.b2a_base64(binascii.a2b_hex(b)).strip()
def str_to_ascii(字符串: str) -> list:
    return [ord(x) for x in 字符串]
def ascii_to_str(列表: list,字符串=True) -> list or str:
    if 字符串:
        return ''.join([chr(x) for x in 列表])
    else:
        return [chr(x) for x in 列表]
def html不转义(字符串):
    return unescape(字符串)
def html转义(字符串):
    return escape(字符串)
def 获取_搜索文件(文件夹目录: str, 关键字: str, 打印=False) -> list:
    '''
    sx.搜索文件(r'D:\python_project\aa', '*mp4 *.mp3',打印=1)
    模糊查询  只能获取文件名 无法获取文件夹
    '''
    import glob
    result = []
    keys = [x.strip() for x in 关键字.split(' ') if x.strip()]
    for root, lists, files in os.walk(文件夹目录):
        for file in files:
            for key in keys:
                file_pattern = os.path.join(root, key)
                for fpath in glob.glob(file_pattern):
                    if 打印:
                        print(fpath)
                    if fpath not in result:
                        result.append(fpath)
    return result
def 获取_目录文件(文件夹目录: str, 打印=False):
    class DirFile():
        文件夹 = [];
        文件 = [];
        文件夹数 = 文件数 = 0

    result = DirFile()
    if not os.path.exists(文件夹目录):
        return result
    for root, lists, files in os.walk(文件夹目录):
        for file in files:
            file_path = os.path.join(root, file)
            if 打印:
                print('文件', file_path)
            if file_path not in result.文件:
                result.文件.append(file_path)
                result.文件数 += 1
        for dir in lists:
            dir_path = os.path.join(root, dir)
            if 打印:
                print('目录', dir_path)
            else:
                if dir_path not in result.文件夹:
                    result.文件夹.append(dir_path)
                    result.文件夹数 += 1
    return result
def 获取_正则搜索文件(文件夹目录: str,正则表达式='', 打印=False):
    class DirFile():
        文件夹 = [];
        文件 = [];
        文件夹数 = 文件数 = 0

    result = DirFile()
    if not os.path.exists(文件夹目录):
        return result
    for root, lists, files in os.walk(文件夹目录):
        for file in files:
            if re.match(正则表达式,file):
                file_path = os.path.join(root, file)
                if 打印:
                    print('文件', file_path)
                if file_path not in result.文件:
                    result.文件.append(file_path)
                    result.文件数 += 1
        for dir in lists:
            if re.match(正则表达式,dir):
                dir_path = os.path.join(root, dir)
                if 打印:
                    print('目录', dir_path)
                else:
                    if dir_path not in result.文件夹:
                        result.文件夹.append(dir_path)
                        result.文件夹数 += 1
    return result
def 检查文件名(s, 编码='utf-8',replace=' '):
    c = '\/:*?"<>|\x08'
    s = s.encode(编码, 'ignore').decode(编码).replace('\\',replace).replace('/',replace)
    s = ' '.join(s.split()) #去掉\r \n \t
    name = ''.join([x for x in s if x not in c]).strip() #去掉'\/:*?"<>|\x08'
    if not name:
        name = 随机字符串(11, 3)
    for i in range(len(name) - 1, -1, -1):  #去掉结尾字符串
        if name[i] in [' ', '.']:
            name=name[:-1]
        else:
            break
    return name
def 创建目录(文件路径: str, 提示类型: int = 1, 编码: str = 'utf-8'):
    '''
    作用：自动创建目录 并且检查是否可以创建 如果 已存在返回 False 不存在返回True
    if 创建目录(目录="abc/123",文件名='a.txt')['bl']:
        print(1)
    True 可以创建文件  False 不能创建
    提示类型 1 全路径 2 文件名
    '''

    class CreateFilepath:
        可创建 = 目录 = 文件名 = 文件路径 = 类型 = 描述 = ''
        def __str__(self):
            return str({x: self.__getattribute__(x) for x in dir(self) if '__' not in x})

    文件路径 = 文件路径.encode(编码, 'ignore').decode(编码).replace('/', "\\")
    文件路径 = ' '.join(文件路径.split())
    目录, 文件名 = os.path.split(文件路径)
    rt = CreateFilepath()

    新的文件名=检查文件名(文件名)
    新的路径 = ''

    if 目录:  # 新路径
        文件夹列表 = 目录.split('\\')
        if 文件夹列表:
            dir_new = []
            if re.match('^\w:$', 文件夹列表[0]):  # c: d:
                # 绝对路径
                dir_new.append(文件夹列表[0])
                for d in 文件夹列表[1:]:
                    dir_new.append(检查文件名(d))
            else:
                for d in 文件夹列表:
                    dir_new.append(检查文件名(d))
            新的路径 = '\\'.join(dir_new)
            if 新的路径:
                os.makedirs(os.path.abspath(新的路径), exist_ok=True)
    if (not 新的文件名) and (not 新的路径):
        rt.描述 = '文件路径错误'
        return rt
    elif 新的文件名:
        rt.类型 = '文件'
    else:
        rt.类型 = '目录'
    save_name = os.path.join(新的路径, 新的文件名) if 目录 else 新的文件名
    if os.path.exists(save_name):
        if 新的文件名:
            rt.可创建 = False
            rt.描述 += '已存在'
        else:
            rt.可创建 = False
            rt.描述 += '空'
    else:
        if 新的文件名:
            rt.可创建 = True
            rt.描述 += '不存在'
        else:
            rt.可创建 = False
            rt.描述 += '空'
    rt.目录 = 新的路径
    rt.文件名 = 新的文件名
    rt.文件路径 = save_name
    if not rt.可创建 and 提示类型:
        if 提示类型 == 1:
            pcolor('已存在 : {}'.format(save_name), 'ok')
        elif 提示类型 == 2:
            pcolor('已存在 : {}'.format(新的文件名), 'ok')
        else:
            pass
    return rt
def 定时运行(秒: int, 函数, 参数: list):
    '''#定时器 单位秒 只执行一次  sx.定时运行(1,task,(1,2,3))'''
    from threading import Timer
    t = Timer(interval=秒, function=函数, args=参数, kwargs=None)
    t.setDaemon(True)
    t.start()
def 绝对路径(文件名):
    '''获取文件绝对路径'''
    return os.path.abspath(文件名)
def 排序_列表里字典(列表, 键, 倒序=False) -> list:
    return sorted(列表, key=lambda d: d[键], reverse=倒序)  # False 正序
def 排序_字典键值(字典, 位置, 倒序=False) -> dict:
    return sorted(字典.items(), key=lambda d: d[位置], reverse=倒序)  # False 正序
def 排序_列表里元组(列表, 位置, 倒叙=False) -> list:
    return sorted(列表, key=lambda d: d[位置], reverse=倒叙)  # False 正序
def 排序_列表(列表, 倒叙=False) -> list:
    return sorted(列表, reverse=倒叙)
def 列表_字典分组(列表:list,健:str,排序健:str='',倒叙=False)->dict:
    # from operator import itemgetter
    # from itertools import groupby
    # from collections import defaultdict
    # lst=sorted(列表,key=lambda k:k[健],reverse=倒叙)
    # lst = groupby(lst, key=itemgetter(健))
    # rt=defaultdict(list)
    # for k, v in lst:
    #     for x in v:
    #         rt[k].append(x)
    # return rt
    from collections import defaultdict
    rt=defaultdict(list)
    列表.sort(key=lambda k:k[排序健 if 排序健 else 健],reverse=倒叙)
    for x in 列表:
        rt[x[健]].append(x)
    return rt
def 集合_交集(*args):
    '''[1,2,3],[2],[1,2,3]'''
    return list(reduce(lambda a, b: a & b, [set(x) for x in args]))
def 集合_并集(*args):
    return list(reduce(lambda a, b: a | b, [set(x) for x in args]))
def 集合_差集(*args):
    return list(reduce(lambda a, b: a - b, [set(x) for x in args]))
def 正则_提取中文(s):
    p = re.compile(r'[\u4e00-\u9fa5]')
    res = re.findall(p, s)
    result = ''.join(res)
    return result
def 加密_MD5(对象, 加密字符串=None) -> str:
    '''
    :param 对象: 加密字符串
    :param 加密字符串: 密码
    :return: 返回加密后16进制字符串
    '''
    hsobj = md5(str(对象).encode("utf-8"))
    if 加密字符串:
        hsobj.update(str(加密字符串).encode("utf-8"))
    return hsobj.hexdigest()
def 加密_SHA1(对象: str):
    return sha1(str(对象).encode('utf-8')).hexdigest()
def 加密_HMAC_MD5(对象, 加密字符串='')->str:
    '''
    :param 对象: 加密字符串
    :param 加密字符串: 密码
    :return: 返回加密后16进制字符串
    '''
    import hmac
    m=hmac.new(加密字符串.encode(), str(对象).encode(),md5)
    return m.hexdigest()
def 获取_TXT行列(文件路径: str, 分割行='\n', 分割列=None) -> list:
    with open(文件路径, 'r', encoding='utf-8-sig') as f:
        s = f.read()
    if 分割列:
        return [[y.strip() for y in x.strip().split(分割列) if y.strip()] for x in s.split(分割行) if x.strip()]
    else:
        return [x.strip() for x in s.split(分割行) if x.strip()]
def 打印_进度条(字符串, 当前ID, 总数, 步长, 下载速度=None, 符号='█', 符号2='░', 进度条长度=30, 类型=4):
    '''打印_进度条('下载文件',0,100,类型=1)'''
    当前ID = 当前ID + 步长
    百分百 = 当前ID / 总数
    if 下载速度:
        speed = ' {}'.format(下载速度)
    else:
        speed = ''
    L = int(进度条长度 * 百分百)
    if 类型 == 1:
        print(('\r{:<%d} {:>4} {} {}/{}{}' % 进度条长度).format(L * 符号 + (进度条长度 - L) * 符号2, f'{int(100 * 百分百)}%', 字符串, 当前ID,
                                                           总数, speed), end='', flush=True)
    elif 类型 == 2:
        print(("\r{:>4} {:<%d} {} {}/{}{}" % 进度条长度).format(f'{int(100 * 百分百)}%', L * 符号 + (进度条长度 - L) * 符号2, 字符串, 当前ID,
                                                           总数, speed), end='', flush=True)
    elif 类型 == 3:
        print(('\r{:<%d} {:>4} {} {}/{}{}' % 进度条长度).format(L * 符号 + (进度条长度 - L) * 符号2, f'{int(100 * 百分百)}%', 字符串,
                                                           当前ID, 总数, speed), end='', flush=True)
    elif 类型 == 4:
        print(("\r{:>4} {:<%d} {} {}/{}{}" % 进度条长度).format(f'{int(100 * 百分百)}%', L * '#' + (进度条长度 - L) * '_', 字符串, 当前ID,
                                                           总数, speed), end='', flush=True)
def 打印_列表(列表:list)->None:
    [print(x) for x in 列表]
def 打印_字典(字典:dict,width:int=20)->None:
    [print('{1:>{0}} : {2}'.format(width,repr(k),repr(v))) for k,v in 字典.items()]
def 打印_JSON(json_):
    print(json.dumps(json_,indent=4,ensure_ascii=False))
#特殊功能函数
def 删除目录树(path):
    from shutil import rmtree
    rmtree(os.path.abspath(path))
def 获取_页数(总数, 分页数):
    return 总数 // 分页数 if 总数 % 分页数 == 0 else (总数 // 分页数) + 1
def 字符串缩略(字符串, 位数, 结尾符号='...'):
    '''('xxxx',6,'...')'''
    if len(字符串) <= 位数:
        return 字符串
    else:
        return 字符串[:位数 - len(结尾符号)] + 结尾符号
def 获取_URL参数(网址: str) -> dict:
    query = {}
    for x in urlparse(网址).query.split('&'):
        if x:
            a, b = x.split('=')
            query[a.lower()] = b
    return query
def 获取_URL_HOST(网址:str)->str:
    return urlparse(网址).hostname
def 获取_URL_QUERY(网址:str)->str:
    return urlparse(网址).query
def 提取m3u8List(字符串:str,倒叙=0)->list():
    lst=[]
    for row in 字符串.split('\n'):
        a=re.search('(http.*?\.m3u8.*?)(\n|$|\s+)', row.strip())
        if a:
            lst.append(a.group(1))
    return sorted(lst,reverse=倒叙)
def 单选(标题, items: list) -> dict:
    '''单选框('xx',[{'i':1,'name':'xxx'},{'i':2,'name':'yyy'}])'''
    while 1:
        try:
            pcolor('【{} 返回0】'.format(标题))
            value = int(input(':'))
            if value == 0:
                return -1
            if 1 <= value <= len(items):
                for x in items:
                    if x['i'] == value:
                        return x
        except:
            pass
def 多选(标题: str, items: list) -> list:
    ''' 多选('xx',[{'i':1,'name':'xxx'},{'i':2,'name':'yyy'}]) i大于等于1 '''
    while 1:
        try:
            ids = [x['i'] for x in items]
            pcolor('【{} 如1-3 1,2,3 返回0】'.format(标题))
            value = input(':')  # 1,2,3 1-3,all,0
            if value == '0':
                return -1
            else:
                if '-' in value:
                    value = value.split('-', 1)
                    start = int(value[0])
                    end = int(value[1])
                    selected = list(range(start, end + 1, 1))
                else:
                    selected = [int(x.strip()) for x in value.split(',') if x.strip()]
                selected = [items[x - 1] for x in selected if x in ids]
                return selected
        except:
            pass
def 文本对齐(文本:str,长度=20,对齐='L'):
    L=len(文本.encode('GBK'))
    if 对齐.upper()=='R':
        return '{:>{len}}'.format(文本, len=长度 - L + len(文本))
    elif 对齐.upper()=='M':
        return '{:^{len}}'.format(文本, len=长度-L+len(文本))
    else:
        return '{:<{len}}'.format(文本, len=长度 - L + len(文本))
# js函数转换
def 执行JS代码(js代码):
    '''执行JS代码('return 123') 无需js环境'''
    sss = '''
    function func(){
        %s
    }
    ''' % js代码
    js = EvalJs()
    js.execute(sss)
    return js.func()
def 执行EXECJS(js代码):
    '''执行JS代码('return 123')  需要nodejs环境'''
    sss = ''' function func(){ %s } ''' % js代码
    js = compile(sss)
    return js.call('func')
def JS_Uint8Array(lst:list)->bytes:
    return bytes(lst)
def JS_parseInt(a,b):
    return int(a,b)
def JS_int8arry_to_uint8arry(lst:list)->list:
    return [x if x>=0 else x+256 for x in lst]
def join(列表:list,分割=''):
    return 分割.join(map(str,列表))
def json_path(josn对象, 表达式, first=True):
    '''
    # 查询store下的所有元素
    print(jsonpath.jsonpath(book_store, '$.store.*'))

    # 获取json中store下book下的所有author值
    print(jsonpath.jsonpath(book_store, '$.store.book[*].author'))

    # 获取所有json中所有author的值
    print(jsonpath.jsonpath(book_store, '$..author'))

    # 获取json中store下所有price的值
    print(jsonpath.jsonpath(book_store, '$.store..price'))

    # 获取json中book数组的第3个值
    print(jsonpath.jsonpath(book_store, '$.store.book[2]'))

    # 获取所有书
    print(jsonpath.jsonpath(book_store, '$..book[0:1]'))

    # 获取json中book数组中包含isbn的所有值
    print(jsonpath.jsonpath(book_store, '$..book[?(@.isbn)]'))

    # 获取json中book数组中price<10的所有值
    print(jsonpath.jsonpath(book_store, '$..book[?(@.price<10)]'))

    # 从根节点开始，匹配name节点
    jsonpath.jsonpath(json_obj, '$..name')

    # A 下面的节点
    jsonpath.jsonpath(json_obj, '$..A.*')

    # A 下面节点的name
    jsonpath.jsonpath(json_obj, '$..A.*.name')

    # C 下面节点的name
    jsonpath.jsonpath(json_obj, '$..C..name')

    # C 下面节点的第二个
    jsonpath.jsonpath(json_obj, '$..C[1]')

    # C 下面节点的第二个的name
    jsonpath.jsonpath(json_obj, '$..C[1].name')

    # C 下面节点的2到5的name
    jsonpath.jsonpath(json_obj, '$..C[1:5].name')

    # C 下面节点最后一个的name
    jsonpath.jsonpath(json_obj, '$..C[(@.length-1)].name')
    '''
    try:
        if first:
            return jsonpath.jsonpath(josn对象,表达式)[0]
        else:
            return jsonpath.jsonpath(josn对象,表达式)
    except:
        if first:
            return None
        else:
            return []
# 请求
def get_proxies(ip_port:str='')->dict:
    '''
    自定义 代理IP  '127.0.0.1:8080'
    或者获取本地代理
    返回列表{} 或者 None
    '''
    if ip_port:
        return {'http': f'http://{ip_port}', 'https': f'http://{ip_port}'}
    else:
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_READ)
        retVal = winreg.QueryValueEx(hKey, "ProxyEnable")
        开启 = retVal[0]
        if 开启:
            res = winreg.QueryValueEx(hKey, "ProxyServer")
            lst = res[0].split(';')
            lst = list(set([x.split('=', 1)[1] if '=' in x else x for x in lst]))
            return {'http': f'http://{lst[0]}', 'https': f'http://{lst[0]}'} if lst else None
        else:
            return None
def set_proxies(ip_port='127.0.0.1:8080',开启代理=1,白名单="")->None:
    '''
    :param 开启代理: 1 或者 0
    :param ip_port: 127.0.0.1:8080;127.0.0.1:8888
    :param 白名单: 127.*;10.*;172.16.*;
    :return:
    '''
    hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
    winreg.SetValueEx(hKey, "ProxyEnable", 0, winreg.REG_DWORD, 开启代理)
    winreg.SetValueEx(hKey, "ProxyServer", 0, winreg.REG_SZ, ip_port)
    winreg.SetValueEx(hKey, "ProxyOverride", 0, winreg.REG_SZ, 白名单)
    winreg.CloseKey(hKey)
def get_request(url, headers=None, verify=False, proxies=None, allow_redirects=True, cookies=None, stream=False, timeout=30, try_num=1):
    for i in range(try_num):
        try:
            with requests.get(url, timeout=timeout, headers=headers if headers else get_headers('chrome'), verify=verify, proxies=proxies,
                              allow_redirects=allow_redirects, cookies=cookies, stream=stream) as resp:
                return resp
        except Exception as e:
            if i == try_num - 1:
                raise Exception(跟踪函数(-3)+' '+str(e))
def post_request(url, headers=None, data=None, verify=False, proxies=None, allow_redirects=True, cookies=None, json_=None, timeout=30, try_num=1):
    for i in range(try_num):
        try:
            with requests.post(url, timeout=timeout, headers=headers if headers else get_headers('chrome'), verify=verify, proxies=proxies,
                               allow_redirects=allow_redirects, data=data, json=json_, cookies=cookies) as resp:
                return resp
        except Exception as e:
            if i == try_num - 1:
                raise Exception(跟踪函数(-3)+' '+str(e))
def 下载文件(文件路径: str = None, 网址: str = '', headers=None, proxies=None, verify=False, cookies=None, try_num=3) -> bool:
    if not 文件路径:
        文件路径 = 网址.rsplit('/', 1)[-1]
    for i in range(try_num):
        try:
            with requests.get(网址, timeout=15, verify=verify, proxies=proxies, allow_redirects=True, headers=headers if headers else get_headers('chrome'),
                              cookies=cookies) as res:
                if res.status_code == 200:
                    res = res.content
                    with open(文件路径, 'wb') as f:
                        f.write(res)
                    return True
                else:
                    if str(res.status_code) in http_err_code.keys():
                        raise Exception(res.status_code, ','.join(http_err_code[str(res.status_code)].values()))
                    else:
                        raise Exception('下载文件失败')
        except Exception as e:
            if i == (try_num - 1):
                pcolor('下载文件错误:{},{}'.format(e.args, e.__traceback__.tb_lineno), 'error')
    return False
def 下载文件_进度条(文件路径: str = None, 网址: str = '', 分段长度: int = 3*1024, 多线程=False, 线程数=5, headers=None, proxies=None, verify=False, cookies=None, 进度条函数=None, 打印错误=True, try_num=2) -> bool:  # 分段长度 kb
    '''覆盖已存在的文件'''
    if not headers:
        headers = get_headers('chrome')
    print('[ {} ] : {}'.format(scolor('下载文件', 'warn'), scolor(文件路径, 'yes')))
    for num in range(try_num):
        if not 文件路径:
            文件路径 = 网址.rsplit('/', 1)[-1]
        if os.path.exists(文件路径):
            os.remove(文件路径)
        try:
            with requests.get(网址, stream=True, headers=headers, proxies=proxies, cookies=cookies,
                              verify=verify) as resp:
                if 'content-length' in resp.headers:
                    size = int(resp.headers['content-length'])
                    chunk_size = 1024 * 分段长度  # 分段接收
                    c = size / chunk_size
                    total_size = c / 1024 * 分段长度
                    count = int(size / chunk_size) if size % chunk_size == 0 else int(size / chunk_size) + 1
                    start_time = time.time()
                    if 多线程:
                        n = 0

                        def get_one(网址, str_range):
                            nonlocal n
                            head = headers.copy()
                            head['range'] = str_range
                            for i in range(try_num):
                                try:
                                    with requests.get(网址, stream=True, headers=head, proxies=proxies, cookies=cookies,
                                                      verify=verify) as resp:
                                        content = resp.content
                                        if 进度条函数:
                                            进度条函数(int((n + 1) / count * 100), '{:.2f}mb'.format(total_size))
                                        t=time.time()-start_time
                                        seconds = t * count / (i + 1) - t
                                        if seconds<1:
                                            剩余时间 = ' '*12
                                        else:
                                            m, s = divmod(seconds, 60)
                                            h, m = divmod(m, 60)
                                            剩余时间 = ' {:0=2.0f}:{:0=2.0f}:{:0=2.0f}'.format(h,m,s)
                                        speed = '{:.2f}MB/S{}'.format(
                                            (n + 1) * chunk_size / 1024 / 1024 / t,剩余时间)
                                        打印_进度条('{:.2f}MB'.format(total_size), n, count, 1, 下载速度=speed)  # 步长1
                                        n += 1
                                        return content
                                except:
                                    return b''

                        pool = ThreadPoolExecutor(max_workers=线程数)
                        tasks = []
                        for i in range(count):
                            if i == count - 1:
                                r = 'bytes={}-'.format(chunk_size * i)
                            else:
                                r = 'bytes={}-{}'.format(chunk_size * i, chunk_size * (i + 1) - 1)
                            tasks.append(pool.submit(get_one, 网址, r))
                        pool.shutdown(wait=True)
                        with open(文件路径, mode='wb') as f:
                            for task in tasks:
                                f.write(task.result())
                        del tasks
                    else:
                        with open(文件路径, 'wb') as f:
                            for i, content in enumerate(resp.iter_content(chunk_size=chunk_size)):
                                f.write(content)
                                if 进度条函数:
                                    进度条函数(int((i + 1) / count * 100), '{:.2f}mb'.format(total_size))
                                t=time.time() - start_time
                                seconds=t * count / (i + 1) - t
                                if seconds<1:
                                    剩余时间 = ' '*12
                                else:
                                    m, s = divmod(seconds, 60)
                                    h, m = divmod(m, 60)
                                    剩余时间 = ' {:0=2.0f}:{:0=2.0f}:{:0=2.0f}'.format(h,m,s)
                                speed = '{:.2f}MB/S{}'.format((i + 1) * chunk_size / 1024 / 1024 / t,剩余时间)
                                打印_进度条('{:.2f}MB'.format(total_size), i, count, 1, 下载速度=speed)  # 步长1
                    print()
                    return True
                elif 'Content-Disposition' in resp.headers:
                    print('[ {} ] : {} MB'.format(scolor('文件大小', 'warn'), round(len(resp.content) / 1024 / 1024, 2)))
                    with open(文件路径, 'wb') as f:
                        f.write(resp.content)
                    return True
                else:
                    return False
        except Exception as e:
            if num == (try_num - 1):
                if 打印错误:
                    pcolor('下载文件错误:{},{}'.format(e.args, e.__traceback__.tb_lineno), 'error')
    print()
    return False
def 下载视频(文件路径:str='',网址:str="",cli_href="",ffmpeg_href="",cli_local="",ffmpeg_local="", option:list=[],istest:bool=False,try_num=1):
    '''
    文档地址 https://nilaoda.github.io/N_m3u8DL-CLI/M3U8URL2File.html
    :param 文件路径: download/xxx 不带后缀
    :param 网址:
    :param baseUrl:  修改ts的头部
    :param maxThreads:
    :param key:
    :param iv:
    :param headers:
    :param istest:
    :param cmd:
    :param option: option=['--headers','"key:value|key1:value1"']
    :return:
    '''
    save_path=文件路径+'.mp4'
    #不重复下载
    if os.path.exists(save_path):
        return True
    workDir,saveName=os.path.split(文件路径)
    if not workDir:
        workDir=os.path.join(os.getcwd(),'Downloads')
    if not saveName:
        saveName="test"
    path = os.path.join(os.path.expanduser('~'), '下载')
    os.makedirs(path, exist_ok=1)
    #如果指定本地文件
    cli_path = cli_local if cli_local else os.path.join(path, "m3u8dl.exe")
    ffmpeg_path = ffmpeg_local if ffmpeg_local else os.path.join(path, "ffmpeg.exe")
    if not os.path.exists(cli_path):
        if not cli_href:
            cli_href=CLI_HREF
        下载文件_进度条(文件路径=cli_path, 网址=cli_href)
    if not os.path.exists(ffmpeg_path):
        if not ffmpeg_href:
            ffmpeg_href=FFMPEG_HREF
        下载文件_进度条(文件路径=ffmpeg_path, 网址=ffmpeg_href)
    # cmd = '"https://vipcache-ffsirapi-llqsource.byteamone.cn/youku/762f2b2c94eaf74bbe19ed5a96966232.m3u8" --workDir "download" --saveName "title" --headers "headers" --baseUrl "baseurl" --maxThreads "30" --minThreads "10" --useKeyBase64 "key" --useKeyIV "iv" --enableDelAfterDone '
    workDir = os.path.join(os.getcwd(), workDir)
    cmd = '{} "{}" --enableDelAfterDone --workDir "{}" --saveName "{}"'.format(cli_path, 网址, workDir, saveName)
    '''
    --workDir    Directory      设定程序工作目录
    --saveName   Filename       设定存储文件名(不包括后缀)
    --baseUrl    BaseUrl        设定Baseurl
    --headers    headers        设定请求头，格式 key:value 使用|分割不同的key&value
    --maxThreads Thread         设定程序的最大线程数(默认为32)
    --minThreads Thread         设定程序的最小线程数(默认为16)
    --retryCount Count          设定程序的重试次数(默认为15)
    --timeOut    Sec            设定程序网络请求的超时时间(单位为秒，默认为10秒)
    --muxSetJson File           使用外部json文件定义混流选项
    --useKeyFile File           使用外部16字节文件定义AES-128解密KEY
    --useKeyBase64 Base64String 使用Base64字符串定义AES-128解密KEY
    --useKeyIV     HEXString    使用HEX字符串定义AES-128解密IV
    --downloadRange Range       仅下载视频的一部分分片或长度
    --liveRecDur HH:MM:SS       直播录制时，达到此长度自动退出软件
    --stopSpeed  Number         当速度低于此值时，重试(单位为KB/s)
    --maxSpeed   Number         设置下载速度上限(单位为KB/s)
    --proxyAddress http://xx    设置HTTP代理, 如 http://127.0.0.1:8080
    --enableDelAfterDone        开启下载后删除临时文件夹的功能
    --enableMuxFastStart        开启混流mp4的FastStart特性
    --enableBinaryMerge         开启二进制合并分片
    --enableParseOnly           开启仅解析模式(程序只进行到meta.json)
    --enableAudioOnly           合并时仅封装音频轨道
    --disableDateInfo           关闭混流中的日期写入
    --noMerge                   禁用自动合并
    --noProxy                   不自动使用系统代理
    --disableIntegrityCheck     不检测分片数量是否完整
    '''
    lst = []
    if istest:
        lst += ['--downloadRange', '0-9']
    lst += option
    if lst:
        cmd += ' {}'.format(' '.join(lst))
    for i in range(try_num):
        if CMD_SYSTEM(cmd)==0:
            #没有文件夹 并且 存在文件 返回真
            if not os.path.exists(文件路径+'/') and os.path.exists(save_path):
                return True
    return False
def 获取_网络图片(图片网址: str, headers=None, proxies=None, cookies=None, verify=False, pil=True, show=False, try_num=3) -> PILimage:
    '''获取网络图片("http://...")'''
    for num in range(try_num):
        try:
            with requests.get(图片网址, headers=headers if headers else get_headers('chrome'), proxies=proxies, cookies=cookies, verify=verify) as res:
                if res.status_code == 200:
                    # 返回本地图片内存对象
                    # from PIL import Image
                    # img=Image.open(obj)  打开图片
                    # Image._show(img) 显示图片
                    img = BytesIO(res.content)
                    if pil:
                        img = PILimage.open(img)
                        if show:
                            PILimage._show(img)
                        return img
                    else:
                        return img
                else:
                    raise Exception('获取网络图片错误')
        except Exception as e:
            if num == (try_num - 1):
                raise Exception('{},{}'.format(e.args, e.__traceback__.tb_lineno))
def 获取_网络文件(文件网址: str, headers=None, proxies=None, cookies=None, verify=False, try_num=3) -> bytes:
    for num in range(try_num):
        try:
            with requests.get(文件网址, headers=headers if headers else get_headers('chrome'), proxies=proxies, cookies=cookies, verify=verify) as res:
                if res.status_code == 200:
                    return res.content
                else:
                    raise Exception('获取网络文件错误')
        except Exception as e:
            if num == (try_num - 1):
                raise Exception('{},{}'.format(e.args, e.__traceback__.tb_lineno))
def 获取_本地IP(proxy=None, timeout=30, try_num=3) -> json:
    for num in range(try_num):
        try:
            url = 'http://pv.sohu.com/cityjson?callback='
            res = requests.get(url, timeout=timeout, proxies=proxy, verify=False).text.strip(
                'var returnCitySN =').strip(';').strip()
            return json.loads(res)
        except Exception as e:
            if num == (try_num - 1):
                raise Exception('获取IP错误,{},{}'.format(e.args, e.__traceback__.tb_lineno))
def 多线程运行(列表, 运行函数, 回调函数=None, 线程数=10, 异步=True):
    pool = ThreadPoolExecutor(max_workers=线程数)
    if 异步:
        for item in 列表:
            if 回调函数:
                pool.submit(运行函数, item).add_done_callback(lambda x: 回调函数(x.result()))  # 异步写入 有锁
            else:
                pool.submit(运行函数, item)  # 异步无锁
        pool.shutdown(wait=True)
    else:
        # 同步
        tasks = [pool.submit(运行函数, item) for item in 列表]  # 异步爬取 无锁
        pool.shutdown(wait=True)
        if 回调函数:
            for task in tasks:
                回调函数(task)  # 同步写入
def 异步函数(func, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

# 实用类
class XPATH(etree.ElementBase):
    def __init__(self, html: str,显示不可见元素=True):
        '''类型str bytes etree._Element  display True 显示左右  False只显示可见'''
        if type(html) == str or type(html) == bytes:
            self.xp = etree.HTML(html)
        elif type(etree._Element):
            self.xp = etree.ElementTree(html)
        else:
            raise Exception('xpath输入类型错误:{}'.format(type(html)))
        if not 显示不可见元素: #只显示可见元素
            self.删除不可见元素()

    def title(self) -> str:
        return self.xp.xpath('normalize-space(string(//title//text()))')

    def 取首元素(self, 表达式: str, xpath=False, 去换行=False) -> str or etree._Element:
        '''
        第一个元素 //title
        第一个元素属性 //title/text()
        xpath 是否返回XPATH对象
        '''
        元素 = self.xp.xpath(表达式)
        if 元素:
            if 去换行:
                return self.取文本去掉换行(元素[0])  # 返回字符串
            elif xpath:
                return self.load(元素[0])
            else:
                return 元素[0]  # 返回元素
        else:
            return None

    def 取尾元素(self, 表达式: str, xpath=False, 去换行=False):
        元素 = self.xp.xpath(表达式)
        if 元素:
            if 去换行:
                return self.取文本去掉换行(元素[-1])  # 返回字符串
            elif xpath:
                return self.load(元素[-1])
            return 元素[-1]
        else:
            return None

    def 取多个元素(self, xpath_str: str, xpath=False , 去换行=False):
        '''
        多个元素 //img
        多个属性 //img/@src
        '''
        元素列表 = self.xp.xpath(xpath_str)
        if 去换行:
            return self.取文本去掉换行(元素列表)  # 返回字符串列表
        elif xpath:
            return [self.load(x) for x in 元素列表]
        else:
            return 元素列表

    def 取文本(self,元素:etree._Element=None,拼接符=' ')->str:
        if 元素:
            return 拼接符.join(元素.xpath('.//text()'))
        else:
            return 拼接符.join(self.xp.xpath('.//text()'))

    def 取文本去掉换行(self, 表达式或元素: str or etree._Element) -> str or etree._Element:
        '''
        表达式 //a
        多个元素 出入多个元素
        单个元素
        '''
        a = 表达式或元素
        if type(a) == list:
            return [x.xpath('normalize-space(.)') for x in a]
        elif type(a) == etree._Element:
            return a.xpath('normalize-space(.)')
        elif type(a) == str:
            a = self.xp.xpath(a)
            return [x.xpath('normalize-space(.)') if type(x) == etree._Element else x for x in a]

    def 取正则查询元素(self, 表达式: str, 属性: str, 正则语句: str) -> list:
        s = '{}[re:match({},"{}")]'.format(表达式, 属性, 正则语句)
        return self.xp.xpath(s, namespaces={"re": "http://exslt.org/regular-expressions"})

    def 模糊查询元素(self, 表达式: str, dic: dict) -> list:
        '''
        xp.模糊查询('//a', {'text()':'美女','@src':True,'@data':False})
        '''
        s = []
        for k, v in dic.items():
            s.append('contains({},{})'.format(k, v if type(v) == bool else "\"{}\"".format(v)))
        s = ' and '.join(s)
        表达式 = '{}[{}]'.format(表达式, s)
        return self.xp.xpath(表达式)

    def 元素集取属性(self, 元素集: list, 表达式: str, 取首个: bool = True) -> list:
        if 取首个:
            return [x.xpath('string({})'.format(表达式)) for x in 元素集]
        else:
            return [x.xpath(表达式) for x in 元素集]

    def 取同级下个元素(self, 元素: etree._Element, 标签: str, N=1) -> etree._Element:
        表达式 = 'following-sibling::{}[{}]'.format(标签, N)
        res = 元素.xpath(表达式)
        return res[0] if res else None

    def 取同级上个元素(self, 元素: etree._Element, 标签: str, N=1) -> etree._Element:
        表达式 = 'preceding-sibling::{}[{}]'.format(标签, N)
        res = 元素.xpath(表达式)
        return res[0] if res else None

    def 取HTML(self, 元素: etree._Element, 编码='utf-8') -> str:
        return etree.tostring(元素, encoding=编码).decode(编码)

    def 删除不可见元素(self,元素: etree._Element=None)->None:
        if 元素:
            lst= 元素.xpath('//*[re:match(@style,"{}")]'.format("display[\s]*:[\s]*none"), namespaces={"re": "http://exslt.org/regular-expressions"})
        else:
            lst= self.xp.xpath('//*[re:match(@style,"{}")]'.format("display[\s]*:[\s]*none"), namespaces={"re": "http://exslt.org/regular-expressions"})
        [elem.getparent().remove(elem) for elem in lst]

    @zsq_try
    def 取表格(self, 表格或表达式: etree._Element, 列: list = [],显示不可见元素=True, 去换行=False) -> list:
        ''' （'//table',[1,2]）'''
        table = []
        if type(表格或表达式)==str:
            元素 = self.取首元素(表格或表达式)
        else:
            元素 = 表格或表达式
        if not 显示不可见元素:
            self.删除不可见元素(元素)
        trs = 元素.xpath('.//tr')
        for tr in trs:
            tds = tr.xpath('.//td')
            if tds:  # 排除空的
                if 去换行:  # 取文本
                    tds = [self.取文本去掉换行(x) for x in tds]
                table.append(tds)
        if 列:
            return [[y for i, y in enumerate(x) if i in 列] for x in table]
        return table

    def xpath(self, *args, **keyargs):
        return self.xp.xpath(*args, **keyargs)

    def load(self, 元素: etree._Element):
        '''返回etree对象'''
        return XPATH(元素)
class RUNTIME():
    def __init__(self):
        pass

    def start(self):
        print('<<<' + '-' * 6)
        self.t1 = time.time()

    def end(self):
        self.t2 = time.time()
        print('-' * 6 + '>>>{:.5f}秒'.format(self.t2 - self.t1))
class MAIL():
    def __init__(self):
        self.服务器 = "smtp.qq.com"  # 设置服务器
        self.用户名 = "wgnms@qq.com"  # 用户名
        self.密码 = ""  # 第三方密码
        self.发件人 = 'wgnms@qq.com'  # 发件人
        self.收件人 = ['758000298@qq.com', 'wgnms@qq.com']  # 收件人
        self.附件 = None  # 文件绝对路径

    def send_mail(self, 标题="邮件测试标题", 邮件内容='邮件发送测试内容', 网页=True):
        try:
            if 网页:
                message = MIMEText(邮件内容, 'html', 'utf-8')
            else:
                message = MIMEText(邮件内容, 'plain', 'utf-8')
            message['Subject'] = 标题
            message['From'] = self.发件人
            message['To'] = ','.join(self.收件人)
            smtpObj = SMTP()
            smtpObj.connect(self.服务器, 25)  # 25 为 SMTP 端口号
            smtpObj.login(self.用户名, self.密码)
            smtpObj.sendmail(self.发件人, self.收件人, message.as_string())
            print("邮件发送成功 {}".format(','.join(self.收件人)))
            return True
        except BaseException as e:
            print("Error: 邮件发送失败")
            return False
class SESSION():
    def __init__(self, cookiePath='cookie.txt'):
        self.sess = requests.session()
        if os.path.exists(cookiePath):
            self.cookiePath = cookiePath
            self.sess.cookies = cookiejar.LWPCookieJar(cookiePath)
            try:
                # 加载cookie文件，ignore_discard = True,即使cookie被抛弃，也要保存下来
                self.sess.cookies.load(ignore_expires=True, ignore_discard=True)
            except:
                pass
        else:
            self.cookiePath = None

    def get(self, *args, **kwargs):
        resp = self.sess.get(*args, **kwargs)
        if self.cookiePath:
            self.sess.cookies.save()
        return resp

    def post(self, *args, **kwargs):
        resp = self.sess.post(*args, **kwargs)
        if self.cookiePath:
            self.sess.cookies.save()
        return resp
class PYPP():
    def __init__(self, headless=False, executablePath=None, width=1080, height=800, userDataDir=None, 启用拦截器=False,timeout=20):
        '''
        :param headless:
        :param executablePath:浏览器exe文件路径
        :param width:
        :param height:
        :param userDataDir: userDataDir='brower_temp'     None 不记录登录状态  填写数据目录则记录登录状态
        :param 启用拦截器:
        :param timeout:
        '''
        self.timeout = timeout * 1000
        self.headless = headless  # 无头模式 False
        self.executablePath = executablePath  # r'D:\pycharm_project\ChromePortable\App\Google Chrome\chrome.exe',
        self.width = width
        self.height = height
        self.userDataDir = userDataDir  # r'D:\pycharm_project\ChromePortable\Data\User Data', #用户地址

        self.option_networkidle0 = {'waitUntil': 'networkidle0', 'timeout': self.timeout}  # 在 500ms 内没有任何网络连接
        self.option_domcontentloaded = {'waitUntil': 'domcontentloaded', 'timeout': self.timeout}  # 状态树构建完成
        self.option_networkidle2 = {'waitUntil': 'networkidle2', 'timeout': self.timeout}  # 在 500ms 内网络连接个数不超过 2 个
        self.option_load = {'waitUntil': 'load', 'timeout': self.timeout}
        self.option_timeout = {'timeout': self.timeout}
        self.启用拦截器 = 启用拦截器
        self.help = '''
        page.waitForXPath：等待 xPath 对应的元素出现，返回对应的 ElementHandle 实例
        page.waitForSelector ：等待选择器对应的元素出现，返回对应的 ElementHandle 实例
        page.waitForResponse ：等待某个响应结束，返回 Response 实例
            await page.waitForResponse("https://www.qq.com")
            await page.waitForResponse(lambda res:res.url=="https://www.qq.com" and res.status==200)
        page.waitForRequest：等待某个请求出现，返回 Request 实例
            await page.waitForRequest("https://www.qq.com")
            await page.waitForeRequest(lambda req:req.url=="https://www.qq.com" and res.mothed=="GET")
        page.waitForFunction：等待在页面中自定义函数的执行结果，返回 JsHandle 实例
            await self.pypp.page.waitForFunction('showButtons')  填函数名
        page.waitFor：设置选择器 或者 方法 或者 等待时间
        
        self.page.on("request",lambda x:print(x.url()))  不需要开拦截器

        page.goto：打开新页面
        page.goBack ：回退到上一个页面
        page.goForward ：前进到下一个页面
        page.reload ：重新加载页面
        page.waitForNavigation：等待页面跳转
        '''

    async def 设置UserAgent(self,user_agent):
        await self.page.setUserAgent(user_agent)

    async def 加载浏览器(self,user_agent=None, opthon=None):
        from pyppeteer import launch,launcher
        # from pyppeteer.network_manager import Request, Response
        # from pyppeteer.dialog import Dialog

        # from pyppeteer import launcher
        # if '--enable-automation' in launcher.DEFAULT_ARGS:
        #     launcher.DEFAULT_ARGS.remove('--enable-automation')

        if not opthon:
            opthon = {
                'headless': self.headless,  #  是否以”无头”的模式运行,，即是否显示窗口，默认为 True(不显示)
                'defaultViewport':{'width':self.width,'height':self.height},
                'devtools': False,  # F12控制界面的显示，用来调试
                'ignoreHTTPSErrors': True,  # 是否忽略 Https 报错信息，默认为 False
                'executablePath': self.executablePath, # r'D:\pycharm_project\ChromePortable\App\Google Chrome\chrome.exe'
                'dumpio': True,  # 防止多开导致的假死
                'autoClose': True,  # 删除临时文件
                'args': [
                    '--mute-audio',  # 静音
                    f'--window-size={self.width + 20},{self.height}',#设置浏览器窗口大小，保持和页面大小一致
                    #"--proxy-server=http://127.0.0.1:80",  #添加代理
                    #'--disable-infobars',                  #不显示信息栏，比如：chrome正在受到自动测试软件的控制
                    #"--start-maximized",                    # 最大化窗口
                    #'--no-sandbox',                        #取消沙盒模式，放开权限
                    # '--disable-extensions',  # 禁用拓展
                    # '--disable-gpu',
                    # '--disable-xss-auditor',
                ],
                'ignoreDefaultArgs':[
                    '--enable-automation',
                ]
            }
            if self.userDataDir:
                opthon['userDataDir'] = self.userDataDir  # 用户地址
        self.brower = await launch(opthon)
        self.page = await self.brower.newPage()
        if user_agent:
            await self.page.setUserAgent(user_agent)
        await self.page.setJavaScriptEnabled(enabled=True)
        self.page.setDefaultNavigationTimeout(1000 * self.timeout)  # 跳转超时
        await self.page.setViewport(viewport={'width': self.width, 'height': self.height})
        if self.启用拦截器:
            await self.page.setRequestInterception(True)
            #self.page.on("request",lambda x:print(x.url()))
            self.page.on("request", lambda x: asyncio.ensure_future(self.request拦截器(x)))
            self.page.on("response", lambda x: asyncio.ensure_future(self.response拦截器(x)))
            self.page.on('dialog', lambda x: asyncio.ensure_future(self.dialog拦截器(x)))
        # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
        await self.page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        await self.page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await self.page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''');
        await self.page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    async def 获取页面(self, url, 跳转=False):
        while True:
            try:
                if 跳转:
                    await asyncio.gather(
                        self.page.goto(url, options=self.option_timeout),
                        self.page.waitForNavigation(options=self.option_networkidle0)
                    )
                    return await self.page.content()
                else:
                    await self.page.goto(url, options=self.option_timeout)
                    return await self.page.content()
            except Exception as e:
                打印错误(e)

    async def 关闭浏览器(self):
        await self.brower.close()

    async def 元素属性(self, elem, attr: str = 'textContent'):
        '''元素 或者 元素列表'''
        if type(elem) == list:
            return [await self.page.evaluate('item=>item.{}'.format(attr), x) for x in elem]
        else:
            return await self.page.evaluate('item=>item.{}'.format(attr), elem)

    async def 设置COOKIE(self, cookie: str, domain='v.qq.com'):
        cookie = dict_From_CookieStr(cookie)
        [await self.page.setCookie({'name': k, 'value': v, 'domain': domain}) for k, v in cookie.items()]

    async def 获取COOKIE_IFRAME(self,iframe=0):
        return await self.page.evaluate(""" document.getElementsByTagName("iframe")[%(i)s].contentWindow.document.cookie """%{'i':str(iframe)})

    async def 获取COOKIE(self):
        # return await self.page.evaluate('document.cookie', force_expr=True)
        cookie=await self.page.cookies()
        rt=[]
        for c in cookie:
            rt.append(f"{c['name']}={c['value']}")
        return ';'.join(rt)

    async def 等待页面跳转(self, options):
        '''跳转超时'''
        await self.page.waitForNavigation(options=options if options else self.option_networkidle0)

    async def request拦截器(self, req):
        # from pyppeteer.network_manager import Request, Response
        resourceType = req.resourceType
        if resourceType in ['image']:  # 不加载资源文件
            await req.continue_()
            # ['document','stylesheet','image','media','font','script','texttrack','xhr','fetch','eventsource','websocket','manifest','other']
            # print('跳过图片',req.url)
            # await req.abort()
        elif 'searchCount' in req.url:
            '''
                * ``url`` (str): If set, the request url will be changed.
                * ``method`` (str): If set, change the request method (e.g. ``GET``).
                * ``postData`` (str): If set, change the post data or request.
                * ``headers`` (dict): If set, change the request HTTP header.
            '''
            data={"url": "https://www.qq.com/", 'method':"GET", }
            await req.continue_(data)  # 修改url为xxx
        else:
            await req.continue_()

    async def response拦截器(self, resp):
        # from pyppeteer.network_manager import Request, Response
        if 'searchCount' in resp.url:
            response = await resp.text()
            print(response)# 获得请求的text内容
            # js = await resp.json()
            # print(response)

    async def dialog拦截器(self, dialog):
        pass
        # from pyppeteer.dialog import Dialog
        # print(dialog.message)  # 打印出弹框的信息
        # print(dialog.type)  # 打印出弹框的类型，是alert、confirm、prompt哪种
        # print(dialog.defaultValue())#打印出默认的值只有prompt弹框才有
        # await page.waitFor(2000)  # 特意加两秒等可以看到弹框出现后取消
        # await dialog.dismiss()

        # await dialog.accept('000') #可以给弹窗设置默认值

    async def 执行js_return(self, js代码):
        '''
        login_token = await pypp.执行js_return('window.localStorage.token')
        :param js代码:
        :return:
        '''
        return await self.page.evaluate('''() =>{ return %s; }''' % js代码)

    async def 执行js(self,js代码):
        return await self.page.evaluate('''() =>{ %s }'''%js代码)

    def 异步函数(self, func, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
class FFMPEG():
    def __init__(self, ffmpeg_href="", fpath=""):
        default_dir=os.path.join(os.path.expanduser('~'), 'FFMPEG')
        os.makedirs(default_dir,exist_ok=1)
        path =os.path.join(default_dir, "ffmpeg.exe")
        self.ffmpeg_path = fpath if fpath else path #本地优先级大于下载
        self.ffmpeg_href = ffmpeg_href
    def 合并视频音频(self,文件路径,音频文件,视频文件):
        cmd=f'"{self.ffmpeg_path}" -i {os.path.abspath(视频文件)} -i {os.path.abspath(音频文件)} -vcodec copy -acodec copy -y {os.path.abspath(文件路径)}'
        self.执行(cmd)
    def ffmpeg_分离器合并(self,文件路径="out.mp4",文件名:str='file.txt'):
        #  ffmpeg -f concat -i filelist.txt -c copy output.mkv
        cmd=f'"{self.ffmpeg_path}" -f concat -safe 0 -i "{文件名}" -y -c copy "{文件路径}"'
        self.执行(cmd,show=1)
    def ffmpeg_拼接合并(self,文件路径="out.mp4",视频列表=[]):
        # ffmpeg -i "concat:input1.mpg|input2.mpg|input3.mpg" -c copy output.mpg
        s='|'.join(视频列表)
        cmd = f'"{self.ffmpeg_path}" -i concat"{s}" -y -c copy {文件路径}'
        self.执行(cmd,show=1)
    def ffmpeg_转格式合并(self,文件路径="out.mp4",ts目录=''):
        #00001.temp 00002.temp ...
        cmd=f'"{self.ffmpeg_path}" -i "1.temp" -c copy -f mpegts -bsf:v h264_mp4toannexb "1.ts"'
        cmd = f'copy /b "{os.path.abspath(ts目录)}\*.ts" "{文件路径}.temp"'
        cmd = f'"{self.ffmpeg_path}" -i "{os.path.abspath(文件路径)}.temp" -c copy -bsf:a aac_adtstoasc "{os.path.abspath(文件路径)}"'
    def 合并音频mp3(self,文件路径="out.mp3",音频列表=[]):
        #ffmpeg64.exe -i "concat:123.mp3|124.mp3" -acodec copy output.mp3
        音频列表=[os.path.abspath(x) for x in 音频列表]
        cmd='{} -i "concat:{}"  -c:a libfdk_aac copy {}'.format(self.ffmpeg_path, '|'.join(音频列表),os.path.abspath(文件路径))
        self.执行(cmd)
    def 合并音频m4a(self,文件路径='out.m4a',音频列表=[]):
        '''
        合并 m4a mp3
        ffmpeg -i file1.m4a -acodec copy file1.aac
        ffmpeg -i file2.m4a -acodec copy file2.aac
        ffmpeg -i "concat:file1.aac|file2.aac" -c copy result.aac
        ffmpeg -i result.aac -acodec copy -bsf:a aac_adtstoasc filenew.m4a
        '''
        import shutil  #删除aac文件夹
        try:
            os.makedirs('aac', exist_ok=1)
            all_files = {}
            for x in 音频列表:
                fpath, fname = os.path.split(x)
                ft = fname.rsplit('.', 1)
                name = ft[0]
                if len(ft) == 2:
                    hz = ft[1]
                else:
                    hz = ''
                all_files[int(name)] = {'name': name, 'path': x, 'dir': os.path.abspath(fpath), 'type': hz}
            all_files = sorted(all_files.items(), key=lambda k: k[0], reverse=False)
            path_aac = os.path.abspath('aac')
            if os.path.exists(path_aac):
                shutil.rmtree(path_aac)
            os.makedirs('aac', exist_ok=1)
            for i, file in enumerate(all_files):
                tp = file[1]['type']
                if tp == 'mp3':
                    cmd = f'"{self.ffmpeg_path}" -y -i {file[1]["path"]} -acodec aac -strict experimental -ab 128k -ar 16k -ac 2 {os.path.abspath("aac/{}.aac".format(file[0]))}'
                elif tp == 'm4a' or tp == '':
                    cmd = f'"{self.ffmpeg_path}" -y -i {file[1]["path"]} -acodec copy {os.path.abspath("aac/{}.aac".format(file[0]))}'
                else:
                    raise Exception('文件类型{}'.format(tp))
                self.执行(cmd)
                # print('\r {}/{}'.format(i+1,len(all_files)),end='',flush=1)
            files = [os.path.abspath(f'aac/{x[0]}.aac') for x in all_files]
            resutl_aac = os.path.abspath("result.aac")
            resutl_m4a = os.path.abspath(文件路径)
            cmd2 = f'"{self.ffmpeg_path}" -i "concat:{"|".join(files)}" -c copy -y {resutl_aac}'
            self.执行(cmd2)
            cmd3 = f'"{self.ffmpeg_path}" -i {resutl_aac} -acodec copy -y {resutl_m4a}'
            self.执行(cmd3)
            if os.path.exists(resutl_aac):
                os.remove(resutl_aac)
            if os.path.exists(path_aac):
                shutil.rmtree(path_aac)
            return True
        except Exception as e:
            打印错误(e)
            return False
    def 执行(self,cmd,show=None):
        if not os.path.exists(self.ffmpeg_path):
            if not self.ffmpeg_href:
                self.ffmpeg_href=FFMPEG_HREF
            下载文件_进度条(文件路径=self.ffmpeg_path, 网址=self.ffmpeg_href)
        if show:
            return CMD_SUBPROCESS_CALL(cmd,类型=2)
        else:
            return CMD_SUBPROCESS_CALL(cmd)
class PROXY():
    def __init__(self):
        '''
        设置代理
        enable: 0关闭，1开启
        proxyIp: 代理服务器ip及端口，如 "192.168.70.127:808"
        IgnoreIp:忽略代理的ip或网址，如 "172.*;192.*;"
        '''
        self.KEY_ProxyEnable = "ProxyEnable"
        self.KEY_ProxyServer = "ProxyServer"
        self.KEY_ProxyOverride = "ProxyOverride"
        self.KEY_XPATH = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    def 设置代理(self,开启=1, 代理IP='127.0.0.1:8080', 白名单=""):
        '''
        :param 开启: 1 或者 0
        :param 代理IP: 127.0.0.1:8080;127.0.0.1:8888
        :param 白名单: 127.*;10.*;172.16.*;
        :return:
        '''
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY_XPATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(hKey, self.KEY_ProxyEnable, 0, winreg.REG_DWORD, 开启)
        winreg.SetValueEx(hKey, self.KEY_ProxyServer, 0, winreg.REG_SZ, 代理IP)
        winreg.SetValueEx(hKey, self.KEY_ProxyOverride, 0, winreg.REG_SZ, 白名单)
        winreg.CloseKey(hKey)
    def 获取代理(self)->list:
        '''返回列表[{},{}]'''
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY_XPATH, 0, winreg.KEY_READ)
        retVal = winreg.QueryValueEx(hKey, self.KEY_ProxyEnable)
        开启=retVal[0]
        if 开启:
            res = winreg.QueryValueEx(hKey, self.KEY_ProxyServer)
            # http=127.0.0.1:8888;https=127.0.0.1:8888
            lst=res[0].split(';')
            lst= list(set([x.split('=',1)[1] if '=' in x else x for x in lst ]))
            return [{'http':f'http://{x}','https':f'http://{x}'} for x in lst]
        else:
            return []
    def get_proxies(self)->dict:
        '''返回列表{} 或者 None'''
        hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.KEY_XPATH, 0, winreg.KEY_READ)
        retVal = winreg.QueryValueEx(hKey, self.KEY_ProxyEnable)
        开启 = retVal[0]
        if 开启:
            res = winreg.QueryValueEx(hKey, self.KEY_ProxyServer)
            # http=127.0.0.1:8888;https=127.0.0.1:8888
            lst = res[0].split(';')
            lst = list(set([x.split('=', 1)[1] if '=' in x else x for x in lst]))
            return {'http': f'http://{lst[0]}', 'https': f'http://{lst[0]}'} if lst else None
        else:
            return None
class SOCKET():
    def __init__(self, host: str = '127.0.0.1', port: int = 8888,连接数=10,byteSize=1024):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.conn_number=连接数
        self.__close__=False
        self.byteSize=byteSize
    def __监听__(self,callback=None):
        self.__close__ = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(self.addr)
        sock.listen(self.conn_number)#连接数
        print('运行socket监听:{}'.format(self.addr))
        while not self.__close__:
            try:
                client, addr0 = sock.accept()
                data = client.recv(self.byteSize)
                if data:
                    if callback:
                        callback(data)
                    else:
                        print('socket接收到:{}'.format(data))
            except Exception as e:
                print(e,e.__traceback__.tb_lineno)
            time.sleep(0.2)
        print('已退出socket监听')
    def 运行监听(self,回调函数=None):
        self.__close__ = False
        th=threading.Thread(target=self.__监听__,args=(回调函数,))
        th.setDaemon(True)
        th.start()
    def 发送消息(self, data: bytes):
        try:
            sock = socket.socket()
            sock.connect(self.addr)
            sock.send(data)
            sock.close()
        except Exception as e:
            打印错误(e)
    def 关闭服务(self):
        self.__close__=True
class COM_SERIAL():
    def __init__(self, port=None,description='', baudrate=115200, bytesize=1024, timeout=None, writeTimeout=None):
        '''
        port 端口
        baudrate 波特率
        bytesize 字节大小
        '''
        self.port=port
        self.description=description
        self.ser=serial.Serial()
        self.ser.baudrate=baudrate
        self.bytesize = bytesize
        self.timeout=timeout
        self.writeTimeout = writeTimeout
        self.连接串口()
        self.__close__=False
    def 连接串口(self):
        while True:
            try:
                if self.ser.isOpen() == True:
                    self.ser.close()
                else:
                    if self.port:
                        self.ser.port = self.port
                    elif self.description:
                        for x in self.串口列表():
                            if self.description in x.description:
                                self.ser.port = x.name
                                break
                        self.ser.open()
                        if self.ser.isOpen()==True:
                            print('已连接串口:{}'.format(x.description))
                            return
                    else:
                        return None
            except Exception as e:
                打印错误(e)
            time.sleep(0.5)
    def __监听__(self,callback=None):
        while not self.__close__:
            try:
                if self.ser.isOpen():
                    data = self.ser.readline()
                    if data:
                        if callback:
                            callback(data.strip())
                        else:
                            print('收到串口数据:{}'.format(data.strip()))
                else:
                    self.连接串口()
            except Exception as e:
                打印错误(e)
                self.连接串口()
            time.sleep(0.2)
        if self.ser.isOpen():
            self.ser.close()
        print('已退出串口:{}'.format(self.ser.port))
    def 串口列表(self):
        return list(serial.tools.list_ports.comports())
    def 关闭串口(self):
        self.__close__=True
    def 运行监听(self,回调函数=None):
        th=threading.Thread(target=self.__监听__,args=(回调函数,))
        th.setDaemon(True)
        th.start()
class 监听程序运行():
    def __init__(self, 程序EXE路径:str):
        self.程序EXE路径=程序EXE路径
        if isinstance(self.程序EXE路径, str):
            self.run_pid=subprocess.Popen(r'{}'.format(self.程序EXE路径), stdout=None, stderr=None, shell=False)
        else:
            raise Exception('cmd格式要求字符串')
        self.__close__ = False
    def __监听__(self):
        if self.run_pid:
            print('正在监听程序:{}'.format(self.程序EXE路径))
            stdoutdata, stderrdata = self.run_pid.communicate(input=None, timeout=None)
            print('stdoutdata:{}'.format(stdoutdata))
            print('stderrdata:{}'.format(stderrdata))
            # 没有强制退出
            if self.run_pid:
                code = self.run_pid.returncode  # returncode 0 正常退出
                print('returncode:{}'.format(code))
                if code != 0:
                    print('程序已异常退出')
                else:
                    print('程序已正常退出')
            # 强制退出了
            else:
                print('程序已强制退出')
            self.run_pid = False
    def 运行监听(self):
        th=threading.Thread(target=self.__监听__)
        th.setDaemon(True)
        th.start()
    def 关闭程序(self):
        if self.run_pid:
            try:
                self.run_pid.kill()
            except:
                pass
        self.run_pid=False
class 电脑信息():
    def __init__(self):
        '''
        wmic diskdrive 可以看出来牌子和大小.
        Wmic logicaldisk 每一个盘的文件系统和剩余空间
        wmic cpu
        wmic memorychip
        wmic bios

        '''
        pass
    def wmic_format(self, cmd):
        '''
        cmd='wmic cpu get name /format:list'
        wmic csproduct get name,uuid,vendor /format:list
        '''
        with os.popen(cmd) as f:
            res = f.read()  # 获取管道信息
        rt={}
        for x in res.split('\n'):
            if x.strip():
                a=x.split('=',1)
                rt[a[0].lower()]=a[1]
        return rt
    def wmic(self,cmd):
        with os.popen(cmd) as f:
            res = f.readlines()  # 获取管道信息
        keys=[x for x in res[0].split(' ') if x.strip()]
        cmd=cmd+' get {} /format:list'.format(','.join(keys))
        rt = self.wmic_format(cmd)
        return rt
    def 主机名(self):
        return socket.gethostname()
    def 网卡(self):
        return psutil.net_if_addrs()
    def 内网IP(self):
        return socket.gethostbyname_ex(self.主机名())[-1]
    def 硬盘分区(self):
        return psutil.disk_partitions()
    def 内存(self):
        return psutil.virtual_memory()
    def 系统开机时间(self):
        return datetime.datetime.fromtimestamp(psutil.boot_time ()).strftime("%Y-%m-%d %H: %M: %S")
    def 磁盘(self):
        硬盘空间=[]
        for disk in psutil.disk_partitions():
            try:
                硬盘空间.append(psutil.disk_usage(disk.device))
            except Exception as e:
                pass
        return 硬盘空间
    def 接收流量(self):
        return '{0:.2f} Mb'.format(self.mb(psutil.net_io_counters().bytes_recv))
    def 发送流量(self):
        return '{0:.2f} Mb'.format(self.mb(psutil.net_io_counters().bytes_sent))
    def 用户(self):
        return psutil.users()
    def mb(self,kb):
        return kb/1024/1024
    def 主板信息(self):
        return self.wmic('wmic csproduct')
    def cpu(self):
        return self.wmic('wmic cpu')
class 弹窗():
    def 信息框(标题, 文本):
        import win32api, win32con
        win32api.MessageBox(None, 文本, 标题, win32con.MB_OK | win32con.MB_ICONQUESTION)
    def 选择框(标题, 文本):
        import win32api, win32con
        x = win32api.MessageBox(None, 文本, 标题, win32con.MB_YESNO | win32con.MB_DEFBUTTON1 | win32con.MB_ICONINFORMATION)
        return True if x == 6 else False  # 7
    def 选择文件夹(标题='选择文件夹'):
        from tkinter import Tk
        from tkinter import filedialog
        root = Tk()
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        path = filedialog.askdirectory(title=标题)
        root.destroy()
        return path
    def 选择文件(路径: str = '', 标题: str = '选择文件', 文件类型: list = []):
        '''文件类型 [['图片',"*.jpg"],[]]'''
        from tkinter import Tk
        from tkinter import filedialog
        root = Tk()
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        fname = filedialog.askopenfilename(title=标题, initialdir=路径 if 路径 else ".", filetypes=文件类型)
        root.destroy()
        return fname
    def 输入数字(标题:str='整数录入',文本说明:str='请输入整数'):
        from tkinter import Tk
        from tkinter import simpledialog
        root = Tk()
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        d = simpledialog.askinteger(title=标题,prompt=文本说明,initialvalue=0)
        root.destroy()
        return d
    def 输入浮点(标题:str='浮点录入',文本说明:str='请输入浮点数'):
        from tkinter import Tk
        from tkinter import simpledialog
        root = Tk()
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        d = simpledialog.askfloat(title=标题,prompt=文本说明,initialvalue=0.0)
        root.destroy()
        return d
    def 输入字符串(标题:str='字符串录入',文本说明:str='请输入字符串'):
        from tkinter import Tk
        from tkinter import simpledialog
        root = Tk()
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        d = simpledialog.askstring(title=标题,prompt=文本说明,initialvalue='')
        root.destroy()
        return d
class 随机():
    def __init__(self):
        pass
    @classmethod
    def 随机字符串(cls,字符串,长度):
        rt = []
        for i in range(长度):
            rt.append(random.choice(字符串))
        return ''.join(rt)
    @classmethod
    def 数字(cls,长度:int=20)->str:
        return cls.随机字符串(string.digits,长度)
    @classmethod
    def 大写字母(cls,长度:int=20)->str:
        return cls.随机字符串(string.ascii_uppercase,长度)
    @classmethod
    def 小写字母(cls, 长度: int=20) -> str:
        return cls.随机字符串(string.ascii_lowercase, 长度)
    @classmethod
    def 字母(cls, 长度: int=20) -> str:
        return cls.随机字符串(string.ascii_letters, 长度)
    @classmethod
    def 字母数字(cls, 长度: int=20) -> str:
        return cls.随机字符串(string.ascii_letters + string.digits,长度)
    @classmethod
    def 字母数字特殊符号(cls, 长度: int=20) -> str:
        return cls.随机字符串(string.ascii_letters + string.digits + string.punctuation,长度)
    @classmethod
    def 列表随机一个(cls,列表:list):
        assert 列表, '随机列表空'
        return random.choice(列表)
    @classmethod
    def 列表随机多个(cls,列表:list,个数)->list:
        assert 列表, '随机列表空'
        assert len(列表)>个数,'随机大于总长度'
        return random.sample(列表,个数)
class 结构体():
    def dict(self):
        return self.__dict__
    def keys(self):
        return list(self.__dict__.keys())
    def values(self):
        return list(self.__dict__.values())
class 过滤字符串():
    def __init__(self):
        self.keys=[]
        self.flag=False
    def 设置_关键字(self,keys=''):
        self.keys=[x.strip() for x in keys.strip().split(' ') if x.strip()]
    def 查找_关键字(self,name='',打印跳过=1):
        if not self.flag and all([x in name for x in self.keys]):
            self.flag=True
        if 打印跳过:
            if not self.flag:
                print('跳过',name)
        return self.flag
if __name__ == '__main__':
    pass