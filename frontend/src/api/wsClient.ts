import type { WSMessage } from '@/types/poll'

export class PollWebSocket {
    private socket: WebSocket | null = null
    private pollId: number
    private messageHandler: ((msg: WSMessage) => void) | null = null
    private reconnectAttempts = 0
    private maxReconnectAttempts = 5
    private reconnectDelay = 2000

    constructor(pollId: number) {
        this.pollId = pollId
    }

    connect(token: string) {
        // 通过 URL 参数传递 JWT token 进行认证（后端消费者需支持）
        const url = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/polls/${this.pollId}/?token=${token}`
        this.socket = new WebSocket(url)

        this.socket.onopen = () => {
            console.log(`WebSocket connected to poll ${this.pollId}`)
            this.reconnectAttempts = 0
        }

        this.socket.onmessage = (event) => {
            try {
                const data: WSMessage = JSON.parse(event.data)
                this.messageHandler?.(data)
            } catch (e) {
                console.error('Failed to parse WebSocket message', e)
            }
        }

        this.socket.onclose = (event) => {
            if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++
                setTimeout(() => this.connect(token), this.reconnectDelay)
            }
        }

        this.socket.onerror = (err) => {
            console.error('WebSocket error', err)
        }
    }

    onMessage(handler: (msg: WSMessage) => void) {
        this.messageHandler = handler
    }

    disconnect() {
        if (this.socket) {
            this.socket.onclose = null  // 避免触发重连
            this.socket.close()
            this.socket = null
        }
    }
}