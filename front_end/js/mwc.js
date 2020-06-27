function MWC_SYSTEM(){
    init_mlog()
    MWCONSOLE.shell_name = "none"
    this.mwc_usr = new MWC_USER()
    this.wsoc = new websocket()
    MWCONSOLE.getElementById = document.getElementById
}

function MWC_USER(){
    function test_page_temp(){
        let a = document.getElementById("title")
        a.innerHTML = "已加载!目前为测试页面"
    }
    document.onload = test_page_temp()

    // document.onload = page_display("shell")
    // document.onload = page_display("main")
    document.onload = page_display("login")
    document.onload = now_t()
}