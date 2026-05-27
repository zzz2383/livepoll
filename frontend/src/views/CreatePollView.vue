<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePollStore } from '@/stores/poll'

const router = useRouter()
const pollStore = usePollStore()

const title = ref('')
const options = ref(['', ''])
const isMultiple = ref(false)
const duration = ref('0')
const customDate = ref('')
const error = ref('')
const loading = ref(false)

const durationOptions = [
    { label: '不限', value: '0' },
    { label: '1 小时', value: '1' },
    { label: '6 小时', value: '6' },
    { label: '12 小时', value: '12' },
    { label: '1 天', value: '24' },
    { label: '3 天', value: '72' },
    { label: '1 周', value: '168' },
    { label: '自定义', value: 'custom' }
]

function addOption() {
    options.value.push('')
}

function removeOption(index: number) {
    if (options.value.length > 2) {
        options.value.splice(index, 1)
    }
}

function calculateClosesAt(): string | undefined {
    if (duration.value === '0') return undefined
    if (duration.value === 'custom') {
        return customDate.value ? new Date(customDate.value).toISOString() : undefined
    }
    const hours = Number(duration.value)
    const closes = new Date(Date.now() + hours * 60 * 60 * 1000)
    return closes.toISOString()
}

async function handleCreate() {
    const validOptions = options.value.filter(o => o.trim() !== '')
    if (!title.value || validOptions.length < 2) {
        error.value = '标题和至少两个选项不能为空'
        return
    }
    loading.value = true
    error.value = ''
    try {
        const poll = await pollStore.createPoll({
            title: title.value,
            options: validOptions,
            is_multiple: isMultiple.value,
            closes_at: calculateClosesAt()
        })
        router.push(`/polls/${poll.id}`)
    } catch (err: any) {
        error.value = err.response?.data?.error || '创建失败'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="create-poll card">
        <h1>创建投票</h1>
        <form @submit.prevent="handleCreate">
            <div class="field">
                <label>投票标题</label>
                <input v-model="title" type="text" required />
            </div>
            <div class="field">
                <label>选项（至少两个）</label>
                <div v-for="(_opt, i) in options" :key="i" class="option-row">
                    <input v-model="options[i]" :placeholder="`选项 ${i + 1}`" />
                    <button type="button" @click="removeOption(i)" :disabled="options.length <= 2"
                        class="btn-icon">✕</button>
                </div>
                <button type="button" @click="addOption" class="btn-link">+ 添加选项</button>
            </div>
            <div class="field">
                <label>截止时间</label>
                <select v-model="duration">
                    <option v-for="opt in durationOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
            </div>
            <div class="field" v-if="duration === 'custom'">
                <label>选择具体日期时间</label>
                <input type="datetime-local" v-model="customDate" />
            </div>
            <div class="field-check">
                <input type="checkbox" v-model="isMultiple" id="multiple" />
                <label for="multiple">允许多选</label>
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading" class="btn-primary">
                {{ loading ? '创建中...' : '创建投票' }}
            </button>
        </form>
    </div>
</template>

<style scoped>
.create-poll {
    max-width: 600px;
    margin: 20px auto;
}

.option-row {
    display: flex;
    gap: 5px;
    margin: 5px 0;
}

.option-row input {
    flex: 1;
}

.btn-link {
    background: none;
    border: none;
    color: #4f46e5;
    font-weight: 500;
    cursor: pointer;
}

.btn-icon {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #ef4444;
    cursor: pointer;
}

.field-check {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 15px 0;
}

.error {
    color: #ef4444;
    margin-top: 0.5rem;
}
</style>