<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
} from 'chart.js'
import type { Option } from '@/types/poll'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps<{
    options: Option[]
}>()

const chartData = computed(() => ({
    labels: props.options.map(o => o.text),
    datasets: [
        {
            label: 'Votes',
            backgroundColor: '#42b983',
            data: props.options.map(o => o.count)
        }
    ]
}))

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        y: {
            beginAtZero: true,
            ticks: { stepSize: 1 }
        }
    }
}
</script>

<template>
    <div style="height: 300px">
        <Bar :data="chartData" :options="chartOptions" />
    </div>
</template>