<template>
  <BContainer>
    <BRow>
      <!-- Admin Overview: Total Campaigns, Users, Ad Requests -->
      <BCol>
        <Bar
          v-if="role === 'admin' && dataOverview.labels?.length > 0"
          :key="chartKeyOverview"
          :data="dataOverview"
          :options="optionsOverview"
        />
      </BCol>

      <!-- Admin Active vs Inactive Campaigns by Sponsor -->
      <BCol>
        <Bar
          v-if="role === 'admin' && dataCampaignsBySponsor.labels?.length > 0"
          :key="chartKeyCampaignsBySponsor"
          :data="dataCampaignsBySponsor"
          :options="optionsCampaignsBySponsor"
        />
      </BCol>

      <!-- Sponsor Campaign Performance -->
      <BCol>
        <Pie
          v-if="role === 'sponsor' && dataPerformance.labels?.length > 0"
          :key="chartKeyPerformance"
          :data="dataPerformance"
          :options="optionsPerformance"
        />
      </BCol>

      <!-- Influencer Ad Requests Status Pie Chart -->
      <BCol>
        <Pie
          v-if="role === 'influencer' && dataAdRequests.labels?.length > 0"
          :key="chartKeyAdRequests"
          :data="dataAdRequests"
          :options="optionsAdRequests"
        />
      </BCol>

      <!-- Influencer Ad Requests Trend Bar Chart -->
      <BCol>
        <Bar
          v-if="role === 'influencer' && dataAdRequestsTrend.labels?.length > 0"
          :key="chartKeyAdRequestsTrend"
          :data="dataAdRequestsTrend"
          :options="optionsAdRequestsTrend"
        />
      </BCol>

      <!-- Fallback for when no data is available -->
      <BRow v-if="!hasData">
        <BCol>
          <h5>Sorry, No Data Available Right Now.</h5>
        </BCol>
      </BRow>
    </BRow>
  </BContainer>
</template>

<script>
import { ref, onMounted } from "vue";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { Pie, Bar } from "vue-chartjs";
import axios from "axios";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  Title,
  BarElement,
  CategoryScale,
  LinearScale
);

