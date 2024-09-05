<template>
  <div
    class="d-flex flex-column justify-content-center gap-2 align-items-center"
  >
    <h3>Welcome Admin!</h3>
    <BCard
      header="Ongoing Campaigns:"
      v-if="activecampaigns.length > 0"
      class="w-75"
    >
      <BListGroup>
        <BListGroupItem
          href="#"
          v-for="i in activecampaigns"
          :key="i.id"
          class="list-group-item mb-1 d-flex justify-content-between w-100"
          >{{ i.name }} | Progress {{ i.end_date
          }}<BCol><BButton>View</BButton></BCol></BListGroupItem
        >
      </BListGroup>
    </BCard>
    <BCard
      v-if="
        campaginsUsers.campaigns.length > 0 || campaginsUsers.users.length > 0
      "
      header="Flagged Users/Campaigns:"
      class="w-75"
    >
      <BListGroup>
        <BListGroupItem
          href="#"
          v-for="i in campaginsUsers.campaigns"
          :key="i.id"
          class="list-group-item mb-1 d-flex justify-content-between w-100"
          >{{ i.name }} | {{ i.company_user
          }}<BCol><BButton>View</BButton></BCol></BListGroupItem
        >
        <BListGroupItem
          href="#"
          v-for="i in campaginsUsers.users"
          :key="i.id"
          class="list-group-item mb-1 d-flex justify-content-between w-100"
          >{{ i.name }} | {{ i.role
          }}<BCol><BButton>View</BButton></BCol></BListGroupItem
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
    const progressMade = ref([]);
    const campaginsUsers = ref({});
    const tempMonth = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    const loadSession = async () => {
      try {
        const { data } = await axios.get("http://localhost:5000/getcampaings");
        const flagged = await axios.get("http://localhost:5000/flagged_data");
        campaginsUsers.value = flagged.data;
        console.log(campaginsUsers.value);
        activecampaigns.value = data;
        today.value = new Date().toLocaleString();
        today.value = today.value.split(", ")[0].split("/");

        activecampaigns.value = activecampaigns.value.map((acctive) => {
          acctive.end_date = acctive.end_date
            .split(", ")[1]
            .split(" ")
            .slice(0, 3);
          acctive.end_date[1] = String(
            tempMonth.findIndex(
              (t) => t.toLowerCase() === acctive.end_date[1].toLowerCase()
            )
          );
          acctive.start_date = acctive.start_date
            .split(", ")[1]
            .split(" ")
            .slice(0, 3);
          acctive.start_date[1] = String(
            tempMonth.findIndex(
              (t) => t.toLowerCase() === acctive.start_date[1].toLowerCase()
            )
          );

          if (
            acctive.end_date[2] === today.value[2] ||
            acctive.end_date[2] > today.value[2]
          ) {
            if (
              acctive.end_date[1] > today.value[1] ||
              acctive.end_date[1] === today.value[1]
            ) {
              if (acctive.end_date[0] > today.value[0]) {
                const days =
                  today.value[0] +
                  acctive.end_date[0] +
                  (acctive.end_date[1] / 2 === 0
                    ? 31 - acctive.end_date[0]
                    : 30 - acctive.end_date[0]) +
                  1;
                let totalDays;
                if (acctive.end_date[1] !== acctive.start_date[1]) {
                  totalDays =
                    Number(acctive.end_date[0]) +
                    Number(
                      acctive.start_date[1] / 2 === 0
                        ? 31 - acctive.start_date[0]
                        : 30 - acctive.start_date[0]
                    );
                } else {
                  totalDays =
                    Number(acctive.end_date[0]) - Number(acctive.start_date[0]);
                }

                progressMade.value = ((totalDays - days) / totalDays) * 100;
                acctive.progressMade = progressMade.value;
              } else {
                return false;
              }
            } else {
              return false;
            }
          } else {
            return false;
          }

          return acctive;
        });
        activecampaigns.value = activecampaigns.value.filter((a) => {
          a !== false;
        });
      } catch (err) {
        console.log(err);
      }
    };

    onMounted(() => {
      loadSession();
    });
    return {
      activecampaigns,
      campaginsUsers,
    };
  },
};
</script>

<style>
.list-group-item {
  border-radius: 0.25rem; /* Adjust the radius as needed */
}
</style>
