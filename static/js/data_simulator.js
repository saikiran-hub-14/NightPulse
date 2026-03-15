function generateData(){

let heart = Math.floor(Math.random()*60)+70
let temp = (Math.random()*3+36).toFixed(1)

document.getElementById("heart").innerText = heart
document.getElementById("temp").innerText = temp

}

setInterval(fetchAlerts,5000)
