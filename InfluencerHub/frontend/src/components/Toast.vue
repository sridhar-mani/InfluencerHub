<template>
  <Teleport to="body">
    <div class="toast-container position-fixed top-0 end-0 p-3">
      <BToast v-if="visible" variant="danger" solid>
        <template #title>{{ title }}</template>
        {{ message }}
      </BToast>
    </div>
  </Teleport>
</template>

<script>
import { ref, watch } from "vue";

export default {
  name: "Toast",
  props: {
    message: {
      type: String,
      default: "",
    },
    show: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: "",
    },
  },
  setup(props, { emit }) {
    const visible = ref(props.show);

    watch(
      () => props.show,
      (newValue) => {
        visible.value = newValue;
        if (newValue) {
          setTimeout(() => {
            visible.value = false;
            emit("update:show", false);
          }, 3000);
        }
      }
    );

    return { visible };
  },
};
</script>

<style scoped>
.toast-container {
  z-index: 1050;
}
</style>
