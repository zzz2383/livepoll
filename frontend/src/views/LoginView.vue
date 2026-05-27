<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
    if (!username.value || !password.value) {
        error.value = '请输入用户名和密码'
        return
    }
    loading.value = true
    error.value = ''
    try {
        await authStore.login({ username: username.value, password: password.value })
        router.push('/')
    } catch (err: any) {
        error.value = err.response?.data?.error || '登录失败'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-container card">
        <h1>登录</h1>
        <form @submit.prevent="handleSubmit">
            <div class="field">
                <label>用户名</label>
                <input v-model="username" type="text" required />
            </div>
            <div class="field">
                <label>密码</label>
                <input v-model="password" type="password" required />
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading" class="btn-primary">
                {{ loading ? '登录中...' : '登录' }}
            </button>
        </form>
        <p class="switch">
            还没有账号？<router-link to="/register">立即注册</router-link>
        </p>
    </div>
</template>

<style scoped>
.auth-container {
    margin-top: 10vh;
}
</style>