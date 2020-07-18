import sys
import traceback
from .constants import *
import json


def log_call(func):
    def print_(*args):
        if getdebug():
            print(*args)

    def inner(*args, **kwargs):
        if getdebug() is True:
            print_(f"\033[1;36m[DEBUG/调试信息输出]函数: {func.__name__} 被: {traceback.extract_stack()[-2][2]} 调用! "
                   f"函数参数大小: {len(args)}\033[0m")
            for arg in args:
                print_(f"\033[1;36m -类型: {type(arg).__name__}, 内容: {arg}\033[0m")
        else:
            pass
        return func(*args, **kwargs)

    return inner


class ServerStatus:
    ISTARTING = "服务器正在启动/SERVER_is_starting"
    ISRUNNING = "服务器正在运行/SERVER_is_running"
    ISTOPPING = "服务器正在停止/SERVER_is_stopping"
    STOPED_by_it_self = "服务器已自行停止/SERVER_stoped_by_ITSELF"
    STOPED_by_func_call = "服务器被函数调用停止/SERVER_stoped_by_func_call"
    ISRESTARTING = "服务器正在重新启动/SERVER_is_restarting"


class server:
    tick = 0.05

    class __console__:
        stdout = sys.stdout
        stdin = sys.stdin
        stderr = sys.stderr


@log_call
def setdebug(debugMode: bool, tmp=True):
    print(f"调试模式: {debugMode}")
    if type(debugMode) is not bool:
        raise TypeError("DEBUG MODE IS A BOOL")
    else:
        with open(os.path.join(tmp_dir_path, "debug"), "w") as f:
            if tmp is False:
                tmp = read_config()
                tmp["DEBUG"] = debugMode
                write_config(tmp)
            return f.write(str(debugMode))


def getdebug():
    with open(os.path.join(tmp_dir_path, "debug"), "r") as f:
        if f.read() == "True":
            return True
        elif f.read() == "False":
            return False
        else:
            return None


@log_call
def stop_server(_self, _a_=False):
    print('')
    _self.Mlogger.logger(0, 'STOPPING', name='STATUS')
    if _a_ is False:
        _self.stop()
    _self.Monitor.stop_monitor()
    _self.ws_handle.stop_ws()
    _self.Mlogger.logger(0, f"服务器状态: {_self.server_status}")
    _self.Mlogger.logger(0, 'Thank you and goodBye! :)')


@log_call
def rm_tmp():
    try:
        os.remove(tmp_dir_path)
    except:
        pass


@log_call
def read_config():
    try:
        with open(config_file_path, "r") as f:
            return json.loads(f.read())
    except Exception:
        raise Exception


@log_call
def write_config(config):
    try:
        try:
            os.mkdir(config_dir_path)
        except:
            pass
        with open(config_file_path, "w") as f:
            if type(config) is dict:
                f.write(json.dumps(config, indent=3))
                return
            else:
                f.write(config)
    except Exception:
        raise Exception


try:
    os.remove(tmp_dir_path)
except:
    pass
try:
    os.mkdir(tmp_dir_path)
except:
    pass

try:
    setdebug(read_config()["DEBUG"])
except:
    setdebug(True)
