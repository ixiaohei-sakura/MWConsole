function page_display(element){
    let main = document.getElementById("MainPage")
    let servermanage = document.getElementById("ServerManage")
    let shell = document.getElementById("Shell")
    let login = document.getElementById("login")
    if(element === "main"){
        login.style.display = "none"
        servermanage.style.display = "none"
        shell.style.display = "none"
        main.style.display = ""
        MainPage()
        load_page()
        MWCONSOLE.info("主页面加载")
    }
    else if(element === "sm"){
        login.style.display = "none"
        shell.style.display = "none"
        main.style.display = "none"
        servermanage.style.display = ""
        ServerManagePage()
        load_page()
        MWCONSOLE.info("服务器管理页面加载")
    }
    else if(element === "shell"){
        login.style.display = "none"
        main.style.display = "none"
        servermanage.style.display = "none"
        shell.style.display = ""
        ShellPage()
        load_page()
        MWCONSOLE.info("终端页面加载")
    }
    else if(element === "login"){
        shell.style.display = "none"
        main.style.display = "none"
        servermanage.style.display = "none"
        login.style.display = ""
        LoginHandle()
        load_page()
        MWCONSOLE.info("登录页面加载")
    }
}