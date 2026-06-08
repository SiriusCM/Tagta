<template>
  <div class="post-item" @click="$emit('viewDetail', post)">
    <div class="post-avatar" @click.stop="$emit('viewProfile', post.user_id)">
      <img :src="post.user?.avatar || defaultAvatar" alt="头像">
    </div>
    <div class="post-content">
      <div class="post-header">
        <span class="post-name" @click.stop="$emit('viewProfile', post.user_id)">
          {{ post.user?.nickname || post.user?.username }}
        </span>
        <span class="post-handle">@{{ post.user?.username }}</span>
        <span class="post-time">{{ formatTime(post.created_at) }}</span>
      </div>
      <div class="post-text">{{ post.content }}</div>

      <div v-if="post.media_type === 'image' && post.image" class="post-media">
        <img :src="post.image" alt="图片" @click.stop="$emit('previewImage', post.image)">
      </div>
      <div v-if="post.media_type === 'video' && post.video" class="post-media">
        <video :src="post.video" controls @click.stop></video>
      </div>

      <div class="post-actions" @click.stop>
        <button class="post-action" @click="$emit('like', post)">
          <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
          <span>{{ post.likes_count || 0 }}</span>
        </button>
        <button class="post-action" v-if="showComment">
          <i class="ri-chat-1-line"></i>
          <span>{{ post.comments_count || 0 }}</span>
        </button>
        <button class="post-action" @click="$emit('share', post)" v-if="showShare">
          <i class="ri-share-line"></i>
        </button>
        <button class="post-action delete" @click="$emit('delete', post)" v-if="showDelete">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  post: { type: Object, required: true },
  showDelete: { type: Boolean, default: false },
  showShare: { type: Boolean, default: false },
  showComment: { type: Boolean, default: true }
})
const emit = defineEmits(['like', 'delete', 'share', 'viewProfile', 'previewImage', 'viewDetail'])

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = (now - date) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return date.toLocaleDateString()
}
</script>