<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
    authStore.logout()
    router.push('/login')
}
</script>

<template>
    <div>
        <h1>Welcome, {{ authStore.user?.username }}!</h1>
        <button @click="handleLogout">Logout</button>
        <!-- 后续添加投票列表等 -->
    </div>
</template>