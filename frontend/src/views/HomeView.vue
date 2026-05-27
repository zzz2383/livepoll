<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePollStore } from '@/stores/poll'

const authStore = useAuthStore()
const pollStore = usePollStore()
const router = useRouter()

const activeTab = ref<'created' | 'participated'>('created')

const currentPolls = computed(() => {
    return activeTab.value === 'created' ? pollStore.myPolls : pollStore.participatedPolls
})

onMounted(() => {
    pollStore.fetchMyPolls()
    pollStore.fetchParticipatedPolls()
})

function goToPoll(pollId: number) {
    router.push(`/polls/${pollId}`)
}

function goToCreate() {
    router.push('/polls/create')
}

function handleLogout() {
    authStore.logout()
    router.push('/login')
}
</script>

<template>
    <div class="home">
        <header class="home-header card">
            <h1>实时投票</h1>
            <div class="user-bar">
                <span>👋 {{ authStore.user?.username }}</span>
                <button @click="handleLogout" class="btn-outline">退出登录</button>
            </div>
        </header>

        <div class="actions">
            <button @click="goToCreate" class="btn-primary">＋ 创建新投票</button>
        </div>

        <div class="tabs">
            <button :class="{ active: activeTab === 'created' }" @click="activeTab = 'created'">我创建的</button>
            <button :class="{ active: activeTab === 'participated' }" @click="activeTab = 'participated'">我参与的</button>
        </div>

        <div v-if="pollStore.loading" class="loading">加载中...</div>
        <div v-else-if="pollStore.error" class="error card">{{ pollStore.error }}</div>
        <div v-else-if="currentPolls.length === 0" class="card empty">
            <p v-if="activeTab === 'created'">还没有创建任何投票，立即创建一个吧！</p>
            <p v-else>还没有参与任何投票。</p>
        </div>
        <div v-else class="poll-list">
            <div v-for="poll in currentPolls" :key="poll.id" class="poll-item card" @click="goToPoll(poll.id)">
                <h3>{{ poll.title }}</h3>
                <div class="meta">
                    <span>{{ poll.total_votes }} 票</span>
                    <span v-if="poll.is_closed" class="closed">已结束</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.home {
    max-width: 720px;
    margin: 20px auto;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-bar {
    display: flex;
    gap: 10px;
    align-items: center;
}

.actions {
    margin: 15px 0;
}

.tabs {
    display: flex;
    gap: 10px;
    margin: 15px 0;
}

.tabs button {
    padding: 6px 16px;
    border: 1px solid #ccc;
    background: #f9f9f9;
    cursor: pointer;
    border-radius: 10px;
}

.tabs button.active {
    background: #4f46e5;
    color: white;
    border-color: #4f46e5;
}

.poll-list {
    list-style: none;
    padding: 0;
}

.poll-item {
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: 0.15s;
}

.poll-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.meta {
    display: flex;
    gap: 15px;
    margin-top: 8px;
    font-size: 0.9rem;
    color: #64748b;
}

.closed {
    color: #ef4444;
}

.loading {
    text-align: center;
    padding: 2rem;
    color: #64748b;
}

.error {
    color: #ef4444;
    margin-top: 0.5rem;
}

.empty {
    text-align: center;
    padding: 3rem;
    color: #64748b;
}
</style>