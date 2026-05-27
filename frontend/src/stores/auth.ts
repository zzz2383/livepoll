import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
    const refreshTokenValue = ref<string | null>(localStorage.getItem('refreshToken'))

    const isAuthenticated = computed(() => !!accessToken.value)

    // 设置 token 并持久化
    function setTokens(access: string, refresh: string) {
        accessToken.value = access
        refreshTokenValue.value = refresh
        localStorage.setItem('accessToken', access)
        localStorage.setItem('refreshToken', refresh)
    }

    function clearTokens() {
        accessToken.value = null
        refreshTokenValue.value = null
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
    }

    // 注册
    async function register(data: RegisterRequest) {
        const response = await authApi.register(data)
        user.value = response.user
        setTokens(response.access, response.refresh)
    }

    // 登录
    async function login(data: LoginRequest) {
        const response = await authApi.login(data)
        user.value = response.user
        setTokens(response.access, response.refresh)
    }

    // 刷新 token
    async function refreshToken() {
        if (!refreshTokenValue.value) {
            throw new Error('No refresh token')
        }
        const response = await authApi.refreshToken({ refresh: refreshTokenValue.value })
        setTokens(response.access, response.refresh)
        return response
    }

    // 登出
    function logout() {
        user.value = null
        clearTokens()
    }

    return {
        user,
        accessToken,
        refreshTokenValue,
        isAuthenticated,
        register,
        login,
        refreshToken,
        logout
    }
})