export default {
  name: "Stats",
  components: { Pie, Bar },
  setup() {
    const role = ref("");
    const hasData = ref(false);

    // Admin Overview: Total campaigns, users, ad requests
    const chartKeyOverview = ref(0);
    const dataOverview = ref({
      labels: ["Campaigns", "Users", "Ad Requests"],
      datasets: [
        {
          label: "Overview",
          backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56"],
          data: [0, 0, 0], // Will be updated via API
        },
      ],
    });

    const optionsOverview = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Admin Overview (Campaigns, Users, Ad Requests)",
        },
        legend: {
          position: "top",
        },
      },
    });

    // Sponsor Campaign Performance
    const chartKeyPerformance = ref(0);
    const dataPerformance = ref({
      labels: [],
      datasets: [
        {
          label: "Campaign Performance (Impressions & Clicks)",
          backgroundColor: ["#36A2EB", "#FF6384"],
          data: [],
        },
      ],
    });

    const optionsPerformance = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Campaign Performance",
        },
        legend: {
          position: "right",
        },
      },
    });

    // Influencer Ad Requests Trend
    const chartKeyAdRequestsTrend = ref(0);
    const dataAdRequestsTrend = ref({
      labels: [],
      datasets: [
        {
          label: "Ad Requests Over Time",
          backgroundColor: "rgba(255,99,132,0.2)",
          borderColor: "rgba(255,99,132,1)",
          borderWidth: 1,
          data: [],
        },
      ],
    });

    const optionsAdRequestsTrend = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Ad Requests Trend",
        },
        legend: {
          position: "top",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    });

    // Admin: Active vs Inactive Campaigns by Sponsor
    const chartKeyCampaignsBySponsor = ref(0);
    const dataCampaignsBySponsor = ref({
      labels: [],
      datasets: [
        {
          label: "Active Campaigns",
          backgroundColor: "rgba(54, 162, 235, 0.5)",
          data: [],
        },
        {
          label: "Inactive Campaigns",
          backgroundColor: "rgba(255, 99, 132, 0.5)",
          data: [],
        },
      ],
    });

    const optionsCampaignsBySponsor = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Active vs Inactive Campaigns by Sponsor",
        },
        legend: {
          position: "top",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    });

    // Influencer Ad Request Status
    const chartKeyAdRequests = ref(0);
    const dataAdRequests = ref({
      labels: ["Pending", "Accepted", "Rejected"],
      datasets: [
        {
          label: "Ad Request Status",
          backgroundColor: ["#FFCE56", "#36A2EB", "#FF6384"],
          data: [0, 0, 0],
        },
      ],
    });

    const optionsAdRequests = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Ad Request Status (Pending, Accepted, Rejected)",
        },
        legend: {
          position: "right",
        },
      },
    });

    // Load the stats from the backend
    const loadStats = async () => {
      try {
        const { data } = await axios.get(
          `http://localhost:5000/stats/${localStorage.getItem("username")}`
        );
        role.value = localStorage.getItem("role");
        hasData.value = Boolean(data);

        // Admin role
        if (role.value === "admin") {
          // Overview (Campaigns, Users, Ad Requests)
          dataOverview.value.datasets[0].data = [
            data.total_campaigns,
            data.total_users,
            data.total_ad_requests,
          ];
          chartKeyOverview.value += 1;

          // Active vs Inactive Campaigns by Sponsor
          const sponsors = data.sponsors.map((sponsor) => sponsor.name);
          const activeCampaigns = sponsors.map(
            (sponsor) => data.active_campaigns[sponsor] || 0
          );
          const inactiveCampaigns = sponsors.map(
            (sponsor) => data.inactive_campaigns[sponsor] || 0
          );

          dataCampaignsBySponsor.value.labels = sponsors;
          dataCampaignsBySponsor.value.datasets[0].data = activeCampaigns;
          dataCampaignsBySponsor.value.datasets[1].data = inactiveCampaigns;
          chartKeyCampaignsBySponsor.value += 1;
        }

        // Sponsor role
        if (role.value === "sponsor") {
          const campaigns = data.campaigns || []; 
          if (campaigns.length > 0) {
            dataPerformance.value.labels = campaigns.map((c) => c.name);
            dataPerformance.value.datasets[0].data = [
              data.total_impressions || 0,
              data.total_clicks || 0,
            ];
            chartKeyPerformance.value += 1;
          } else {
            console.log("No campaigns data available for sponsor.");
            hasData.value = false; // Indicate no data is available
          }
        }

        // Influencer role
        if (role.value === "influencer") {
          const adRequests = data.ad_requests || [];

          // Ad Requests Status Pie Chart
          const adRequestStatus = {
            pending: 0,
            accepted: 0,
            rejected: 0,
          };
          adRequests.forEach((request) => {
            adRequestStatus[request.status]++;
          });
          dataAdRequests.value.datasets[0].data =
            Object.values(adRequestStatus);
          chartKeyAdRequests.value += 1;

          // Ad Requests Trend Bar Chart
          const adRequestsPerMonth = Array(12).fill(0);
          const currentDate = new Date();
          adRequests.forEach((request) => {
            const requestDate = new Date(request.created_at);
            const monthIndex =
              (requestDate.getFullYear() - currentDate.getFullYear()) * 12 +
              requestDate.getMonth() -
              currentDate.getMonth() +
              11;
            if (monthIndex >= 0 && monthIndex < 12) {
              adRequestsPerMonth[monthIndex]++;
            }
          });

          dataAdRequestsTrend.value.labels = Array.from(
            { length: 12 },
            (_, i) =>
              new Date(
                currentDate.getFullYear(),
                currentDate.getMonth() - 11 + i
              ).toLocaleString("default", { month: "long" })
          );
          dataAdRequestsTrend.value.datasets[0].data = adRequestsPerMonth;
          chartKeyAdRequestsTrend.value += 1;
        }
      } catch (error) {
        console.error("Error loading stats:", error);
        hasData.value = false;
      }
    };

    onMounted(() => {
      loadStats();
    });

    return {
      role,
      hasData,
      dataOverview,
      chartKeyOverview,
      optionsOverview,
      dataPerformance,
      chartKeyPerformance,
      optionsPerformance,
      dataAdRequestsTrend,
      chartKeyAdRequestsTrend,
      optionsAdRequestsTrend,
      dataCampaignsBySponsor,
      chartKeyCampaignsBySponsor,
      optionsCampaignsBySponsor,
      dataAdRequests,
      chartKeyAdRequests,
      optionsAdRequests,
    };
  },
};
</script>

<style scoped>
h5 {
  text-align: center;
  color: #ff6384;
  margin-top: 20px;
}
</style>
