function login_submit(){
    let usrname = MWCONSOLE.login.elements.usrid.value
    let psw = MWCONSOLE.login.elements.passwd.value
    MWCONSOLE.info(usrname)
    MWCONSOLE.info(psw)
    window.addEventListener("onkeydown", login_submit, false)
    MWCONSOLE.username = usrname

}

function load_login(){
    MWCONSOLE.login = {}
    MWCONSOLE.login.usrname = ""
    MWCONSOLE.login.passwd = ""
    MWCONSOLE.login.elements = {}
    MWCONSOLE.login.elements.usrid = document.getElementById("login-userid")
    MWCONSOLE.login.elements.passwd = document.getElementById("login-passwd")
    window.onkeydown = MWCONSOLE.login.elements.passwd.onkeydown = MWCONSOLE.login.elements.usrid.onkeypress = function(e){let theEvent = window.event || e;let code = theEvent.keyCode || theEvent.which || theEvent.charCode;MWCONSOLE.login.cache = MWCONSOLE.login.elements.passwd.value;if(code === 13 && MWCONSOLE.login.cache.length !== 0){login_submit()}}
}

function LoginHandle(){
    load_login()
}