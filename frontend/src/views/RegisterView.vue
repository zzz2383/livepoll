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

async function handleRegister() {
    if (!username.value || !password.value) {
        error.value = 'Username and password are required'
        return
    }
    if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
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
        error.value = err.response?.data?.error || 'Registration failed'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-container">
        <h1>Register</h1>
        <form @submit.prevent="handleRegister">
            <div>
                <label>Username</label>
                <input v-model="username" type="text" required />
            </div>
            <div>
                <label>Email (optional)</label>
                <input v-model="email" type="email" />
            </div>
            <div>
                <label>Password</label>
                <input v-model="password" type="password" required />
            </div>
            <div>
                <label>Confirm Password</label>
                <input v-model="confirmPassword" type="password" required />
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
            </button>
        </form>
        <p>
            Already have an account? <router-link to="/login">Login</router-link>
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