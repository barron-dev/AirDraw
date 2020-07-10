var socket = io.connect('http://127.0.0.1:5000/')
let vue = new Vue({
    el: '#app',

    data: {
        username: null,
        useCamera: false,
        userId: null,
        isLeader: false,
        ready: false,
        error: false,
        message: null,
        chat: [],
        players: [],
        points: [],
        currentWord: '',
        wordOptions: [],
        drawing: false,
        canDraw: false,
        showWordModal: false,
        showPlayerModal: false,
        showScoreModal: false,
        currentRound: 0,
        roundCount: 0,
        roundTime: 0,
        currentPlayer: 0,
        scores: []
    },

    created() {
        let usp = new URLSearchParams(window.location.search)
        this.username = usp.get('username')
        this.useCamera = (usp.get('useCamera') == 'true')
    },

    mounted() {
        socket.on('connect', () => {
            this.error = false
        })

        socket.on('connect_error', () => {
            this.error = true
        })

        socket.on('assign-id', (data) => {
            this.userId = data.id
            if (data.players.length === 0)
                this.isLeader = true
            socket.emit('assign-name', ({
                name: this.username,
                id: this.userId
            }))
            for (let i = 0; i < data.players.length; i++) {
                this.new_player(data.players[i].id, data.players[i].name)
            }
        })

        socket.on('start-game', (data) => {
            this.ready = true
            this.roundCount = data.roundCount
            this.roundTime = data.roundTime
        });

        socket.on('user-connected', (data) => {
            this.new_player(data.id, data.name)
        })

        socket.on('user-disconnected', (data) => {
            for (let i = 0; i < this.players.length; i++) {
                if (this.players[i].id == data.id) {
                    this.players.splice(i, 1)
                }
            }
        })

        socket.on('chat-message', (data) => {
            this.chat.push({
                type: data.type,
                name: this.getName(data.id),
                text: data.text
            })
            $(".chat-list").stop().animate({ scrollTop: $(".chat-list")[0].scrollHeight}, 450);
        })

        socket.on('user-draw', (data) => {
            this.$refs.board.draw(data.points)
        })

        socket.on('clear-board', () => {
            this.$refs.board.resetCanvas()
        })

        socket.on('word-selection', (data) => {
            this.canDraw = true
            this.wordOptions = data.words
            this.showWordModal = true
        })

        socket.on('next-turn', (data) => {
            this.$nextTick(() => {
                this.stopCountdown()
                this.currentPlayer = data.id
                console.log(`data: ${data.id}, user: ${this.userId}`)
                this.canDraw = data.id == this.userId
                this.$refs.board.resetCanvas()
                this.showPlayerModal = !this.canDraw
                this.currentRound = data.round
                for (let i = 0; i < data.scores.length; i++) {
                    this.setScore(data.scores[i].id, data.scores[i].score)
                }
            })
        })

        socket.on('start-turn', (data) => {
            if (!this.canDraw)
                this.currentWord = data.hint
            this.showPlayerModal = false
            this.startCountdown()
        })

        socket.on('game-finished', () => {
            this.scores = this.players.sort((a, b) => b.score - a.score)
            this.showScoreModal = true
            socket.disconnect()
        })

    },

    methods: {
        sendMsg: function () {
            if (!this.canDraw)
                socket.emit('chat-message', { id: this.userId, type: 1, text: this.message })
            this.message = null
        },

        startGame: function () {
            socket.emit('start-game')
        },

        clearBoard: function () {
            this.$refs.board.resetCanvas()
            socket.emit('clear-board')
        },

        getName: function (id) {
            for (let i = 0; i < this.players.length; i++) {
                if (this.players[i].id === id) {
                    return this.players[i].name
                }
            }
        },

        handleDraw: function (point) {
            if (!this.drawing) {
                this.drawing = true
                setTimeout(() => {
                    this.drawing = false
                    this.sendPoints()
                }, 100)
            }
            this.points.push({
                x: point.x,
                y: point.y
            })
        },

        wordSelected: function (word) {
            this.showWordModal = false
            this.currentWord = word
            socket.emit('word-selected', { word: word })
        },

        sendPoints: function () {
            this.points[this.points.length - 1].stop = true
            socket.emit('user-draw', { points: this.points })
            this.points.length = 0
        },

        startCountdown: function () {
            this.$refs.timer.start()
        },

        stopCountdown: function () {
            this.$refs.timer.stop()
        },

        countdownFinished: function () {
            // if(this.canDraw){
            //     setTimeout(() => {
            //         socket.emit('done-drawing')
            //         console.log('im emitting finish')
            //     }, 500)
            // }
        },

        new_player: function (id, name) {
            this.players.push({
                id: id,
                name: name,
                score: 0,
                isDrawing: false
            })
        },

        setScore: function (id, score) {
            for (let i = 0; i < this.players.length; i++) {
                if (this.players[i].id === id) {
                    this.players[i].score = score
                    break
                }
            }
        },

        mainMenu: function () {
            window.location = 'index.html'
        }


    }
})

