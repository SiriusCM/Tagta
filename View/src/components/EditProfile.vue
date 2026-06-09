<template>
  <div class="tab-content">
    <div class="edit-profile-form">
      <div class="edit-avatar-section">
        <div class="avatar-preview">
          <img :src="editForm.avatar || defaultAvatar" alt="头像">
        </div>
        <div class="avatar-actions">
          <button class="btn btn-outline" @click="triggerAvatarUpload">更换头像</button>
          <input type="file" ref="avatarInput" @change="handleAvatarChange" accept="image/*" style="display: none;">
        </div>
      </div>

      <div class="form-group">
        <label>昵称</label>
        <input type="text" v-model="editForm.nickname" placeholder="请输入昵称">
      </div>

      <div class="form-group">
        <label>个人简介</label>
        <textarea v-model="editForm.bio" placeholder="介绍一下自己" rows="3"></textarea>
      </div>

      <button class="btn" @click="saveProfile">保存</button>
      <button class="btn btn-outline" @click="$emit('cancel')">取消</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({ currentUser: Object })
const emit = defineEmits(['saved', 'cancel'])

const editForm = ref({ nickname: '', bio: '', avatar: '' })
const avatarFile = ref(null)
const avatarInput = ref(null)

watch(() => props.currentUser, (user) => {
  if (user) {
    editForm.value = {
      nickname: user.nickname || '',
      bio: user.bio || '',
      avatar: user.avatar || ''
    }
  }
}, { immediate: true })

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

const getAuthHeader = () => {
  const token = localStorage.getItem('identityToken')
  return token ? { 'Authorization': token } : {}
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => { editForm.value.avatar = e.target.result }
  reader.readAsDataURL(file)
}

const saveProfile = async () => {
  try {
    const formData = new FormData()
    if (editForm.value.nickname) formData.append('nickname', editForm.value.nickname)
    if (editForm.value.bio) formData.append('bio', editForm.value.bio)
    if (avatarFile.value) formData.append('avatar_file', avatarFile.value)

    const response = await axios.post('/api/profile', formData, {
      headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' }
    })

    avatarFile.value = null
    emit('saved', response.data.user)
  } catch (error) {
    alert(error.response?.data?.detail || '保存失败')
  }
}
</script>