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

async function handleLogin() {
    if (!username.value || !password.value) {
        error.value = 'Username and password are required'
        return
    }
    loading.value = true
    error.value = ''
    try {
        await authStore.login({ username: username.value, password: password.value })
        router.push('/')
    } catch (err: any) {
        error.value = err.response?.data?.error || 'Login failed'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-container">
        <h1>Login</h1>
        <form @submit.prevent="handleLogin">
            <div>
                <label>Username</label>
                <input v-model="username" type="text" required />
            </div>
            <div>
                <label>Password</label>
                <input v-model="password" type="password" required />
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
            </button>
        </form>
        <p>
            Don't have an account? <router-link to="/register">Register</router-link>
        </p>
    </div>
</template>

<style scoped>
.auth-container {
    max-width: 400px;
    margin: 50px auto;
}

.error {
    color: red;
}
</style>