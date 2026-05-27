<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
    if (!username.value || !password.value) {
        error.value = '用户名和密码不能为空'
        return
    }
    if (password.value !== confirmPassword.value) {
        error.value = '两次输入的密码不一致'
        return
    }
    loading.value = true
    error.value = ''
    try {
        await authStore.register({
            username: username.value,
            email: email.value || undefined,
            password: password.value
        })
        router.push('/')
    } catch (err: any) {
        error.value = err.response?.data?.error || '注册失败'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-container card">
        <h1>注册</h1>
        <form @submit.prevent="handleSubmit">
            <div class="field">
                <label>用户名</label>
                <input v-model="username" type="text" required />
            </div>
            <div class="field">
                <label>邮箱 <span>（选填）</span></label>
                <input v-model="email" type="email" />
            </div>
            <div class="field">
                <label>密码</label>
                <input v-model="password" type="password" required />
            </div>
            <div class="field">
                <label>确认密码</label>
                <input v-model="confirmPassword" type="password" required />
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading" class="btn-primary">
                {{ loading ? '注册中...' : '注册' }}
            </button>
        </form>
        <p class="switch">
            已有账号？<router-link to="/login">去登录</router-link>
        </p>
    </div>
</template>

<style scoped>
.auth-container {
    margin-top: 10vh;
}
</style>