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
from django.urls import path
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
import socket
import json
import os


class Http:
    def __init__(self):
        self.socket = socket.socket
        tmp = self.load_config()
        self.ADDR = (tmp['SOCKET']['ADDR'], tmp['SOCKET']['PORT'])

    def load_config(self):
        with open(os.path.join("config", "config.json"), 'r') as f:
            tmp = f.read()
        return json.loads(tmp)

    def keep_server_alive(self):
        if len(self.socket.recv(1024).decode('utf-8')) == 0:
            self.reload()


http = Http()


def MWC_url_handle(request: WSGIRequest, name='', name2='', name3=''):
    if name.find("js") >= 0:
        if name2.find(".js") >= 0:
            with open(f"./front_end/js/{name2}") as f1:
                return HttpResponse(content=f1.read(), charset="utf-8", content_type="text/javascript", status=200)
        elif name3.find(".js") >= 0:
            with open(f"./front_end/js/{name2}/{name3}") as f2:
                return HttpResponse(content=f2.read(), charset="utf-8", content_type="text/javascript", status=200)
        return HttpResponse(content="", charset="utf-8", content_type="text/javascript", status=500)
    elif name.find("css") >= 0:
        if name2.find(".css") >= 0:
            with open(f"./front_end/css/{name2}") as f1:
                return HttpResponse(content=f1.read(), charset="utf-8", content_type="text/css", status=200)
        elif name3.find(".css") >= 0:
            with open(f"./front_end/css/{name2}/{name3}") as f2:
                return HttpResponse(content=f2.read(), charset="utf-8", content_type="text/css", status=200)
        return HttpResponse(content="", charset="utf-8", content_type="text/css", status=500)
    elif name.find("image") >= 0:
        if name2.find(".png") >= 0 or name2.find(".jpg") >= 0 or name2.find(".jpeg") >= 0 or name2.find(".ico") >= 0 or name2.find(".icon") >= 0:
            with open(f"./front_end/images/{name2}", "rb") as f1:
                image_data = f1.read()
                print(name2)
                return HttpResponse(image_data, content_type="image/png")
        elif name3.find(".png") >= 0 or name3.find(".jpg") >= 0 or name3.find(".jpeg") >= 0 or name3.find(".ico") >= 0 or name3.find(".icon") >= 0:
            with open(f"./front_end/images/{name2}/{name3}", "rb") as f2:
                image_data = f2.read()
                return HttpResponse(image_data, content_type="image/png")
        return HttpResponse(content="", status=500)
    else:
        with open("./front_end/main_page.html", "rb") as f3:
            return HttpResponse(content=f3.read(), charset="utf-8", content_type="text/html", status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MWC_url_handle),
    path('<name>', MWC_url_handle),
    path('<name>/', MWC_url_handle),
    path('<name>/<name2>', MWC_url_handle),
    path('<name>/<name2>/', MWC_url_handle),
    path('<name>/<name2>/<name3>', MWC_url_handle),
    path('<name>/<name2>/<name3>/', MWC_url_handle),
]
