<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePollStore } from '@/stores/poll'
import PollChart from '@/components/PollChart.vue'

const route = useRoute()
const router = useRouter()
const pollStore = usePollStore()
const pollId = Number(route.params.id)
const selectedOptions = ref<number[]>([])
const voteError = ref('')
const voting = ref(false)
const copied = ref(false)

onMounted(async () => {
    try {
        await pollStore.fetchPollDetail(pollId)
    } catch {
        router.push('/')
    }
})

onUnmounted(() => {
    pollStore.closeWebSocket()
})

const isOpen = computed(() => pollStore.currentPoll && !pollStore.currentPoll.is_closed)
const hasVoted = computed(() => pollStore.currentPoll?.has_voted ?? false)

const maxVotes = computed(() => {
    if (!pollStore.currentPoll) return 1
    return Math.max(...pollStore.currentPoll.options.map(o => o.count), 1)
})

function getPercentage(count: number): number {
    return (count / maxVotes.value) * 100
}

function toggleOption(optionId: number) {
    const poll = pollStore.currentPoll
    if (!poll || !isOpen.value || hasVoted.value) return
    if (poll.is_multiple) {
        const idx = selectedOptions.value.indexOf(optionId)
        if (idx >= 0) selectedOptions.value.splice(idx, 1)
        else selectedOptions.value.push(optionId)
    } else {
        selectedOptions.value = [optionId]
    }
}

async function submitVote() {
    if (!pollStore.currentPoll || selectedOptions.value.length === 0) return
    voting.value = true
    voteError.value = ''
    try {
        await pollStore.submitVote(pollId, selectedOptions.value)
    } catch (err: any) {
        voteError.value = err.response?.data?.error || '投票失败'
    } finally {
        voting.value = false
    }
}

function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        copied.value = true
        setTimeout(() => (copied.value = false), 2000)
    })
}

const closesAt = computed(() => {
    if (!pollStore.currentPoll?.closes_at) return null
    return new Date(pollStore.currentPoll.closes_at)
})
const timeLeft = ref('')
let timer: ReturnType<typeof setInterval> | null = null

function updateTimeLeft() {
    if (!closesAt.value) {
        timeLeft.value = ''
        return
    }
    const diff = closesAt.value.getTime() - Date.now()
    if (diff <= 0) {
        timeLeft.value = '已结束'
        return
    }
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((diff % (1000 * 60)) / 1000)
    timeLeft.value = `${hours}小时 ${minutes}分 ${seconds}秒`
}

onMounted(() => {
    updateTimeLeft()
    timer = setInterval(updateTimeLeft, 1000)
})
onUnmounted(() => {
    if (timer) clearInterval(timer)
    pollStore.closeWebSocket()
})
</script>

<template>
    <div v-if="pollStore.loading" class="loading card">加载投票中...</div>
    <div v-else-if="pollStore.error" class="error card">{{ pollStore.error }}</div>

    <div v-else-if="pollStore.currentPoll" class="poll-detail card">
        <h1>{{ pollStore.currentPoll.title }}</h1>
        <p class="creator">创建者：{{ pollStore.currentPoll.created_by }}</p>

        <div v-if="closesAt && !pollStore.currentPoll.is_closed" class="status">
            <span class="time-left">⏳ 剩余时间：{{ timeLeft }}</span>
        </div>
        <div v-else-if="pollStore.currentPoll.is_closed" class="closed-badge">已结束</div>

        <PollChart :options="pollStore.currentPoll.options" />

        <div class="options">
            <div v-for="opt in pollStore.currentPoll.options" :key="opt.id"
                :class="['option', { selected: selectedOptions.includes(opt.id) }]"
                @click="isOpen && !hasVoted && toggleOption(opt.id)">
                <span class="option-text">{{ opt.text }}</span>
                <div class="bar-bg">
                    <div class="bar-fill" :style="{ width: getPercentage(opt.count) + '%' }"></div>
                </div>
                <span class="count">{{ opt.count }} 票</span>
            </div>
        </div>

        <div v-if="isOpen && !hasVoted" class="vote-action">
            <button @click="submitVote" :disabled="selectedOptions.length === 0 || voting" class="btn-primary">
                {{ voting ? '投票中...' : '提交投票' }}
            </button>
            <p v-if="voteError" class="error">{{ voteError }}</p>
        </div>
        <div v-else-if="hasVoted" class="voted-msg">✓ 您已投票，结果实时更新</div>

        <div class="share">
            <button @click="copyLink" class="btn-outline">{{ copied ? '已复制！' : '复制链接' }}</button>
        </div>
    </div>
</template>

<style scoped>
.poll-detail {
    max-width: 700px;
    margin: 20px auto;
}

.creator {
    color: #64748b;
    margin-bottom: 15px;
}

.status {
    margin: 10px 0;
}

.time-left {
    background: #eef2ff;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 500;
}

.closed-badge {
    background: #ef4444;
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    display: inline-block;
    margin: 10px 0;
}

.options {
    margin: 20px 0;
}

.option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    cursor: pointer;
}

.option.selected .option-text {
    color: #4f46e5;
    font-weight: 600;
}

.option-text {
    flex: 1;
}

.bar-bg {
    flex: 1;
    height: 8px;
    background: #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    background: #4f46e5;
    border-radius: 10px;
    transition: width 0.3s;
}

.count {
    font-weight: bold;
    min-width: 50px;
    text-align: right;
}

.vote-action {
    margin-top: 20px;
}

.voted-msg {
    background: #10b981;
    color: white;
    padding: 10px 20px;
    border-radius: 12px;
    display: inline-block;
    margin: 15px 0;
}

.share {
    margin-top: 25px;
}

.error {
    color: #ef4444;
    margin-top: 0.5rem;
}

.loading {
    text-align: center;
    padding: 3rem;
    color: #64748b;
}
</style>