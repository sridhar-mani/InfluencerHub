<template>
  <div
    class="d-flex flex-column justify-content-center gap-2 align-items-center"
  >
    <h3>Welcome Admin!</h3>
    <BCard header="Ongoing Campaigns:" class="w-75">
      <BListGroup>
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Cras justo odio</BListGroupItem
        >
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Dapibus ac facilisis in</BListGroupItem
        >
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Vestibulum at eros</BListGroupItem
        >
      </BListGroup>
    </BCard>
    <BCard header="Flagged Users/Campaigns:" class="w-75">
      <BListGroup>
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Cras justo odio</BListGroupItem
        >
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Dapibus ac facilisis in</BListGroupItem
        >
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Vestibulum at eros</BListGroupItem
        >
      </BListGroup>
    </BCard>
  </div>
</template>

<script>
import { BCard } from "bootstrap-vue-next";

export default {
  name: "Info",
};
</script>

<style>
.list-group-item {
  border-radius: 0.25rem; /* Adjust the radius as needed */
}
</style>
