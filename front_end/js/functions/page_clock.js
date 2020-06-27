function get_time(){
    let vWeek,vWeek_s
    vWeek = ["星期天","星期一","星期二","星期三","星期四","星期五","星期六"]
    let date =  new Date()
    let year = date.getFullYear()
    let month = date.getMonth() + 1
    let day = date.getDate()
    let hours = date.getHours()
    let minutes = date.getMinutes()
    let seconds = date.getSeconds()
    vWeek_s = date.getDay()
    return (year + "年" + month + "月" + day + "日" + "\t" + hours + ":" + minutes +":" + seconds + "\t" + vWeek[vWeek_s])
}

function now_t(){
    let e = document.getElementById("now_time")
    function progress(){
        e.innerHTML = get_time()
    }
    setInterval(progress, 300)
}