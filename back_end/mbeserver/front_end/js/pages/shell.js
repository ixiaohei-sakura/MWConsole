function display_message(msg, cf, usrname){
    if((MWCONSOLE.shell_output.scrollHeight > MWCONSOLE.shell_output.clientHeight) || (MWCONSOLE.shell_output.offsetHeight > MWCONSOLE.shell_output.clientHeight)){
        for (let i = MWCONSOLE.shell_output.childNodes.length - 1; i >= 0; i--){
            MWCONSOLE.shell_output.removeChild(MWCONSOLE.shell_output.childNodes[i]);
        }
    }
    let tmp_ = document.createElement("span")
    tmp_.innerHTML = "[" + cf + "@" + usrname + "]" + "&nbsp;&nbsp;"
    tmp_.style = "color: #4cae4c"
    MWCONSOLE.shell_output.appendChild(tmp_)
    tmp_ = document.createElement("span")
    tmp_.innerHTML = msg + "<br>"
    MWCONSOLE.shell_output.appendChild(tmp_)
}

function get_command(e){
    let theEvent = window.event || e
    let code = theEvent.keyCode || theEvent.which || theEvent.charCode
    MWCONSOLE.shell_input.cache = MWCONSOLE.shell_input.element.value
    if(code === 13 && MWCONSOLE.shell_input.cache.length !== 0){
        MWCONSOLE.shell_input.element.value = ""
        if(MWCONSOLE.shell_input.cache.indexOf("#bash")>=0){MWCONSOLE.shell_input.type=0}
        else if(MWCONSOLE.shell_input.cache.indexOf("#shell")>=0){MWCONSOLE.shell_input.type=1}
        else {MWCONSOLE.shell_input.type=2}
        send_command(MWCONSOLE.shell_input.type, MWCONSOLE.shell_input.cache)
        MWCONSOLE.shell_input.cache = ""
    }
}

function send_command(type, cmd){
    if(type === 0){display_message(MWCONSOLE.shell_input.cache, "server_bash", "root")}
    else if(type === 1){display_message(MWCONSOLE.shell_input.cache, "server_shell", "root")}
    else if(type === 2){display_message(MWCONSOLE.shell_input.cache, "ws_shell", MWCONSOLE.username)}
}

function load_shell(){
    MWCONSOLE.shell_input = {}
    MWCONSOLE.shell_input.cache = "none"
    MWCONSOLE.shell_input.type = -1
    MWCONSOLE.shell_input.element = document.getElementById("shell_input")
    MWCONSOLE.shell_output = document.getElementById("shell_output")
    MWCONSOLE.shell_input.element.onkeydown = function(e){get_command(e)}

    display_message("MWEBCONSOLE "+MWCONSOLE.version.front_end, "SYS", "I")
    display_message("目前终端: "+MWCONSOLE.shell_name, "SYS", "I")
    display_message("TIPS: 输入命令，回车以执行MCDR或服务器命令，可以执行shell&bash命令。执行shell or bash命令请加上#bash或#shell", "SYS", "I")
}

function ShellPage(){
    load_shell()
}