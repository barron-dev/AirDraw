const {ipcRenderer} = require('electron')

var vue = new Vue({
    el: "#app",
    data:{
        username: null,
        gameId: null,
        useCamera: false
    },
    methods:{
        startGame: function(){
            window.location = `lobby.html?username=${this.username}&useCamera=${this.useCamera}`
        }
    }
})

