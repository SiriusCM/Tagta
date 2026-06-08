<template>
  <div class="tab-content">
    <div class="profile-header">
      <div class="profile-banner"></div>
      <div class="profile-info">
        <div class="profile-avatar">
          <img :src="currentUser?.avatar || defaultAvatar" alt="头像">
        </div>
        <div class="profile-name">{{ currentUser?.nickname || currentUser?.username }}</div>
        <div class="profile-handle">@{{ currentUser?.username }}</div>
        <div class="profile-bio" v-if="currentUser?.bio">{{ currentUser.bio }}</div>
        <div class="profile-stats">
          <span @click="$emit('showFollowingList')">
            <strong>{{ currentUser?.following_count || 0 }}</strong> 关注
          </span>
          <span @click="$emit('showFollowersList')">
            <strong>{{ currentUser?.follower_count || 0 }}</strong> 粉丝
          </span>
          <span>
            <strong>{{ myPosts.length }}</strong> 帖子
          </span>
        </div>
      </div>
    </div>

    <div class="my-posts">
      <h3>我的帖子</h3>
      <PostItem
        v-for="post in myPosts"
        :key="post.id"
        :post="post"
        :showDelete="true"
        @like="$emit('toggleLike', $event)"
        @delete="$emit('deletePost', $event)"
      />

      <div v-if="myPosts.length === 0" class="empty-state">
        <i class="ri-edit-line"></i>
        <p>还没有发布任何内容</p>
      </div>
    </div>

    <div class="profile-actions">
      <button class="btn btn-outline" @click="$emit('editProfile')">编辑资料</button>
      <button class="btn btn-danger" @click="$emit('logout')">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import PostItem from './PostItem.vue'

defineProps({
  currentUser: Object,
  myPosts: Array
})

defineEmits([
  'editProfile', 'logout',
  'showFollowingList', 'showFollowersList',
  'toggleLike', 'deletePost'
])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'
</script>