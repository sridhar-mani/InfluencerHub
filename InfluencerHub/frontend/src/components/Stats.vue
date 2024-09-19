<template>
  <BContainer>
    <BRow>
      <!-- Existing Sponsor Budget Chart -->
      <BCol>
        <Pie
          v-if="dataC.labels?.length > 0"
          :key="chartKeySponsor"
          :data="dataC"
          :options="optionsC"
        />
      </BCol>

      <!-- Existing Influencer Budget Chart -->
      <BCol v-if="dataInfluencer.labels?.length > 0">
        <Pie
          v-if="dataInfluencer.labels?.length > 0"
          :key="chartKeyInfluencer"
          :data="dataInfluencer"
          :options="optionsInfluencer"
        />
      </BCol>

      <!-- Existing Campaigns per Month Chart -->
      <BCol>
        <Bar
          v-if="dataCampaigns.labels.length > 0"
          :key="chartKeyCampaigns"
          :data="dataCampaigns"
          :options="optionsCampaigns"
        />
      </BCol>
    </BRow>

    <!-- New Sponsor Campaign Performance Pie Chart -->
    <BRow v-if="role === 'sponsor' && dataPerformance.labels.length > 0">
      <BCol>
        <Pie
          :key="chartKeyPerformance"
          :data="dataPerformance"
          :options="optionsPerformance"
        />
      </BCol>
    </BRow>

    <!-- New Influencer Ad Requests Trend Bar Chart -->
    <BRow v-if="role === 'influencer' && dataAdRequestsTrend.labels.length > 0">
      <BCol>
        <Bar
          :key="chartKeyAdRequestsTrend"
          :data="dataAdRequestsTrend"
          :options="optionsAdRequestsTrend"
        />
      </BCol>
    </BRow>

    <!-- New Admin Active vs Inactive Campaigns by Sponsor -->
    <BRow v-if="role === 'admin' && dataCampaignsBySponsor.labels.length > 0">
      <BCol>
        <Bar
          :key="chartKeyCampaignsBySponsor"
          :data="dataCampaignsBySponsor"
          :options="optionsCampaignsBySponsor"
        />
      </BCol>
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
    const chartKeySponsor = ref(0);
    const chartKeyInfluencer = ref(0);
    const chartKeyCampaigns = ref(0);
    const role = ref("");

    // New Charts for Sponsor Performance (Impressions & Clicks)
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

    // New Influencer Ad Requests Trend Chart
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

    // New Admin Campaigns by Sponsor Chart
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

    // Sponsor Budgets Pie Chart
    const dataC = ref({
      labels: [],
      datasets: [
        {
          label: "Sponsor Budget Distribution",
          backgroundColor: [],
          data: [],
        },
      ],
    });

    const optionsC = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Sponsor Budget Distribution",
        },
        legend: {
          position: "right",
        },
      },
    });

    // Influencer Budgets Pie Chart
    const dataInfluencer = ref({
      labels: [],
      datasets: [
        {
          label: "Influencer Budget Distribution",
          backgroundColor: [],
          data: [],
        },
      ],
    });

    const optionsInfluencer = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Influencer Budget Distribution",
        },
        legend: {
          position: "right",
        },
      },
    });

    // Campaigns per Month Bar Chart
    const dataCampaigns = ref({
      labels: [],
      datasets: [
        {
          label: "Number of Campaigns per Month",
          backgroundColor: "rgba(54, 162, 235, 0.5)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
          data: [],
        },
      ],
    });

    const optionsCampaigns = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Number of Campaigns per Month",
        },
        legend: {
          position: "top",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: 10,
          ticks: {
            stepSize: 10,
          },
        },
      },
    });

    const loadStats = async () => {
      try {
        const { data } = await axios.get(
          `http://localhost:5000/stats/${localStorage.getItem("username")}`
        );
        role.value = localStorage.getItem("role");
        console.log("Loaded data:", data);

        if (role.value === "sponsor") {
          // Campaign Performance Pie Chart (Impressions & Clicks)
          const impressions = data.campaignsdata.map(
            (campaign) => campaign.impressions
          );
          const clicks = data.campaignsdata.map((campaign) => campaign.clicks);

          dataPerformance.value.labels = data.campaignsdata.map((m) => m.name);
          dataPerformance.value.datasets[0].data = [
            impressions.reduce((a, b) => a + b, 0),
            clicks.reduce((a, b) => a + b, 0),
          ];
          chartKeyPerformance.value += 1;
        }

        if (role.value === "influencer") {
          // Ensure ad_requests is available before using
          const adRequests = data.ad_requests || []; // Default to empty array if undefined

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
            if (monthIndex >= 0 && monthIndex < 12)
              adRequestsPerMonth[monthIndex]++;
          });

          dataAdRequestsTrend.value.labels = Array.from(
            { length: 12 },
            (_, i) =>
              new Date(
                currentDate.getFullYear(),
                currentDate.getMonth() - 11 + i
              ).toLocaleString("default", {
                month: "long",
              })
          );
          dataAdRequestsTrend.value.datasets[0].data = adRequestsPerMonth;
          chartKeyAdRequestsTrend.value += 1;
        }

        if (role.value === "admin") {
          // Active vs Inactive Campaigns by Sponsor Chart
          const sponsors = data.all_sponsors.map((sponsor) => sponsor.name);
          const activeBySponsor = sponsors.map((sponsor) => {
            return data.all_campaigns.filter(
              (campaign) =>
                campaign.sponsor === sponsor && campaign.end_date > new Date()
            ).length;
          });
          const inactiveBySponsor = sponsors.map((sponsor) => {
            return data.all_campaigns.filter(
              (campaign) =>
                campaign.sponsor === sponsor && campaign.end_date <= new Date()
            ).length;
          });

          dataCampaignsBySponsor.value.labels = sponsors;
          dataCampaignsBySponsor.value.datasets[0].data = activeBySponsor;
          dataCampaignsBySponsor.value.datasets[1].data = inactiveBySponsor;
          chartKeyCampaignsBySponsor.value += 1;
        }

        if (role.value === "sponsor") {
          // Sponsor logic for charts
          const totalBudget = data.sponsordata.budget;

          // Sponsor Budgets Pie Chart
          dataC.value.labels = data.campaignsdata.map((m) => m.name);
          dataC.value.labels.push("Unused Budget");
          dataC.value.datasets[0].data = data.campaignsdata.map(
            (m) => m.budget
          );
          const unusedBudget =
            totalBudget -
            dataC.value.datasets[0].data.reduce(
              (tot, budget) => tot + budget,
              0
            );
          dataC.value.datasets[0].data.push(unusedBudget);
          dataC.value.datasets[0].backgroundColor = dataC.value.labels.map(
            () => {
              const letters = "0123456789ABCDEF";
              let color = "#";
              for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
              }
              return color;
            }
          );
          chartKeySponsor.value += 1;

          // Influencer Budgets Pie Chart
          if (data.influencerbudget) {
            dataInfluencer.value.labels = data.influencerbudget.map(
              (i) => i.influencer
            );
            dataInfluencer.value.datasets[0].data = data.influencerbudget.map(
              (i) => i.budget
            );
            dataInfluencer.value.datasets[0].backgroundColor =
              dataInfluencer.value.labels.map(() => {
                const letters = "0123456789ABCDEF";
                let color = "#";
                for (let i = 0; i < 6; i++) {
                  color += letters[Math.floor(Math.random() * 16)];
                }
                return color;
              });
            chartKeyInfluencer.value += 1;
          }

          // Campaigns per Month Bar Chart
          const campaignsPerMonth = Array(12).fill(0);
          const currentDate = new Date();
          const currentMonth = currentDate.getMonth();
          const currentYear = currentDate.getFullYear();

          data.campaignsdata.forEach((campaign) => {
            const startDate = new Date(campaign.start_date);
            const endDate = new Date(campaign.end_date);

            // Loop through each month the campaign is active
            for (
              let year = startDate.getFullYear();
              year <= endDate.getFullYear();
              year++
            ) {
              const startMonth =
                year === startDate.getFullYear() ? startDate.getMonth() : 0;
              const endMonth =
                year === endDate.getFullYear() ? endDate.getMonth() : 11;

              for (let month = startMonth; month <= endMonth; month++) {
                const monthIndex =
                  (year - currentYear) * 12 + month - currentMonth + 11;
                if (monthIndex >= 0 && monthIndex < 12) {
                  campaignsPerMonth[monthIndex] += 1;
                }
              }
            }
          });

          // Populate the labels with the past 12 months
          dataCampaigns.value.labels = Array.from({ length: 12 }, (_, i) =>
            new Date(
              currentDate.getFullYear(),
              currentDate.getMonth() - 11 + i
            ).toLocaleString("default", {
              month: "long",
            })
          );

          console.log("campaignsPerMonth:", campaignsPerMonth);
          dataCampaigns.value.datasets[0].data = campaignsPerMonth;

          // Dynamically adjust the y-axis scale
          const maxCampaigns = Math.max(...campaignsPerMonth);
          console.log("maxCampaigns:", maxCampaigns);
          if (maxCampaigns > 0) {
            if (maxCampaigns < 10) {
              optionsCampaigns.value.scales.y.suggestedMax = 10;
              optionsCampaigns.value.scales.y.ticks.stepSize = 1;
            } else if (maxCampaigns < 100) {
              optionsCampaigns.value.scales.y.suggestedMax = 100;
              optionsCampaigns.value.scales.y.ticks.stepSize = 10;
            } else if (maxCampaigns < 1000) {
              optionsCampaigns.value.scales.y.suggestedMax = 1000;
              optionsCampaigns.value.scales.y.ticks.stepSize = 100;
            }
          }

          chartKeyCampaigns.value += 1;
        } else if (role.value === "influencer") {
          // Logic for influencer-specific stats
          const adRequests = data.ad_requests; // Assuming this is returned by the backend
          // Populate any charts or data relevant to influencers here

          // Example: If you want to show a pie chart for ad request status
          const adRequestStatus = {
            pending: 0,
            accepted: 0,
            rejected: 0,
          };

          adRequests.forEach((request) => {
            adRequestStatus[request.status]++;
          });

          dataC.value.labels = Object.keys(adRequestStatus);
          dataC.value.datasets[0].data = Object.values(adRequestStatus);
          dataC.value.datasets[0].backgroundColor = dataC.value.labels.map(
            () => {
              const letters = "0123456789ABCDEF";
              let color = "#";
              for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
              }
              return color;
            }
          );
          chartKeyInfluencer.value += 1;
        } else if (role.value === "admin") {
          // Logic for admin-specific stats
          const allCampaigns = data.all_campaigns || [];
          const activeCampaigns = allCampaigns.filter(
            (campaign) => campaign.end_date > new Date()
          ).length;

          // Prepare any additional charts or stats for admin
          dataCampaigns.value.labels = ["Active Campaigns", "Total Campaigns"];
          dataCampaigns.value.datasets[0].data = [
            activeCampaigns,
            allCampaigns.length,
          ];
          chartKeyCampaigns.value += 1;
        }
      } catch (error) {
        console.error("Error loading stats:", error);
      }
    };

    onMounted(() => {
      loadStats()
        .then(() => {
          console.log("Charts data loaded successfully");
        })
        .catch((error) => {
          console.error("Error in loading charts data:", error);
        });
    });

    return {
      dataC,
      optionsC,
      chartKeySponsor,
      dataInfluencer,
      optionsInfluencer,
      chartKeyInfluencer,
      dataCampaigns,
      optionsCampaigns,
      chartKeyCampaigns,
    };
  },
};
</script>

<style scoped></style>
