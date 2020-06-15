"""MwebConsole URL Configuration

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

def keep_server_alive():
    s = socket.socket()
    with open('./configs/config.json', 'r') as f:
        tmp = f.read()
    tmp = json.loads(tmp)
    addr = tmp['SOCKET']['ADDR']
    port = tmp['SOCKET']['PORT']
    ADDR = (addr, port)
    s.connect(ADDR)
    if len(s.recv(1024).decode('utf-8')) == 0:
        raise SystemExit

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

def req(request: WSGIRequest, http_return, name='login', name2='', name3='', soc_return=None, status_code='200', soc_status='OK'):
    s = socket.socket()
    with open('./configs/config.json', 'r') as f:
        tmp = f.read()
    tmp = json.loads(tmp)
    addr = tmp['SOCKET']['ADDR']
    port = tmp['SOCKET']['PORT']
    ADDR = (addr, port)
    s.connect(ADDR)
    s.recv(1024)
    s.sendall(enjson('id', 'django_info'))
    if soc_return == None:
        s.sendall(enjson('django_info', '[HTTP1.1/GET {0}:200 STATUS OK] {1}'.format(name, "\033[1;33mtime:\033[0m [\033[1;32m"+time.strftime('%H:%M:%S', time.localtime())+"\033[0m]")))
    else:
        s.sendall(enjson('django_info', '[HTTP1.1/GET {0}:{1} STATUS {2}] {3}'.format(soc_return, status_code, soc_status, "\033[1;33mtime:\033[0m [\033[1;32m"+time.strftime('%H:%M:%S', time.localtime())+"\033[0m]")))
    s.shutdown(2)
    s.close()
    return HttpResponse(http_return)



def login(request: WSGIRequest, name='login', name2='', name3=''):
    if name == 'login':
        return req(request, enjson('msg', "Hello, world. You're at the polls index."+time.strftime('%H:%M:%S', time.localtime())+request.get_full_path()), name=name, name2=name2, name3=name3)
    return req(request, '404 , NotFound ):', name=name, name2=name2, name3=name3, soc_return=request.path, status_code='404', soc_status='NF')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<name>/', login),
    path('<name>/<name2>/', login),
    path('<name>/<name2>/<name3>', login),
]
