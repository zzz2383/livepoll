import apiClient from './client'
import type {
    PollDetail,
    PollListItem,
    PollCreateRequest,
    VoteRequest
} from '@/types/poll'

export const pollApi = {
    // 获取当前用户的投票列表
    getMyPolls(): Promise<PollListItem[]> {
        return apiClient.get('/polls/')
    },

    // 获取单个投票详情（包含最新计数）
    getPollDetail(pollId: number): Promise<PollDetail> {
        return apiClient.get(`/polls/${pollId}/`)
    },

    // 创建投票
    createPoll(data: PollCreateRequest): Promise<PollDetail> {
        return apiClient.post('/polls/', data)
    },

    // 提交投票
    vote(pollId: number, data: VoteRequest): Promise<PollDetail> {
        return apiClient.post(`/polls/${pollId}/vote/`, data)
    }
}