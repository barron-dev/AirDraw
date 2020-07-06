const {ipcRenderer} = require('electron')

var vue = new Vue({
    el: "#app",
    data:{
        username: null,
        gameId: null
    },
    methods:{
        startGame: function(){
            if(this.username != null){
                window.location = 'lobby.html?username=' + this.username
            }
        }
    }
})

