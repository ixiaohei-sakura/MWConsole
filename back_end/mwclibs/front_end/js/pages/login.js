function login_submit(){
    let usrname = MWCONSOLE.login.elements.usrid.value
    let psw = MWCONSOLE.login.elements.passwd.value
    MWCONSOLE.info(usrname)
    MWCONSOLE.info(psw)
    window.addEventListener("onkeydown", login_submit, false)
    MWCONSOLE.username = usrname

    MWCONSOLE.info("向服务器发送登录凭据...")
    //首先调用websocket发送凭据
    // 然后等待
    //这里应该有一个websocket的判断..., 像这样
    while(MWCONSOLE.login.credential.token === MWCONSOLE.none||MWCONSOLE.login.credential.prikey === MWCONSOLE.none){}
    MWCONSOLE.info("接收到数据")
    if(MWCONSOLE.login.status.return_status === MWCONSOLE.login.status.server_not_access_content||MWCONSOLE.login.status.return_status === MWCONSOLE.none){MWCONSOLE.info("凭据有未知错误");alert("凭据有未知错误")}
    if(MWCONSOLE.login.status.return_status === MWCONSOLE.login.status.passwd_w){MWCONSOLE.info("密码有错误");alert("密码有错误")}
    if(MWCONSOLE.login.status.return_status === MWCONSOLE.login.status.usr_w){MWCONSOLE.info("用户名有错误");alert("用户名有错误")}
    MWCONSOLE.info("即将跳转")
    page_display("main")
}

function load_login(){
    MWCONSOLE.login = {}
    MWCONSOLE.login.status = {}
    MWCONSOLE.login.credential = {}
    MWCONSOLE.login.elements = {}
    MWCONSOLE.login.credential.token = MWCONSOLE.none
    MWCONSOLE.login.prikey = MWCONSOLE.none
    MWCONSOLE.login.pubkey = MWCONSOLE.none

    //临时的
    MWCONSOLE.login.credential.token = "test_token"
    MWCONSOLE.login.credential.prikey = "awa"
    MWCONSOLE.login.credential.pubkey = "owo"
    //结束

    //状态码开始
    MWCONSOLE.login.status.server_not_access_content = 900
    MWCONSOLE.login.status.passwd_w = 800
    MWCONSOLE.login.status.usr_w = 801
    // MWCONSOLE.login.status.return_status = MWCONSOLE.none
    MWCONSOLE.login.status.return_status = 101
    //结束

    // 凭据变量开始
    MWCONSOLE.login.usrname = MWCONSOLE.none
    MWCONSOLE.login.passwd = MWCONSOLE.none
    // 结束

    // 元素变量开始
    MWCONSOLE.login.elements.usrid = document.getElementById("login-userid")
    MWCONSOLE.login.elements.passwd = document.getElementById("login-passwd")
    MWCONSOLE.login.elements.passwd.onkeydown = MWCONSOLE.login.elements.usrid.onkeydown = function(e){let theEvent = window.event || e;let code = theEvent.keyCode || theEvent.which || theEvent.charCode;MWCONSOLE.login.cache = MWCONSOLE.login.elements.passwd.value;if(code === 13 && MWCONSOLE.login.cache.length !== 0){login_submit()}}
    // 结束
}

function LoginHandle(){
    load_login()
}