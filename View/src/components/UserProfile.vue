<template>
  <div class="tab-content">
    <div class="profile-header">
      <div class="profile-banner"></div>
      <div class="profile-info">
        <div class="profile-avatar">
          <img :src="profileUser?.avatar || defaultAvatar" alt="头像">
        </div>
        <div class="profile-name">{{ profileUser?.nickname || profileUser?.username }}</div>
        <div class="profile-handle">@{{ profileUser?.username }}</div>
        <div class="profile-bio" v-if="profileUser?.bio">{{ profileUser.bio }}</div>
        <div class="profile-stats">
          <span>
            <strong>{{ profileUser?.following_count || 0 }}</strong> 关注
          </span>
          <span>
            <strong>{{ profileUser?.follower_count || 0 }}</strong> 粉丝
          </span>
          <span>
            <strong>{{ profileUser?.post_count || 0 }}</strong> 帖子
          </span>
        </div>
        <div class="profile-actions">
          <button class="btn" @click="followUser" v-if="!profileUser?.is_following && !isMyProfile">
            关注
          </button>
          <button class="btn btn-outline" @click="unfollowUser" v-else-if="!isMyProfile">
            取消关注
          </button>
        </div>
      </div>
    </div>

    <div class="user-posts">
      <PostItem
        v-for="post in userPosts"
        :key="post.id"
        :post="post"
        @like="toggleLike"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import PostItem from './PostItem.vue'

const props = defineProps({
  userId: Number,
  isMyProfile: Boolean
})
const emit = defineEmits(['error'])

const profileUser = ref(null)
const userPosts = ref([])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

const getAuthHeader = () => {
  const token = localStorage.getItem('identityToken')
  return token ? { 'Authorization': token } : {}
}

const loadUserProfile = async () => {
  if (!props.userId) return
  try {
    const response = await axios.post(`/api/users/${props.userId}`, {}, { headers: getAuthHeader() })
    profileUser.value = response.data.user

    const postsResponse = await axios.post(`/api/users/${props.userId}/posts`, {}, { headers: getAuthHeader() })
    userPosts.value = postsResponse.data.posts || []
  } catch (error) {
    emit('error', '加载失败')
  }
}

const followUser = async () => {
  try {
    await axios.post(`/api/follow/${profileUser.value.id}`, {}, { headers: getAuthHeader() })
    profileUser.value.is_following = true
    profileUser.value.follower_count = (profileUser.value.follower_count || 0) + 1
  } catch (error) {
    emit('error', error.response?.data?.detail || '关注失败')
  }
}

const unfollowUser = async () => {
  try {
    await axios.post(`/api/follow/${profileUser.value.id}/unfollow`, {}, { headers: getAuthHeader() })
    profileUser.value.is_following = false
    profileUser.value.follower_count = Math.max(0, (profileUser.value.follower_count || 1) - 1)
  } catch (error) {
    emit('error', error.response?.data?.detail || '取消关注失败')
  }
}

const toggleLike = async (post) => {
  try {
    await axios.post(`/api/posts/${post.id}/like`, {}, { headers: getAuthHeader() })
    post.is_liked = !post.is_liked
    post.likes_count = post.is_liked ? (post.likes_count || 0) + 1 : Math.max(0, (post.likes_count || 1) - 1)
  } catch (error) {
    emit('error', '操作失败')
  }
}

watch(() => props.userId, loadUserProfile, { immediate: true })
</script>