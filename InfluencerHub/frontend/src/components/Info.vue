<template>
  <div
    class="d-flex flex-column justify-content-center gap-2 align-items-center"
  >
    <h3>Welcome Admin!</h3>
    <BCard header="Ongoing Campaigns:" class="w-75">
      <BListGroup>
        <BListGroupItem
          href="#"
          v-for="i in activecampaigns"
          :key="i.id"
          class="list-group-item mb-1 d-flex justify-content-between w-100"
          >{{ name }} | {{ i.end_data
          }}<BCol><BButton>View</BButton></BCol></BListGroupItem
        >
      </BListGroup>
    </BCard>
    <BCard header="Flagged Users/Campaigns:" class="w-75">
      <BListGroup>
        <BListGroupItem href="#" class="list-group-item mb-1"
          >Cras justo odio</BListGroupItem
        >
      </BListGroup>
    </BCard>
  </div>
</template>

<script>
import axios from "axios";
import { BCard } from "bootstrap-vue-next";
import { onMounted, ref } from "vue";

export default {
  name: "Info",
  setup() {
    const activecampaigns = ref([]);
    const today = ref(null);
    const loadSession = async () => {
      try {
        const { data } = await axios.get("http://localhost:5000/getcampaings");
        activecampaigns.value = data;
        today.value = new Date().toLocaleString();
        console.log(today, activecampaigns);
      } catch (err) {
        console.log(err);
      }
    };

    onMounted(() => {
      loadSession();
    });
    return {
      activecampaigns,
    };
  },
};
</script>

<style>
.list-group-item {
  border-radius: 0.25rem; /* Adjust the radius as needed */
}
</style>
