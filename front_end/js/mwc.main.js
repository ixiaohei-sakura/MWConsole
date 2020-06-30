if (check_browser() === true){
    window.MWCONSOLE = {}
    console.info("["+get_time()+"]"+" 浏览器检查成功")

    //############常量############//
    MWCONSOLE.username = "none" //临时
    //定义什么是啥也没有
    MWCONSOLE.none = -1
    //版本，更新则变化
    MWCONSOLE.version = {}
    MWCONSOLE.version.front_end = "pre-v0.0.1"
    MWCONSOLE.version.back_end = "pre-v0.0.1"
    //############结束############//

    // 启动程序
    MWCONSOLE.mwc_sys = new MWC_SYSTEM()

    // 全局化ws和窗口控制
    MWCONSOLE.now_window = "main"
    MWCONSOLE.info("初始化成功")
}
else
{
    console.error("["+get_time()+"]"+" 浏览器检查失败 请更换浏览器!")
}