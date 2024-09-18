<template>
  <div
    class="admin-dashboard d-flex flex-column justify-content-center gap-4 align-items-center"
  >
    <h3>Welcome Admin!</h3>

    <BCard
      v-if="activecampaigns.length > 0"
      header="Ongoing Campaigns:"
      class="w-75"
    >
      <BListGroup>
        <BListGroupItem
          v-for="campaign in activecampaigns"
          :key="campaign.id"
          class="list-group-item mb-2 d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>{{ campaign.name }}</strong>
            <small class="text-muted">
              | Progress: {{ campaign.progressMade }}%</small
            >
          </div>
          <div class="d-flex justify-content-end gap-2">
            <BButton variant="success" size="sm">View</BButton>
            <BButton variant="danger" size="sm">Remove</BButton>
          </div>
        </BListGroupItem>
      </BListGroup>
    </BCard>

    <BCard
      v-if="
        campaignUsers.campaigns?.length > 0 || campaignUsers.users?.length > 0
      "
      header="Flagged Users/Campaigns:"
      class="w-75"
    >
      <BListGroup>
        <BListGroupItem
          v-for="item in campaignUsers.campaigns"
          :key="item.id"
          class="list-group-item mb-2 d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <small class="text-muted"> | {{ item.company_user }}</small>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <BButton variant="success" size="sm">View</BButton>
            <BButton variant="danger" size="sm">Remove</BButton>
          </div>
        </BListGroupItem>

        <BListGroupItem
          v-for="user in campaignUsers.users"
          :key="user.id"
          class="list-group-item mb-2 d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>{{ user.name }}</strong>
            <small class="text-muted"> | {{ user.role }}</small>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <BButton variant="success" size="sm">View</BButton>
            <BButton variant="danger" size="sm">Remove</BButton>
          </div>
        </BListGroupItem>
      </BListGroup>
    </BCard>

    <BCard
      v-if="unapprovedUsers.length > 0"
      header="Sponsor Account Approval:"
      class="w-75"
    >
      <BListGroup>
        <BListGroupItem
          v-for="user in unapprovedUsers"
          :key="user.id"
          class="list-group-item mb-2 d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>{{ user.name }}</strong>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <BButton
              variant="success"
              size="sm"
              @click="approveSponsor(user.id)"
              >Approve</BButton
            >
            <BButton variant="danger" size="sm">Decline</BButton>
          </div>
        </BListGroupItem>
      </BListGroup>
    </BCard>
  </div>
</template>

<script>
import axios from "axios";
import { BCard, BListGroup, BListGroupItem, BButton } from "bootstrap-vue-next";
import { onMounted, ref } from "vue";

export default {
  name: "Info",
  setup() {
    const activecampaigns = ref([]);
    const campaignUsers = ref({});
    const unapprovedUsers = ref([]);
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
    const today = new Date().toLocaleDateString().split("/");

    const loadSession = async () => {
      try {
        const campaignsResponse = await axios.get(
          "http://localhost:5000/getcampaings"
        );
        const flaggedResponse = await axios.get(
          "http://localhost:5000/flagged_data"
        );
        const unapprovedResponse = await axios.get(
          "http://localhost:5000/unapproved_sponsors"
        );

        campaignUsers.value = flaggedResponse.data;
        console.log(campaignUsers);
        unapprovedUsers.value = unapprovedResponse.data;

        activecampaigns.value = campaignsResponse.data
          .map((campaign) => {
            const endDate = new Date(campaign.end_date);
            const startDate = new Date(campaign.start_date);
            const progressMade = calculateProgress(startDate, endDate, today);

            return progressMade >= 0 ? { ...campaign, progressMade } : null;
          })
          .filter((campaign) => campaign !== null);
      } catch (err) {
        console.log(err);
      }
    };

    const calculateProgress = (startDate, endDate, currentDate) => {
      const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);
      const daysPassed =
        (new Date(currentDate) - startDate) / (1000 * 60 * 60 * 24);
      return ((daysPassed / totalDays) * 100).toFixed(2);
    };

    const approveSponsor = async (id) => {
      const res = await axios.post("http://localhost:5000/approve_sponsor", {
        sponsor_id: id,
      });
      if (res.data.message.includes("success")) {
        loadSession();
      }
    };

    onMounted(() => {
      loadSession();
    });

    return {
      activecampaigns,
      campaignUsers,
      unapprovedUsers,
      approveSponsor,
    };
  },
};
</script>

<style scoped>
.list-group-item {
  border-radius: 0.25rem;
}
</style>
