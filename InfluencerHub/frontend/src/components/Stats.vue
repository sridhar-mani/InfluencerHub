<template>
  <BContainer>
    <BRow>
      <BCol>
        <Pie
          v-if="dataC.labels.length > 0"
          :key="chartKeySponsor"
          :data="dataC"
          :options="optionsC"
        />
      </BCol>
      <BCol v-if="dataInfluencer.labels.length > 0">
        <Pie
          v-if="dataInfluencer.labels.length > 0"
          :key="chartKeyInfluencer"
          :data="dataInfluencer"
          :options="optionsInfluencer"
        />
      </BCol>
      <BCol>
        <Bar
          v-if="dataCampaigns.labels.length > 0"
          :key="chartKeyCampaigns"
          :data="dataCampaigns"
          :options="optionsCampaigns"
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
        console.log("Loaded data:", data);

        if (localStorage.getItem("role")) {
          // Sponsor Budgets Pie Chart
          const totalBudget = data.sponsordata.budget;
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
        }
      } catch (error) {
        console.error("Error loading stats:", error);
      }
    };

    onMounted(() => {
      loadStats();
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
