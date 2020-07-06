Vue.component('drawing', {
    props: {
        enabled: Boolean
    },
    data() {
        return {
            canvas: null,
            context: null,
            isDrawing: false,
            width: 5,
            startX: 0,
            startY: 0,
            points: []
        }
    },
    mounted() {
        this.canvas = this.$refs.canvas;
        this.context = this.canvas.getContext("2d");
        this.canvas.addEventListener('mousedown', this.mousedown);
        this.canvas.addEventListener('mousemove', this.mousemove)
        this.canvas.addEventListener('mouseup', this.mouseup);
        this.handleCanvasResize();
        window.addEventListener("resize", this.handleCanvasResize, false);
    },
    template: '<canvas style="background: white;" ref="canvas"></canvas>',
    methods: {
        mousedown(e) {
            if (this.enabled) {
                var rect = this.canvas.getBoundingClientRect();
                var x = e.clientX - rect.left;
                var y = e.clientY - rect.top;

                this.isDrawing = true;
                this.startX = x;
                this.startY = y;
                this.points.push({
                    x: x,
                    y: y
                });
            }
        },
        mousemove(e) {
            if (this.enabled) {
                var rect = this.canvas.getBoundingClientRect();
                var x = e.clientX - rect.left;
                var y = e.clientY - rect.top;

                if (this.isDrawing) {
                    this.context.beginPath();
                    this.context.moveTo(this.startX, this.startY);
                    this.context.lineTo(x, y);
                    this.context.lineWidth = this.width;
                    this.context.lineCap = 'round';
                    this.context.strokeStyle = "rgba(0,0,0,1)";
                    this.context.stroke();

                    this.startX = x;
                    this.startY = y;

                    this.points.push({
                        x: x,
                        y: y
                    });

                    this.$emit('draw', { x: x, y: y })
                }
            }
        },
        drawPoint(x, y) {
            this.context.beginPath();
            this.context.moveTo(this.startX, this.startY);
            this.context.lineTo(x, y);
            this.context.lineWidth = this.width;
            this.context.lineCap = 'round';
            this.context.strokeStyle = "rgba(0,0,0,1)";
            this.context.stroke();

            this.startX = x;
            this.startY = y;
        },
        draw(points) {
            if (points.length) {
                this.startX = points[0].x
                this.startY = points[0].y
                for (let i = 1; i < points.length; i++) {
                    if (points[i - 1].stop) {
                        this.startX = points[i].x
                        this.startY = points[i].y
                    }
                    this.drawPoint(points[i].x, points[i].y)
                }
            }
        },
        setLineWidth(width) {
            this.width = width
        },
        mouseup(e) {
            if (this.enabled) {
                this.isDrawing = false;
                this.points[this.points.length - 1].stop = true
            }
        },
        resetCanvas() {
            this.handleCanvasResize()
        },
        handleCanvasResize() {
            this.canvas.width = this.canvas.parentElement.clientWidth
            this.canvas.height = this.canvas.parentElement.clientHeight
            this.points.length = 0
        }
    }
})

