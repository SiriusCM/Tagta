<template>
  <div class="tab-content">
    <div class="tab-switcher">
      <button :class="{ active: discoverTab === 'recommended' }" @click="$emit('switchDiscoverTab', 'recommended')">
        推荐
      </button>
      <button :class="{ active: discoverTab === 'following' }" @click="$emit('switchDiscoverTab', 'following')">
        关注
      </button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchKeyword && searchResults.length > 0" class="search-results">
      <div v-for="user in searchResults" :key="user.id" class="user-item" @click="$emit('viewProfile', user.id)">
        <div class="user-avatar">
          <img :src="user.avatar || defaultAvatar" alt="头像">
        </div>
        <div class="user-info">
          <div class="user-name">{{ user.nickname || user.username }}</div>
          <div class="user-handle">@{{ user.username }}</div>
        </div>
      </div>
    </div>

    <!-- 推荐动态 -->
    <div v-else-if="discoverTab === 'recommended'" class="posts-list">
      <PostItem
        v-for="post in recommendedPosts"
        :key="post.id"
        :post="post"
        :showDelete="post.user_id === currentUser?.id"
        :showShare="post.user_id === currentUser?.id"
        @like="$emit('toggleLike', $event)"
        @delete="$emit('deletePost', $event)"
        @share="$emit('sharePost', $event)"
        @viewProfile="$emit('viewProfile', $event)"
        @previewImage="$emit('previewImage', $event)"
        @viewDetail="$emit('viewPostDetail', $event)"
      />

      <div v-if="recommendedPosts.length === 0" class="empty-state">
        <i class="ri-bubble-chart-line"></i>
        <p>暂无推荐内容</p>
      </div>

      <div class="load-more" @click="$emit('loadMorePosts')" v-if="hasMorePosts">
        加载更多
      </div>
    </div>

    <!-- 关注动态 -->
    <div v-else-if="discoverTab === 'following'" class="posts-list">
      <PostItem
        v-for="post in followingPosts"
        :key="post.id"
        :post="post"
        @like="$emit('toggleLike', $event)"
        @viewProfile="$emit('viewProfile', $event)"
      />

      <div v-if="followingPosts.length === 0" class="empty-state">
        <i class="ri-user-follow-line"></i>
        <p>关注一些人来查看他们的动态</p>
        <button class="btn" @click="$emit('switchDiscoverTab', 'recommended')">发现内容</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import PostItem from './PostItem.vue'

defineProps({
  discoverTab: String,
  searchKeyword: String,
  searchResults: Array,
  recommendedPosts: Array,
  followingPosts: Array,
  hasMorePosts: Boolean,
  currentUser: Object
})

defineEmits([
  'switchDiscoverTab', 'loadMorePosts',
  'viewProfile', 'viewPostDetail', 'previewImage',
  'toggleLike', 'sharePost', 'deletePost'
])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'
</script>