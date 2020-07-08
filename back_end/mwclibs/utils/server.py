import platform

try:
    from .constants import *
    from .mlogger import *
    from .fespc import *
    from .socserver import *
    from .wsocserver import *
    from .checkupdate import *
    from .server_status import *
    from .lang.init_lang import *
except ImportError:
    from mwclibs.utils.constants import *
    from mwclibs.utils.mlogger import *
    from mwclibs.utils.fespc import *
    from mwclibs.utils.socserver import *
    from mwclibs.utils.wsocserver import *
    from mwclibs.utils.checkupdate import *
    from mwclibs.utils.server_status import *
    from mwclibs.utils.lang.init_lang import *


class Server_Control:
    class ConfigFileNotFound(Exception):
        pass

    def __init__debug__(self):
        try:
            setdebug(read_config()["DEBUG"])
        except:
            setdebug(False)
        print("debugMode: ", getdebug())

    def __init__(self, args):
        self.server = None
        self.ws_handle = None
        self.soc_handle = None
        self.update_checker = None
        self.msg = None
        self.__process = None
        self.stop_and_exit = None

        self.Mlogger = MLogger()

        self.buff = ""
        self.pycmd = ""
        self.lang = ""
        self.saddr = ""
        self.sport = ""
        self.wsaddr = ""
        self.wsport = ""
        self.port = 0
        self.ahost = []

        self.__init__debug__()
        self.__check_file__()
        self.Mlogger = MLogger()

        self.__init_server__()

    @log_call
    def start_server(self):
        """
        启动全部
        :return:
        """
        self.Mlogger.logger(0, 'StartServerProcess', name='ProcessManager')
        self.server = FrontEndServerProcessControl(self.Mlogger, '{0} manage.py runserver 0:{1}'.format(
            read_config()['PYCMD'], read_config()['WEBPORT']), ensoc=True, wsoc=self.ws_handle,
                                                   soc=self.soc_handle, Monitor=True)
        threading.Thread(target=self.__console_input__, daemon=True).start()
        self.__print_messag__()
        self.server.join()
        while True:
            # 接下来进入服务器状态判断循环
            if self.server.server_status == ServerStatus.STOPED_by_func_call:
                # 当服务器是被函数调用所停止的，那么接着循环
                time.sleep(server.tick)
            if self.server.server_status == ServerStatus.ISRESTARTING:
                # 当服务器是被函数调用重启
                self.server.start()
            if self.server.server_status == ServerStatus.STOPED_by_it_self:
                # 当服务器被用户停止或出现错误时，退出循环，退出主程序.
                time.sleep(server.tick)
                self.Mlogger.logger(0, "退出主程序")
                self.stop_and_exit = True
                break
            self.server.join()
            time.sleep(server.tick)
        if self.stop_and_exit is True:
            return [self.server.server_status, self.server.process.poll()]
        else:
            self.Mlogger.logger(2, "程序未知错误，如果您知道在发生此错误前详细地做了些什么，请向我提交issues并详细的描述，地址: "
                                   "https://github.com/ixiaohei-sakura/MWConsole/issues")
            return [self.server.server_status, self.server.process.poll()]

    @log_call
    def __print_messag__(self):
        self.update_checker = Check_Update(self)
        self.msg = """
    __  ____      _____/\\
   /  |/  / | /| / / ___/
  / /|_/ /| |/ |/ / /__  
 / /  /_/ |__/|__/\___/
 \/"""
        for line in self.msg.splitlines():
            self.Mlogger.logger(0, line)
        self.Mlogger.logger(0, '==== MCDRWEBCONSOLE ====')

        time.sleep(0.5)
        self.Mlogger.logger(0, '正在启动MCDR-WEBCONSOLE')
        self.update_checker.check_update()
        self.Mlogger.logger(0, '上报BUG请联系 ixiaohei:')
        self.Mlogger.logger(0, 'QQ: 486118772')
        self.Mlogger.logger(0, 'mwc-httpserver is OpenSource, find it here:')
        self.Mlogger.logger(0, 'GAYHUB: https://github.com/ixiaohei-sakura/')
        self.Mlogger.logger(0, 'G-PROJECT: https://github.com/ixiaohei-sakura/MWConsole')
        self.Mlogger.logger(0, 'ServerStarted. Quit the server with CONTROL-C')

    @log_call
    def __start_internet_connection__(self):
        try:
            self.ws_handle = WSocket_handle(self.Mlogger, self)
        except:
            self.Mlogger.logger(4, '***BIND PORT ERR***', name='WSocketServer')
            raise SystemExit
        try:
            self.soc_handle = Socket_handle(self.Mlogger, self)
        except Exception as exc:
            print(exc)
            self.Mlogger.logger(4, '***BIND PORT ERR***', name='SocketServer')
            raise SystemExit

    @log_call
    def __init_server__(self):
        self.__start_internet_connection__()
        self.__check_database__()

    @log_call
    def __check_database__(self):
        self.Mlogger.logger(0, '检查必要的数据表', name='ServerCheck')
        self.__process = FrontEndServerProcessControl(self.Mlogger, '{0} manage.py migrate'.format(read_config()["PYCMD"]), Monitor=True, ensoc=False)
        self.__process.join()

    @log_call
    def __console_input__(self):
        time.sleep(3)
        self.Mlogger.logger(0, "==MWC正在监听标准输入流==")
        self.Mlogger.logger(3, "DEBUG模式已打开，MWC终端自动启动DEBUG模式")
        self.Mlogger.logger(0, "命令列表: ")
        self.Mlogger.logger(0, "restart: 重启web服务器")
        self.Mlogger.logger(0, "restart_: 重启MWC")
        self.Mlogger.logger(0, "start: 启动web服务器")
        self.Mlogger.logger(0, "stop: 停止MWC")
        self.Mlogger.logger(0, "stop_: 停止web服务器并等待启动")
        self.Mlogger.logger(0, "debug [True/False]开启/关闭debug模式")
        self.Mlogger.logger(0, "命令需以#m#开头, 例: #m#debug True")
        while True:
            buff = input()
            if buff[0:3] == "#m#":
                buff = buff[3:]
                if buff == "restart":
                    self.server.restart()
                elif buff == "restart_":
                    self.server.restart_program(1)
                elif buff == "start":
                    self.server.start()
                elif buff == "stop":
                    self.server.stop()
                elif buff == "stop_":
                    self.server.stop(func_call=True)
                elif buff == "status":
                    print("状态码: ", self.server.server_status)
                elif buff.find("debug") >= 0:
                    try:
                        buff = buff.split(" ")[1]
                    except Exception as exc:
                        print("GET A exeception: ", str(exc))
                        continue
                    try:
                        if buff == "False":
                            setdebug(debugMode=False, tmp=False)
                        elif buff == "True":
                            setdebug(debugMode=True, tmp=False)
                        else:
                            print("Error")
                    except Exception as exc:
                        print("GET A exeception: ", str(exc))
                        continue
                elif buff.find("rm") >= 0 or buff.find("dd") >= 0:
                    pass
                else:
                    os.system(buff)
            time.sleep(server.tick)

    @log_call
    def __check_config__(self):
        if os.path.isfile(config_file_path) is not True:
            print("=============M=W=C=============\n"
                  " 检测到第一次启动，按照下面的提示去做 \n"
                  "MWConsole后台程序将会指导您配置并使用\n"
                  "任何的配置选项留空则是默认\n"
                  "=============M=W=C=============\n")

            while True:
                buff = input("======选择语言SelectLanguage=====\n"
                             "1. English(US)\n"
                             "2. 中文(简体)\n"
                             "3. 中文(繁体)\n"
                             "请输入序号来选择/Please enter the number to select\n"
                             "此选项将作为MWC默认语言选项，为必需填选\n"
                             "[INPUTNUMBER]> ")
                lang_dict = {1: "en-us", 2: "zh-cn", 3: "zh-tw"}
                try:
                    self.lang = int(buff)
                    self.lang = lang_dict[self.lang]
                except:
                    print("Error, renter please.")
                    print("================================\n\n")
                    continue
                else:
                    init_lang(self.lang)
                    print("================================\n\n")
                    break

            print("首先，请输入下列配置的配置项, 留空以选择默认选项: ")
            print("=============端口设置============")
            while True:
                buff = input("[请输入网页服务器端口]> ")
                if len(buff) is 0:
                    print("端口号未输入，默认为8000")
                    self.port = 8000
                else:
                    try:
                        self.port = int(buff)
                    except:
                        print("不允许输入非数字的端口号!")
                        print("=============M=W=C=============\n")
                        continue
                print(f"已经设置的配置项：端口号:{self.port}")
                if platform.platform().find("Darwin") >= 0:
                    print(f"检测到系统为MACOSX, 版本: {platform.platform()}")
                    if input("[是否需要检查? y/n]> ") is "y":
                        print("正在使用brew安装lsof,安装时间由网络状态决定...")
                        sys.stderr.close()
                        os.system("brew install lsof")
                        sys.stderr = server.__console__.stderr
                        print("正在检查端口合法性...")
                        if len(Popen(f"lsof -i:{self.port}", stdout=PIPE, shell=True).stdout.read()) is not 0:
                            print("测试不通过，请更换端口!")
                            print(f"结果: {Popen(f'lsof -i:{self.port}', stdout=PIPE, shell=True).stdout.read()}")
                            print("=============M=W=C=============\n")
                            continue
                        print(f"端口: {self.port} 可用!")
                elif platform.platform().find("Windows"):
                    print("请自行检查合法性")
                else:
                    print("请自行检查合法性")
                buff = input("[是否确认? y/n]> ")
                if buff is "y":
                    print(f"已经确定的配置项：端口号:{self.port}")
                    print("=============M=W=C=============\n")
                    break
                elif buff is "n":
                    print("取消设定，重新执行")
                    print("=============M=W=C=============\n")
                    continue
                else:
                    print("错误: 请输入 y 或 n")
                    print("=============M=W=C=============\n")
                    continue

            print("请输入下列配置的配置项:")
            print("=============命令设置============, 留空以选择默认选项")
            while True:
                buff = input("示例：python3\n"
                             "[请输入PYTHON命令]> ")

                if len(buff) is not 0:
                    self.pycmd = buff
                else:
                    print("python命令未输入，默认为python3.7")
                    self.pycmd = "python3.7"
                print(f"已经设置的配置项：python命令:{self.pycmd}")
                buff = input("[是否确认? y/n]> ")
                if buff is "y":
                    print(f"已经确定的配置项：python命令:{self.pycmd}")
                    print("=============M=W=C=============\n")
                    break
                elif buff is "n":
                    print("取消设定，重新执行")
                    print("=============M=W=C=============\n")
                    continue
                else:
                    print("错误: 请输入 y 或 n")
                    print("=============M=W=C=============\n")
                    continue

            print("输入允许的访问域,中间用|隔开，例子: 0.0.0.0|localhost|xxx.xxx.xxx.xxx, 留空以选择默认选项")
            print("=============域设置============")
            while True:
                buff = input("[输入上述的设置]> ")
                self.ahost = buff.split("|")
                print("完成，设置项：")
                for value in self.ahost:
                    print(f" -{value}")
                buff = input("[是否确认? y/n]> ")
                if buff is "y":
                    print(f"已经确定的配置项")
                    print("=============M=W=C=============\n")
                    break
                elif buff is "n":
                    print("取消设定，重新执行")
                    print("=============M=W=C=============\n")
                    continue
                else:
                    print("错误: 请输入 y 或 n")
                    print("=============M=W=C=============\n")
                    continue

            print("输入socket的监听地址和监听端口，用:隔开。例子: 127.0.0.1:3547, 留空以选择默认选项")
            print("=============socket设置============")
            while True:
                buff = input("[输入上述的设置]> ")
                if len(buff) is 0:
                    print("端口号未输入，默认为8000")
                    self.sport = 3547
                    print("地址未输入，默认为127.0.0.1")
                    self.saddr = "127.0.0.1"
                else:
                    tmp = buff.split(":")
                    self.saddr = tmp[0]
                    self.sport = tmp[1]
                print("配置项:\n"
                      f"地址: {self.saddr}\n"
                      f"端口: {self.sport}")
                buff = input("[是否确认? y/n]> ")
                if buff is "y":
                    print(f"已经确定的配置项")
                    print("=============M=W=C=============\n")
                    break
                elif buff is "n":
                    print("取消设定，重新执行")
                    print("=============M=W=C=============\n")
                    continue
                else:
                    print("错误: 请输入 y 或 n")
                    print("=============M=W=C=============\n")
                    continue

            print("输入websocket的监听地址和监听端口，用:隔开。例子: 127.0.0.1:3548, 留空以选择默认选项")
            print("=============websocket设置============")
            while True:
                buff = input("[输入上述的设置]> ")
                if len(buff) is 0:
                    print("端口号未输入，默认为8000")
                    self.wsport = 3547
                    print("地址未输入，默认为127.0.0.1")
                    self.wsaddr = "127.0.0.1"
                else:
                    tmp = buff.split(":")
                    self.wsaddr = tmp[0]
                    self.wsport = tmp[1]
                print("配置项:\n"
                      f"地址: {self.wsaddr}\n"
                      f"端口: {self.wsport}")
                buff = input("[是否确认? y/n]> ")
                if buff is "y":
                    print(f"已经确定的配置项")
                    print("=============M=W=C=============\n")
                    break
                elif buff is "n":
                    print("取消设定，重新执行")
                    print("=============M=W=C=============\n")
                    continue
                else:
                    print("错误: 请输入 y 或 n")
                    print("=============M=W=C=============\n")
                    continue

            tmp = {"WEBPORT": self.port, "PYCMD": self.pycmd,
                   "ALLOWED_HOSTS": self.ahost,
                   "LANGUAGE_CODE": "en-us", "TIME_ZONE": "UTC", "STATIC_URL": "/static/",
                   "ROOT_URLCONF": "MwebConsole.urls",
                   "SECRET_KEY": "******=&=^c#s^lm*#fBYIXIA@HEIsxwIXiaO@HeiIS%fu&*kingcreatedthis&^#%^@&("
                                 "*_&*$^$&proJECt#%^&#~!#^#%^@$=f@cx8kc@krrgw!-******",
                   "WSGI_APPLICATION": "MwebConsole.wsgi.application", "USE_I18N": True, "USE_L10N": True,
                   "USE_TZ": True, "DEBUG": True, "MWCLANGCODE": self.lang,
                   "SOCKET": {"ADDR": "127.0.0.1", "PORT": 3547},
                   "WSOCKET": {"ADDR": "127.0.0.1", "PORT": 3548}}
            write_config(tmp)

    @log_call
    def __check_file__(self):
        if os.path.isfile("./configs/config.json") is False:
            self.__check_config__()
        if platform.system().find("Darwin") >= 0:
            os.system("clear")
        elif platform.system().find("Linux") >= 0:
            os.system("clear")
        elif platform.system().find("Windows") >= 0:
            os.system("cls")
        else:
            os.system("clear")
            os.system("cls")


