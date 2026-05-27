// 选项
export interface Option {
    id: number
    text: string
    count: number
}

// 投票详情（包含实时选项计数）
export interface PollDetail {
    id: number
    title: string
    options: Option[]
    is_multiple: boolean
    closes_at: string | null
    created_by: string
    total_votes: number
    is_closed: boolean
    created_at: string
    has_voted: boolean
}

// 投票列表项（简略）
export interface PollListItem {
    id: number
    title: string
    total_votes: number
    created_at: string
    is_closed: boolean
}

// 创建投票请求
export interface PollCreateRequest {
    title: string
    options: string[]        // 至少2个
    is_multiple?: boolean
    closes_at?: string       // ISO 日期字符串
}

// 投票请求
export interface VoteRequest {
    option_ids: number[]
}

// WebSocket 实时推送的消息格式
export interface WSMessage {
    type: 'vote_update' | 'poll_closed'
    payload: {
        poll_id?: number
        option_id?: number
        new_count?: number
        total_votes?: number
    }
}