function check_browser(){
    if("WebSocket" in window){
        return true
    }else{
        document.getElementById("html").innerHTML = "<h1>您的浏览器暂不支持Websocket, 请更换浏览器!</h1>"
        return false
    }
}