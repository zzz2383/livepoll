import { defineStore } from 'pinia'
import { ref, } from 'vue'
import { pollApi } from '@/api/poll'
import { PollWebSocket } from '@/api/wsClient'
import { useAuthStore } from '@/stores/auth'
import type { PollDetail, PollListItem, PollCreateRequest, } from '@/types/poll'

export const usePollStore = defineStore('poll', () => {
    const authStore = useAuthStore()

    // --- 状态 ---
    const myPolls = ref<PollListItem[]>([])
    const currentPoll = ref<PollDetail | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)
    const participatedPolls = ref<PollListItem[]>([])

    // WebSocket 实例管理（一个投票一个连接）
    const activeWebSocket = ref<PollWebSocket | null>(null)

    // --- 动作 ---

    async function fetchParticipatedPolls() {
        loading.value = true
        error.value = null
        try {
            participatedPolls.value = await pollApi.getParticipatedPolls()
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Failed to load participated polls'
            throw err
        } finally {
            loading.value = false
        }
    }

    // 获取我的投票列表
    async function fetchMyPolls() {
        loading.value = true
        error.value = null
        try {
            myPolls.value = await pollApi.getMyPolls()
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Failed to load polls'
            throw err
        } finally {
            loading.value = false
        }
    }

    // 获取投票详情（同时建立 WebSocket 连接）
    async function fetchPollDetail(pollId: number) {
        // 先断开之前的连接
        if (activeWebSocket.value) {
            activeWebSocket.value.disconnect()
            activeWebSocket.value = null
        }

        loading.value = true
        error.value = null
        try {
            const poll = await pollApi.getPollDetail(pollId)
            currentPoll.value = poll
            // 建立 WebSocket 连接（需 JWT）
            if (authStore.accessToken) {
                const ws = new PollWebSocket(pollId)
                ws.onMessage(handleWSMessage)
                ws.connect(authStore.accessToken)
                activeWebSocket.value = ws
            }
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Failed to load poll'
            throw err
        } finally {
            loading.value = false
        }
    }

    // 处理 WebSocket 实时消息：更新 currentPoll 的选项计数
    function handleWSMessage(msg: { type: string; payload: any }) {
        if (!currentPoll.value) return
        if (msg.type === 'vote_update') {
            const { option_id, new_count } = msg.payload
            const option = currentPoll.value.options.find(opt => opt.id === option_id)
            if (option) {
                option.count = new_count
                // 重新计算总票数
                currentPoll.value.total_votes = currentPoll.value.options.reduce((sum, o) => sum + o.count, 0)
            }
        } else if (msg.type === 'poll_closed') {
            currentPoll.value.is_closed = true
        }
    }

    // 创建投票
    async function createPoll(data: PollCreateRequest) {
        loading.value = true
        error.value = null
        try {
            const newPoll = await pollApi.createPoll(data)
            // 更新列表（简单处理：重新获取，或者手动插入）
            await fetchMyPolls()
            return newPoll
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Failed to create poll'
            throw err
        } finally {
            loading.value = false
        }
    }

    // 提交投票
    async function submitVote(pollId: number, optionIds: number[]) {
        error.value = null
        try {
            const updated = await pollApi.vote(pollId, { option_ids: optionIds })
            // 后端会通过 WebSocket 推送更新，但我们也直接更新本地数据保持立即反馈
            currentPoll.value = updated
            return updated
        } catch (err: any) {
            error.value = err.response?.data?.error || 'Vote failed'
            throw err
        }
    }

    // 离开详情页时断开 WebSocket
    function closeWebSocket() {
        if (activeWebSocket.value) {
            activeWebSocket.value.disconnect()
            activeWebSocket.value = null
        }
    }

    return {
        myPolls,
        currentPoll,
        loading,
        error,
        participatedPolls,
        fetchMyPolls,
        fetchPollDetail,
        createPoll,
        submitVote,
        closeWebSocket,
        fetchParticipatedPolls
    }
})