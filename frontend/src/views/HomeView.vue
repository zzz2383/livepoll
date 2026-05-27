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
        <header>
            <h1>LivePoll</h1>
            <div class="user-bar">
                <span>Welcome, {{ authStore.user?.username }}</span>
                <button @click="handleLogout">Logout</button>
            </div>
        </header>

        <div class="actions">
            <button @click="goToCreate" class="btn-primary">Create New Poll</button>
        </div>

        <!-- 标签切换 -->
        <div class="tabs">
            <button :class="{ active: activeTab === 'created' }" @click="activeTab = 'created'">
                My Polls
            </button>
            <button :class="{ active: activeTab === 'participated' }" @click="activeTab = 'participated'">
                Participated
            </button>
        </div>

        <div v-if="pollStore.loading">Loading...</div>
        <div v-else-if="pollStore.error" class="error">{{ pollStore.error }}</div>
        <div v-else-if="currentPolls.length === 0">
            <p v-if="activeTab === 'created'">No polls yet. Create your first one!</p>
            <p v-else>You haven't participated in any polls yet.</p>
        </div>
        <ul v-else class="poll-list">
            <li v-for="poll in currentPolls" :key="poll.id" @click="goToPoll(poll.id)">
                <h3>{{ poll.title }}</h3>
                <span>Total votes: {{ poll.total_votes }}</span>
                <span v-if="poll.is_closed" class="closed">Closed</span>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.home {
    max-width: 600px;
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
}

.tabs button.active {
    background: #42b983;
    color: white;
    border-color: #42b983;
}

.poll-list {
    list-style: none;
    padding: 0;
}

.poll-list li {
    border: 1px solid #ddd;
    padding: 10px;
    margin: 5px 0;
    cursor: pointer;
}

.poll-list li:hover {
    background-color: #f0f0f0;
}

.closed {
    color: red;
    margin-left: 10px;
}

.error {
    color: red;
}

.btn-primary {
    padding: 8px 16px;
    cursor: pointer;
}
</style>