Vue.component('modal', {
    template: `
    <transition name="modal">
        <div class="modal-mask">
          <div class="modal-wrapper">
              <slot></slot>
          </div>
        </div>
      </transition>
    `
})
