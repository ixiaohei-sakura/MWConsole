function load_page(){
    let tmp = 0
    document.getElementById("lpb").style.display = ""
    function progress_bar(){
        if(tmp>100){
            clearInterval(timer)
            document.getElementById("lpb").style.display = "none"
            return
        }
        document.getElementById("lp").style.width = tmp+"%"
        tmp++
    }
    let timer = setInterval(progress_bar, 7)
}