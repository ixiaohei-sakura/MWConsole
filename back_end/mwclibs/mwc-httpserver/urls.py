"""mwc-httpserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
import socket
import json
import time
import queue

def enjson(_type: str, value: str):
    tmp = {
        "type":"",
        "ping":"",
        "cmd":"",
        "cmd_return":""
    }
    tmp['type'] = _type
    tmp[_type] = value
    return bytes(json.dumps(tmp), encoding='UTF-8')

def dejson(msg: str):
        buff = json.loads(msg)
        try:
            if type(buff) == str:
                raise TypeError
        except:
            buff = json.loads(buff)
        class _return:
            msg: str
            msgtype: str
            full: dict
            msgtype = buff['type']
            msg = buff[buff['type']]
            full = buff
        return _return

class Socket_handle():
    def open(self: classmethod):
        try:
            self.socket = socket.socket
            tmp = self.load_config()
            self.ADDR = (tmp['SOCKET']['ADDR'], tmp['SOCKET']['PORT'])
            self.socket.connect(self.ADDR)
            self.socket.recv(1024)
            self.socket.sendall(enjson('id', 'django_info'))
            tmp = self.socket.recv(1024).decode('utf-8')
            tmp = dejson(tmp)
            if not tmp.msg.find('id_ok'):
                self.close()
        except Exception as exc:
            raise exc

    def close(self: classmethod):
        try:
            self.socket.shutdown(2)
            self.socket.close()
        except Exception as exc:
            raise exc

    def reload(self: classmethod):
        self.close()
        self.open()

    def load_config(self: classmethod):
        with open('./configs/config.json', 'r') as f:
            tmp = f.read()
        return json.loads(tmp)

    def keep_server_alive(self: classmethod):
        if len(self.socket.recv(1024).decode('utf-8')) == 0:
            self.reload()
    
    def req(self: classmethod, request: WSGIRequest, http_return, name='login', name2='', name3='', soc_return=None, status_code='200', soc_status='OK'):
        if soc_return == None:
            self.socket.sendall(enjson('django_info', '\033[1;32m[HTTP1.1/GET {0}:200 STATUS OK] {1}'.format(name, "\033[1;33mtime:\033[0m [\033[1;32m"+time.strftime('%H:%M:%S', time.localtime())+"\033[0m]")))
        else:
            self.socket.sendall(enjson('django_info', '\033[1;33m[HTTP1.1/GET {0}:{1} STATUS {2}] {3}'.format(soc_return, status_code, soc_status, "\033[1;33mtime:\033[0m [\033[1;32m"+time.strftime('%H:%M:%S', time.localtime())+"\033[0m]")))
        return HttpResponse(http_return)


soc_handle = Socket_handle()
def MWC_url_handle(request: WSGIRequest, name='login', name2='', name3=''):
    if name == 'login':
        return soc_handle.req(request, enjson('msg', "Hello, world. You're at the polls index."+time.strftime('%H:%M:%S', time.localtime())+request.get_full_path()), name=name, name2=name2, name3=name3)
    return soc_handle.req(request, '404 , NotFound ):', name=name, name2=name2, name3=name3, soc_return=request.path, status_code='404', soc_status='NF')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<name>/', MWC_url_handle),
    path('<name>/<name2>/', MWC_url_handle),
    path('<name>/<name2>/<name3>', MWC_url_handle),
]