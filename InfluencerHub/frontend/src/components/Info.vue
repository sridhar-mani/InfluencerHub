<template>
  <div
    class="admin-dashboard d-flex flex-column justify-content-center gap-4 align-items-center"
  >
    <h3>Welcome Admin!</h3>

    <!-- Ongoing Campaigns Card -->
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
            <BButton
              variant="success"
              size="sm"
              @click="viewCampaign(campaign.id)"
              >View</BButton
            >
            <BButton
              variant="danger"
              size="sm"
              @click="deleteCampaign(campaign.id)"
              >Delete</BButton
            >
          </div>
        </BListGroupItem>
      </BListGroup>
    </BCard>

    <!-- Flagged Users/Campaigns Card -->
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
            <BButton
              variant="success"
              :to="{ name: 'OneProfile', params: { username: item.username } }"
              size="sm"
              >View</BButton
            >
            <BButton variant="danger" size="sm" @click="deleteCampaign(item.id)"
              >Delete</BButton
            >
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
            <BButton variant="success" size="sm" @click="viewUser(user.id)"
              >View</BButton
            >
            <BButton variant="danger" size="sm" @click="deleteUser(user.id)"
              >Delete</BButton
            >
          </div>
        </BListGroupItem>
      </BListGroup>
    </BCard>

    <!-- Unapproved Users Card -->
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
            <BButton variant="danger" size="sm" @click="declineSponsor(user.id)"
              >Decline</BButton
            >
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

    const loadSession = async () => {
      try {
        const flaggedResponse = await axios.get(
          "http://localhost:5000/flagged_data"
        );
        const unapprovedResponse = await axios.get(
          "http://localhost:5000/unapproved_sponsors"
        );
        const campaignsResponse = await axios.get(
          "http://localhost:5000/getcampaings"
        );

        campaignUsers.value = flaggedResponse.data;
        unapprovedUsers.value = unapprovedResponse.data;

        activecampaigns.value = campaignsResponse.data
          .filter((campaign) => campaign.end_date > new Date())
          .map((campaign) => {
            const progressMade = calculateProgress(
              new Date(campaign.start_date),
              new Date(campaign.end_date)
            );
            return { ...campaign, progressMade };
          });
      } catch (err) {
        console.log(err);
      }
    };

    const calculateProgress = (startDate, endDate) => {
      const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);
      const daysPassed = (new Date() - startDate) / (1000 * 60 * 60 * 24);
      return ((daysPassed / totalDays) * 100).toFixed(2);
    };

    const viewCampaign = (id) => {
      // Implement campaign viewing logic
      console.log(`View campaign with ID: ${id}`);
    };

    const viewUser = (id) => {
      // Implement user viewing logic
      console.log(`View user with ID: ${id}`);
    };

    const deleteCampaign = async (id) => {
      if (confirm("Are you sure you want to delete this campaign?")) {
        try {
          await axios.delete(`http://localhost:5000/delete_campaign`, {
            data: { campaign_id: id },
          });
          loadSession(); // Refresh data
        } catch (err) {
          console.log(err);
        }
      }
    };

    const declineSponsor = async (id) => {
      if (
        confirm(
          "Are you sure you want to decline this sponsor and delete the profile?"
        )
      ) {
        try {
          await axios.delete(`http://localhost:5000/remove_user/${id}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          });
          loadSession(); // Refresh the data after deletion
        } catch (err) {
          console.error(
            "Error deleting sponsor:",
            err.response?.data || err.message
          );
        }
      }
    };

    const deleteUser = async (id) => {
      if (confirm("Are you sure you want to delete this user?")) {
        try {
          await axios.delete(`http://localhost:5000/remove_user/${id}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          });
          loadSession(); // Refresh data
        } catch (err) {
          console.log(localStorage.getItem("token"));

          console.log(err.response?.data || err.message);
        }
      }
    };

    const approveSponsor = async (id) => {
      const res = await axios.post("http://localhost:5000/approve_sponsor", {
        sponsor_id: id,
      });
      if (res.data.message.includes("success")) {
        loadSession(); // Refresh the data
      }
    };

    onMounted(() => {
      loadSession();
    });

    return {
      activecampaigns,
      campaignUsers,
      unapprovedUsers,
      viewCampaign,
      deleteCampaign,
      viewUser,
      deleteUser,
      approveSponsor,
      declineSponsor,
    };
  },
};
</script>

<style scoped>
.list-group-item {
  border-radius: 0.25rem;
}
</style>
