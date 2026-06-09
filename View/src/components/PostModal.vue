<template>
  <div class="modal" :class="{ active: show }" @click="closePostModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <button class="close-btn" @click="closePostModal">
          <i class="ri-close-line"></i>
        </button>
        <span class="modal-title">发布新帖</span>
        <button class="btn" @click="submitPost" :disabled="!postContent.trim()">
          发布
        </button>
      </div>

      <textarea
        class="post-textarea"
        v-model="postContent"
        placeholder="有什么新鲜事想分享给大家？"
        maxlength="500"
        @input="updateCharCount"
      ></textarea>

      <div class="post-char-count">{{ charCount }}/500</div>

      <div class="media-upload-section">
        <div class="media-type-selector">
          <button :class="{ active: postMediaType === 'text' }" @click="postMediaType = 'text'">
            <i class="ri-text"></i>
            文字
          </button>
          <button :class="{ active: postMediaType === 'image' }" @click="postMediaType = 'image'">
            <i class="ri-image-add-line"></i>
            图片
          </button>
          <button :class="{ active: postMediaType === 'video' }" @click="postMediaType = 'video'">
            <i class="ri-video-upload-line"></i>
            视频
          </button>
        </div>

        <div v-if="postMediaType === 'image'" class="media-upload-area" @click="triggerMediaUpload('image')">
          <div v-if="postImage" class="media-preview">
            <img :src="postImage" alt="预览">
            <button class="remove-media" @click.stop="postImage = null; postImageFile = null">
              <i class="ri-close-circle-fill"></i>
            </button>
          </div>
          <div v-else class="upload-placeholder">
            <i class="ri-image-add-line"></i>
            <span>点击上传图片</span>
          </div>
          <input type="file" ref="imageInput" @change="handleImageUpload" accept="image/*" style="display: none;">
        </div>

        <div v-if="postMediaType === 'video'" class="media-upload-area" @click="triggerMediaUpload('video')">
          <div v-if="postVideo" class="media-preview">
            <video :src="postVideo" controls></video>
            <button class="remove-media" @click.stop="postVideo = null; postVideoFile = null">
              <i class="ri-close-circle-fill"></i>
            </button>
          </div>
          <div v-else class="upload-placeholder">
            <i class="ri-video-upload-line"></i>
            <span>点击上传视频</span>
          </div>
          <input type="file" ref="videoInput" @change="handleVideoUpload" accept="video/*" style="display: none;">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['submit', 'close'])

const postContent = ref('')
const charCount = ref(0)
const postMediaType = ref('text')
const postImage = ref('')
const postVideo = ref('')
const postImageFile = ref(null)
const postVideoFile = ref(null)
const imageInput = ref(null)
const videoInput = ref(null)

const getAuthHeader = () => {
  const token = localStorage.getItem('identityToken')
  return token ? { 'Authorization': token } : {}
}

const updateCharCount = () => {
  charCount.value = postContent.value.length
}

const closePostModal = (e) => {
  if (!e || e.target.classList.contains('modal')) {
    resetForm()
    emit('close')
  }
}

const resetForm = () => {
  postContent.value = ''
  postImage.value = ''
  postVideo.value = ''
  postImageFile.value = null
  postVideoFile.value = null
  postMediaType.value = 'text'
  charCount.value = 0
}

const submitPost = async () => {
  if (!postContent.value.trim()) return

  try {
    const formData = new FormData()
    formData.append('content', postContent.value)
    formData.append('media_type', postMediaType.value)

    const file = postMediaType.value === 'image'
      ? postImageFile.value
      : (postMediaType.value === 'video' ? postVideoFile.value : null)

    if (file) formData.append('file', file)

    await axios.post('/api/posts', formData, {
      headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' }
    })

    emit('submit')
    resetForm()
  } catch (error) {
    alert(error.response?.data?.detail || '发布失败')
  }
}

const triggerMediaUpload = (type) => {
  if (type === 'image') imageInput.value?.click()
  else if (type === 'video') videoInput.value?.click()
}

const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    postImageFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => { postImage.value = e.target.result }
    reader.readAsDataURL(file)
  }
}

const handleVideoUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    postVideoFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => { postVideo.value = e.target.result }
    reader.readAsDataURL(file)
  }
}
</script>