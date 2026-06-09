<template>
  <div class="tab-content">
    <div class="list-container">
      <div v-for="user in listUsers" :key="user.id" class="user-item" @click="$emit('viewProfile', user.id)">
        <div class="user-avatar">
          <img :src="user.avatar || defaultAvatar" alt="头像">
        </div>
        <div class="user-info">
          <div class="user-name">{{ user.nickname || user.username }}</div>
          <div class="user-handle">@{{ user.username }}</div>
        </div>
      </div>

      <div v-if="listUsers.length === 0" class="empty-state">
        <p>暂无内容</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  userId: Number,
  type: String // 'following' | 'followers'
})
const emit = defineEmits(['viewProfile', 'error'])

const listUsers = ref([])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

const getAuthHeader = () => {
  const token = localStorage.getItem('identityToken')
  return token ? { 'Authorization': token } : {}
}

const loadList = async () => {
  if (!props.userId) return
  try {
    const endpoint = props.type === 'following'
      ? `/api/users/${props.userId}/following`
      : `/api/users/${props.userId}/followers`
    const response = await axios.post(endpoint, {}, { headers: getAuthHeader() })
    listUsers.value = response.data.users || []
  } catch (error) {
    emit('error', '加载失败')
  }
}

watch(() => [props.userId, props.type], loadList, { immediate: true })
</script>