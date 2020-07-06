Vue.component('countdown', {
    props: {time: Number},
    data(){
        return {countdown: 0}
    },
    template: '<p>{{countdown}}</p>',
    created(){
        this.countdown = this.time
    },
    methods: {
        start() {
            if(this.countdown <= 0)
                this.countdown = this.time
            this.startR()
        },
        startR() {
            if(this.countdown > 0) {
                setTimeout(() => {
                    this.countdown -= 1
                    this.startR()
                }, 1000)
            }
            else{
                this.$emit('finished')
            }
        },
        stop() {
            this.countdown = 0
        }
    }
})