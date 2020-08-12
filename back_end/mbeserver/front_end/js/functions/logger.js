function init_mlog(){
    MWCONSOLE.info = function (info){
        console.info("["+get_time()+"] "+ info)
    }
    MWCONSOLE.warn = function (warn){
        console.warn("["+get_time()+"] "+ warn)
    }
    MWCONSOLE.error = function (erro){
        console.error("["+get_time()+"] "+ erro)
    }
}