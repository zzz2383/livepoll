export interface User {
    id: number
    username: string
    email: string
}

export interface AuthResponse {
    user: User
    access: string
    refresh: string
}

export interface LoginRequest {
    username: string
    password: string
}

export interface RegisterRequest {
    username: string
    email?: string
    password: string
}

export interface TokenRefreshRequest {
    refresh: string
}

export interface TokenRefreshResponse {
    access: string
    refresh: string
}