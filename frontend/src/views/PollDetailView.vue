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

const isOpen = computed(() =>
    pollStore.currentPoll && !pollStore.currentPoll.is_closed
)

const hasVoted = computed(() =>
    pollStore.currentPoll?.has_voted ?? false
)

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
        // has_voted 会通过 store 更新
    } catch (err: any) {
        voteError.value = err.response?.data?.error || 'Vote failed'
    } finally {
        voting.value = false
    }
}

function copyLink() {
    const url = window.location.href
    navigator.clipboard.writeText(url).then(() => {
        copied.value = true
        setTimeout(() => (copied.value = false), 2000)
    })
}
</script>

<template>
    <div class="poll-detail" v-if="pollStore.currentPoll">
        <h1>{{ pollStore.currentPoll.title }}</h1>
        <p>Created by {{ pollStore.currentPoll.created_by }}</p>
        <p v-if="pollStore.currentPoll.is_closed" class="closed">This poll is closed</p>

        <!-- 图表 -->
        <PollChart :options="pollStore.currentPoll.options" />

        <!-- 选项列表和进度条 -->
        <div class="options">
            <div v-for="option in pollStore.currentPoll.options" :key="option.id"
                :class="['option', { selected: selectedOptions.includes(option.id) }]"
                @click="isOpen && !hasVoted && toggleOption(option.id)">
                <span class="option-text">{{ option.text }}</span>
                <span class="bar" :style="{ width: getPercentage(option.count) + '%' }"></span>
                <span class="count">{{ option.count }}</span>
            </div>
        </div>

        <!-- 投票按钮 -->
        <div v-if="isOpen && !hasVoted" class="vote-action">
            <button @click="submitVote" :disabled="selectedOptions.length === 0 || voting">
                {{ voting ? 'Voting...' : 'Submit Vote' }}
            </button>
            <p v-if="voteError" class="error">{{ voteError }}</p>
        </div>

        <!-- 已投票提示 -->
        <div v-else-if="hasVoted" class="voted-message">
            ✓ You have voted. Results update in real-time.
        </div>

        <!-- 分享链接 -->
        <div class="share-section">
            <button @click="copyLink">{{ copied ? 'Copied!' : 'Copy Link' }}</button>
        </div>

        <div v-if="pollStore.loading">Loading...</div>
        <div v-else-if="pollStore.error" class="error">{{ pollStore.error }}</div>
    </div>
</template>
<style scoped>
.poll-detail {
    max-width: 600px;
    margin: 20px auto;
}

.options {
    margin: 20px 0;
}

.option {
    display: flex;
    align-items: center;
    margin: 10px 0;
    padding: 8px;
    border: 1px solid #ddd;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.option.selected {
    border-color: #42b983;
    background-color: #f0fff0;
}

.option-text {
    flex: 1;
    z-index: 1;
}

.bar {
    height: 100%;
    background-color: #42b98333;
    position: absolute;
    left: 0;
    top: 0;
    transition: width 0.3s;
    z-index: 0;
}

.count {
    margin-left: 10px;
    z-index: 1;
    font-weight: bold;
}

.closed {
    color: red;
}

.vote-action {
    margin-top: 20px;
}

.error {
    color: red;
}

.voted-message {
    color: green;
    margin-top: 20px;
}

.share-section {
    margin-top: 20px;
}
</style>