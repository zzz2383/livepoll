import apiClient from './client'
import type {
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenRefreshResponse
} from '@/types/auth'

export const authApi = {
    register(data: RegisterRequest): Promise<AuthResponse> {
        return apiClient.post('/users/register/', data)
    },
    login(data: LoginRequest): Promise<AuthResponse> {
        return apiClient.post('/users/login/', data)
    },
    refreshToken(data: TokenRefreshRequest): Promise<TokenRefreshResponse> {
        return apiClient.post('/users/token/refresh/', data)
    }
}