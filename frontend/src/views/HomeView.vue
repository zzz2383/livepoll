<script setup lang="ts">
import { onMounted, } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePollStore } from '@/stores/poll'

const authStore = useAuthStore()
const pollStore = usePollStore()
const router = useRouter()

onMounted(() => {
    pollStore.fetchMyPolls()
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

        <div v-if="pollStore.loading">Loading...</div>
        <div v-else-if="pollStore.error" class="error">{{ pollStore.error }}</div>
        <div v-else-if="pollStore.myPolls.length === 0">
            <p>No polls yet. Create your first one!</p>
        </div>
        <ul v-else class="poll-list">
            <li v-for="poll in pollStore.myPolls" :key="poll.id" @click="goToPoll(poll.id)">
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