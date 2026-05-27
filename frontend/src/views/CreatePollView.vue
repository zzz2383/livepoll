<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePollStore } from '@/stores/poll'

const router = useRouter()
const pollStore = usePollStore()

const title = ref('')
const options = ref(['', ''])  // 至少两个选项
const isMultiple = ref(false)
const error = ref('')
const loading = ref(false)

function addOption() {
    options.value.push('')
}

function removeOption(index: number) {
    if (options.value.length > 2) {
        options.value.splice(index, 1)
    }
}

async function handleCreate() {
    const validOptions = options.value.filter(o => o.trim() !== '')
    if (!title.value || validOptions.length < 2) {
        error.value = 'Title and at least 2 options are required'
        return
    }
    loading.value = true
    error.value = ''
    try {
        const poll = await pollStore.createPoll({
            title: title.value,
            options: validOptions,
            is_multiple: isMultiple.value
        })
        router.push(`/polls/${poll.id}`)
    } catch (err: any) {
        error.value = err.response?.data?.error || 'Failed to create poll'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="create-poll">
        <h1>Create Poll</h1>
        <form @submit.prevent="handleCreate">
            <div>
                <label>Title</label>
                <input v-model="title" required />
            </div>
            <div>
                <label>Options (minimum 2)</label>
                <div v-for="(_opt, index) in options" :key="index" class="option-row">
                    <input v-model="options[index]" :placeholder="`Option ${index + 1}`" />
                    <button type="button" @click="removeOption(index)" :disabled="options.length <= 2">X</button>
                </div>
                <button type="button" @click="addOption">+ Add Option</button>
            </div>
            <div>
                <label>
                    <input type="checkbox" v-model="isMultiple" />
                    Allow multiple choice
                </label>
            </div>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit" :disabled="loading">{{ loading ? 'Creating...' : 'Create' }}</button>
        </form>
    </div>
</template>

<style scoped>
.create-poll {
    max-width: 500px;
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

.error {
    color: red;
}
</style>