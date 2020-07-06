const {ipcRenderer} = require('electron')

var vue = new Vue({
    el: "#app",
    data:{
        username: null,
        gameId: null
    },
    methods:{
        startGame: function(){
            window.location = 'lobby.html?username=' + this.username
        }
    }
})