@log_call
def main():
    try:
        print("init server....")
        process = Server_Control(sys.argv)
    except:
        import traceback
        traceback.print_exc()
        print('Fail to initialize Server')
    else:
        # 此函数为阻塞函数, 保持阻塞直到服务器被 ^C 或 kill 停止.
        process.start_server()
        rm_tmp()
        raise SystemExit

# netstat -anp | grep 880

# python3 manage.py migrate 每当第一次启动时执行此命令.
# python3 manage.py createsuperuser --user hei
# python3 manage.py runserver 0:880


# ADDRESS = ('127.0.0.1', 8712)

# g_socket_server = None
# g_conn_pool = []


# init()


# 福利
# 《美少女万华镜》官网：
# PlusWeb http://www.plus01.jp/htdocs/biman/bisyo.html
# 第一话 http://omega-star.jp/bimanhtml/index.html
# 第二话 http://omega-star.jp/biman2html/index.html
# 外传(2.5话) http://omega-star.jp/bimanharuhtml/index.html
# 第三话 http://omega-star.jp/biman3html/index.html
# 第四话 http://omega-star.jp/biman4html/index.html
# 第五话 http://omega-star.jp/biman5html/index.html
# 第五话 http://www.favo-soft.jp/omega-star/biman5html/open.html
