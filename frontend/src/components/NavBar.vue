<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 不需要导航条的路由名称（登录/注册）
const hideNavRoutes = ['login', 'register']
const showNav = computed(() => !hideNavRoutes.includes(route.name as string))

function goTo(path: string) {
    router.push(path)
}

function handleLogout() {
    authStore.logout()
    router.push('/login')
}
</script>

<template>
    <nav v-if="showNav" class="navbar">
        <div class="nav-inner">
            <div class="nav-brand" @click="goTo('/')">
                🗳️ 实时投票
            </div>
            <div class="nav-links">
                <button @click="goTo('/')" :class="{ active: route.path === '/' }">首页</button>
                <button @click="goTo('/polls/create')" :class="{ active: route.path === '/polls/create' }">创建投票</button>
            </div>
            <div class="nav-user">
                <span v-if="authStore.user">{{ authStore.user.username }}</span>
                <button @click="handleLogout" class="btn-logout">退出</button>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.navbar {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(148, 163, 184, 0.25);
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 0 20px;
}

.nav-inner {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    height: 56px;
    gap: 20px;
}

.nav-brand {
    font-weight: 700;
    font-size: 1.2rem;
    cursor: pointer;
    color: #4f46e5;
    user-select: none;
}

.nav-links {
    display: flex;
    gap: 8px;
    flex: 1;
}

.nav-links button {
    padding: 8px 16px;
    border: none;
    background: transparent;
    border-radius: 10px;
    font-weight: 500;
    color: #334155;
    transition: all 0.2s;
}

.nav-links button:hover {
    background: #f1f5f9;
}

.nav-links button.active {
    background: #4f46e5;
    color: white;
}

.nav-user {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.9rem;
    color: #475569;
}

.btn-logout {
    background: none;
    border: 1px solid #cbd5e1;
    padding: 6px 12px;
    border-radius: 8px;
    color: #ef4444;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-logout:hover {
    background: #fee2e2;
    border-color: #ef4444;
}

/* 移动端适配 */
@media (max-width: 600px) {
    .nav-inner {
        gap: 10px;
    }

    .nav-links button {
        padding: 6px 12px;
        font-size: 0.9rem;
    }
}
</style>