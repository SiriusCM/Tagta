<template>
  <div class="app-container">
    <!-- 顶部导航 -->
    <header class="header">
      <span class="back-btn" @click="goBack" v-if="showBackBtn">
        <i class="ri-arrow-left-line"></i>
      </span>
      <div class="header-search" v-if="currentTab === 'discover'">
        <i class="ri-search-line"></i>
        <input type="text" v-model="searchKeyword" placeholder="搜索用户" @input="searchUsers">
      </div>
      <h1 v-else>{{ currentTabTitle }}</h1>
    </header>

    <div class="page-container">
      <!-- 发现页 -->
      <div v-show="currentTab === 'discover'" class="tab-content">
        <div class="tab-switcher">
          <button :class="{ active: discoverTab === 'recommended' }" @click="switchDiscoverTab('recommended')">
            推荐
          </button>
          <button :class="{ active: discoverTab === 'following' }" @click="switchDiscoverTab('following')">
            关注
          </button>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchKeyword && searchResults.length > 0" class="search-results">
          <div v-for="user in searchResults" :key="user.id" class="user-item" @click="viewProfile(user.id)">
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
          <div v-for="post in recommendedPosts" :key="post.id" class="post-item" @click="viewPostDetail(post)">
            <div class="post-avatar" @click.stop="viewProfile(post.user_id)">
              <img :src="post.user?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="post-content">
              <div class="post-header">
                <span class="post-name" @click.stop="viewProfile(post.user_id)">
                  {{ post.user?.nickname || post.user?.username }}
                </span>
                <span class="post-handle">@{{ post.user?.username }}</span>
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
              <div class="post-text">{{ post.content }}</div>

              <!-- 媒体内容 -->
              <div v-if="post.media_type === 'image' && post.image" class="post-media">
                <img :src="post.image" alt="图片" @click.stop="previewImage(post.image)">
              </div>
              <div v-if="post.media_type === 'video' && post.video" class="post-media">
                <video :src="post.video" controls @click.stop></video>
              </div>

              <div class="post-actions" @click.stop>
                <button class="post-action" @click="toggleLike(post)">
                  <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                  <span>{{ post.likes_count || 0 }}</span>
                </button>
                <button class="post-action">
                  <i class="ri-chat-1-line"></i>
                  <span>{{ post.comments_count || 0 }}</span>
                </button>
                <button class="post-action" @click="sharePost(post)" v-if="post.user_id === currentUser?.id">
                  <i class="ri-share-line"></i>
                </button>
                <button class="post-action delete" @click="deletePost(post)" v-if="post.user_id === currentUser?.id">
                  <i class="ri-delete-bin-line"></i>
                </button>
              </div>
            </div>
          </div>

          <div v-if="recommendedPosts.length === 0" class="empty-state">
            <i class="ri-bubble-chart-line"></i>
            <p>暂无推荐内容</p>
          </div>

          <div class="load-more" @click="loadMorePosts" v-if="hasMorePosts">
            加载更多
          </div>
        </div>

        <!-- 关注动态 -->
        <div v-else-if="discoverTab === 'following'" class="posts-list">
          <div v-for="post in followingPosts" :key="post.id" class="post-item" @click="viewPostDetail(post)">
            <div class="post-avatar" @click.stop="viewProfile(post.user_id)">
              <img :src="post.user?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="post-content">
              <div class="post-header">
                <span class="post-name" @click.stop="viewProfile(post.user_id)">
                  {{ post.user?.nickname || post.user?.username }}
                </span>
                <span class="post-handle">@{{ post.user?.username }}</span>
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
              <div class="post-text">{{ post.content }}</div>

              <div v-if="post.media_type === 'image' && post.image" class="post-media">
                <img :src="post.image" alt="图片">
              </div>
              <div v-if="post.media_type === 'video' && post.video" class="post-media">
                <video :src="post.video" controls></video>
              </div>

              <div class="post-actions" @click.stop>
                <button class="post-action" @click="toggleLike(post)">
                  <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                  <span>{{ post.likes_count || 0 }}</span>
                </button>
                <button class="post-action">
                  <i class="ri-chat-1-line"></i>
                  <span>{{ post.comments_count || 0 }}</span>
                </button>
              </div>
            </div>
          </div>

          <div v-if="followingPosts.length === 0" class="empty-state">
            <i class="ri-user-follow-line"></i>
            <p>关注一些人来查看他们的动态</p>
            <button class="btn" @click="switchDiscoverTab('recommended')">发现内容</button>
          </div>
        </div>
      </div>

      <!-- 我的页面 -->
      <div v-show="currentTab === 'profile'" class="tab-content">
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
              <span @click="showFollowingList">
                <strong>{{ currentUser?.following_count || 0 }}</strong> 关注
              </span>
              <span @click="showFollowersList">
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
          <div v-for="post in myPosts" :key="post.id" class="post-item">
            <div class="post-avatar">
              <img :src="currentUser?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="post-content">
              <div class="post-header">
                <span class="post-name">{{ currentUser?.nickname || currentUser?.username }}</span>
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
              <div class="post-text">{{ post.content }}</div>

              <div v-if="post.media_type === 'image' && post.image" class="post-media">
                <img :src="post.image" alt="图片">
              </div>
              <div v-if="post.media_type === 'video' && post.video" class="post-media">
                <video :src="post.video" controls></video>
              </div>

              <div class="post-actions">
                <button class="post-action" @click="toggleLike(post)">
                  <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                  <span>{{ post.likes_count || 0 }}</span>
                </button>
                <button class="post-action delete" @click="deletePost(post)">
                  <i class="ri-delete-bin-line"></i>
                </button>
              </div>
            </div>
          </div>

          <div v-if="myPosts.length === 0" class="empty-state">
            <i class="ri-edit-line"></i>
            <p>还没有发布任何内容</p>
          </div>
        </div>

        <div class="profile-actions">
          <button class="btn btn-outline" @click="switchToEditProfile">编辑资料</button>
          <button class="btn btn-danger" @click="logout">退出登录</button>
        </div>
      </div>

      <!-- 编辑资料 -->
      <div v-show="currentTab === 'editProfile'" class="tab-content">
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
          <button class="btn btn-outline" @click="switchTab('profile')">取消</button>
        </div>
      </div>

      <!-- 用户资料页 -->
      <div v-show="currentTab === 'userProfile'" class="tab-content">
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
              <button class="btn" @click="followUser(profileUser)" v-if="!profileUser?.is_following && !isMyProfile">
                关注
              </button>
              <button class="btn btn-outline" @click="unfollowUser(profileUser)" v-else-if="!isMyProfile">
                取消关注
              </button>
            </div>
          </div>
        </div>

        <div class="user-posts">
          <div v-for="post in userPosts" :key="post.id" class="post-item">
            <div class="post-avatar">
              <img :src="profileUser?.avatar || defaultAvatar" alt="头像">
            </div>
            <div class="post-content">
              <div class="post-header">
                <span class="post-name">{{ profileUser?.nickname || profileUser?.username }}</span>
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
              <div class="post-text">{{ post.content }}</div>

              <div v-if="post.media_type === 'image' && post.image" class="post-media">
                <img :src="post.image" alt="图片">
              </div>

              <div class="post-actions">
                <button class="post-action" @click="toggleLike(post)">
                  <i :class="[post.is_liked ? 'ri-heart-fill' : 'ri-heart-line', { liked: post.is_liked }]"></i>
                  <span>{{ post.likes_count || 0 }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 关注/粉丝列表 -->
      <div v-show="currentTab === 'followingList' || currentTab === 'followersList'" class="tab-content">
        <div class="list-container">
          <div v-for="user in listUsers" :key="user.id" class="user-item" @click="viewProfile(user.id)">
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
    </div>

    <!-- 底部导航 -->
    <nav class="tabbar">
      <button class="tabbar-item" :class="{ active: currentTab === 'discover' }" @click="switchTab('discover')">
        <i class="ri-compass-3-line"></i>
        <span>发现</span>
      </button>
      <button class="tabbar-item" :class="{ active: currentTab === 'profile' }" @click="switchTab('profile')">
        <i class="ri-user-3-line"></i>
        <span>我的</span>
      </button>
    </nav>

    <!-- 发帖按钮 -->
    <button class="fab" @click="showPostModal = true">
      <i class="ri-edit-line"></i>
    </button>

    <!-- 发帖弹窗 -->
    <div class="modal" :class="{ active: showPostModal }" @click="closePostModal">
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
            <button
              :class="{ active: postMediaType === 'text' }"
              @click="postMediaType = 'text'"
            >
              <i class="ri-text"></i>
              文字
            </button>
            <button
              :class="{ active: postMediaType === 'image' }"
              @click="postMediaType = 'image'"
            >
              <i class="ri-image-add-line"></i>
              图片
            </button>
            <button
              :class="{ active: postMediaType === 'video' }"
              @click="postMediaType = 'video'"
            >
              <i class="ri-video-upload-line"></i>
              视频
            </button>
          </div>

          <div v-if="postMediaType === 'image'" class="media-upload-area" @click="triggerMediaUpload('image')">
            <div v-if="postImage" class="media-preview">
              <img :src="postImage" alt="预览">
              <button class="remove-media" @click.stop="postImage = null">
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
              <button class="remove-media" @click.stop="postVideo = null">
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

    <!-- Toast -->
    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>

    <!-- 图片预览 -->
    <div class="image-preview-modal" v-if="previewImageUrl" @click="previewImageUrl = null">
      <img :src="previewImageUrl" alt="预览">
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const defaultAvatar = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%23667eea"/></svg>'

// 获取认证头
const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// 状态
const currentUser = ref(null)
const currentTab = ref('discover')
const discoverTab = ref('recommended')
const showBackBtn = ref(false)

const searchKeyword = ref('')
const searchResults = ref([])
const suggestedUsers = ref([])

// 发帖
const showPostModal = ref(false)
const postContent = ref('')
const charCount = ref(0)
const postMediaType = ref('text')
const postImage = ref('')
const postVideo = ref('')

// 帖子
const recommendedPosts = ref([])
const followingPosts = ref([])
const myPosts = ref([])
const userPosts = ref([])
const currentPage = ref(1)
const hasMorePosts = ref(true)

// 用户资料
const profileUser = ref(null)
const isMyProfile = ref(false)

// 列表
const listUsers = ref([])
const listType = ref('following')

// 编辑资料
const editForm = ref({
  nickname: '',
  bio: '',
  avatar: ''
})

// Toast
const showToast = ref(false)
const toastMessage = ref('')

// 图片预览
const previewImageUrl = ref(null)

// Avatar input ref
const avatarInput = ref(null)
const imageInput = ref(null)
const videoInput = ref(null)

// 计算属性
const currentTabTitle = computed(() => {
  const titles = {
    discover: '发现',
    profile: '我的',
    editProfile: '编辑资料',
    userProfile: '资料',
    followingList: '关注列表',
    followersList: '粉丝列表'
  }
  return titles[currentTab.value] || ''
})

// Toast
const showToastMessage = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

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

// Tab切换
const switchTab = (tab) => {
  currentTab.value = tab
  showBackBtn.value = !['discover', 'profile'].includes(tab)

  if (tab === 'discover') {
    loadRecommendedPosts()
  } else if (tab === 'profile') {
    loadMyProfile()
  }
}

const switchDiscoverTab = (tab) => {
  discoverTab.value = tab
  if (tab === 'recommended') {
    loadRecommendedPosts()
  } else {
    loadFollowingPosts()
  }
}

// 返回
const goBack = () => {
  if (currentTab.value === 'userProfile') {
    switchTab('discover')
  } else if (['followingList', 'followersList', 'editProfile'].includes(currentTab.value)) {
    switchTab('profile')
  } else {
    switchTab('discover')
  }
}

// 加载推荐帖子
const loadRecommendedPosts = async () => {
  try {
    const response = await axios.post('/api/discover', {}, { headers: getAuthHeader() })
    recommendedPosts.value = response.data.posts || []

    // 更新推荐用户
    if (response.data.suggested_users) {
      suggestedUsers.value = response.data.suggested_users
    }
  } catch (error) {
    console.error('加载推荐失败:', error)
  }
}

// 加载关注帖子
const loadFollowingPosts = async () => {
  try {
    const response = await axios.post('/api/feed', {}, { headers: getAuthHeader() })
    followingPosts.value = response.data.posts || []
  } catch (error) {
    console.error('加载关注动态失败:', error)
  }
}

// 加载更多
const loadMorePosts = async () => {
  currentPage.value++
  await loadRecommendedPosts()
}

// 搜索用户
const searchUsers = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const response = await axios.post('/api/search', { keyword: searchKeyword.value }, { headers: getAuthHeader() })
    searchResults.value = response.data.users || []
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 加载我的资料
const loadMyProfile = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    if (!userData || !userData.id) {
      logout()
      return
    }
    currentUser.value = userData

    // 获取完整用户信息
    const response = await axios.post(`/api/users/${userData.id}`, {}, { headers: getAuthHeader() })
    currentUser.value = response.data.user

    // 获取我的帖子
    const postsResponse = await axios.post(`/api/users/${userData.id}/posts`, {}, { headers: getAuthHeader() })
    myPosts.value = postsResponse.data.posts || []
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 查看用户资料
const viewProfile = async (userId) => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    isMyProfile.value = userData.id === userId

    const response = await axios.post(`/api/users/${userId}`, {}, { headers: getAuthHeader() })
    profileUser.value = response.data.user

    const postsResponse = await axios.post(`/api/users/${userId}/posts`, {}, { headers: getAuthHeader() })
    userPosts.value = postsResponse.data.posts || []

    currentTab.value = 'userProfile'
    showBackBtn.value = true
  } catch (error) {
    showToastMessage('加载失败')
  }
}

// 关注
const followUser = async (user) => {
  try {
    await axios.post(`/api/follow/${user.id}`, {}, { headers: getAuthHeader() })
    user.is_following = true
    user.follower_count = (user.follower_count || 0) + 1
    showToastMessage('关注成功')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '关注失败')
  }
}

// 取消关注
const unfollowUser = async (user) => {
  try {
    await axios.post(`/api/follow/${user.id}/unfollow`, {}, { headers: getAuthHeader() })
    user.is_following = false
    user.follower_count = Math.max(0, (user.follower_count || 1) - 1)
    showToastMessage('已取消关注')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '取消关注失败')
  }
}

// 点赞
const toggleLike = async (post) => {
  try {
    await axios.post(`/api/posts/${post.id}/like`, {}, { headers: getAuthHeader() })
    post.is_liked = !post.is_liked
    post.likes_count = post.is_liked ? (post.likes_count || 0) + 1 : Math.max(0, (post.likes_count || 1) - 1)
  } catch (error) {
    showToastMessage('操作失败')
  }
}

// 删除帖子
const deletePost = async (post) => {
  if (!confirm('确定删除这条帖子？')) return
  try {
    await axios.post(`/api/posts/${post.id}/delete`, {}, { headers: getAuthHeader() })
    showToastMessage('删除成功')

    // 从列表中移除
    recommendedPosts.value = recommendedPosts.value.filter(p => p.id !== post.id)
    followingPosts.value = followingPosts.value.filter(p => p.id !== post.id)
    myPosts.value = myPosts.value.filter(p => p.id !== post.id)
    userPosts.value = userPosts.value.filter(p => p.id !== post.id)
  } catch (error) {
    showToastMessage(error.response?.data?.message || '删除失败')
  }
}

// 查看帖子详情
const viewPostDetail = (post) => {
  showToastMessage('详情页开发中')
}

// 分享帖子
const sharePost = (post) => {
  if (navigator.share) {
    navigator.share({
      title: 'Tagta',
      text: post.content,
      url: window.location.origin + '/post/' + post.id
    })
  } else {
    showToastMessage('分享功能开发中')
  }
}

// 预览图片
const previewImage = (url) => {
  previewImageUrl.value = url
}

// 发帖相关
const updateCharCount = () => {
  charCount.value = postContent.value.length
}

const closePostModal = (e) => {
  if (!e || e.target.classList.contains('modal')) {
    showPostModal.value = false
    postContent.value = ''
    postImage.value = ''
    postVideo.value = ''
    postMediaType.value = 'text'
    charCount.value = 0
  }
}

const submitPost = async () => {
  if (!postContent.value.trim()) {
    showToastMessage('请输入内容')
    return
  }

  try {
    const data = {
      content: postContent.value,
      media_type: postMediaType.value
    }

    if (postMediaType.value === 'image' && postImage.value) {
      data.image = postImage.value
    } else if (postMediaType.value === 'video' && postVideo.value) {
      data.video = postVideo.value
    }

    await axios.post('/api/posts', data, { headers: getAuthHeader() })
    showToastMessage('发布成功')
    closePostModal()

    // 刷新当前列表
    if (currentTab.value === 'discover') {
      if (discoverTab.value === 'recommended') {
        loadRecommendedPosts()
      } else {
        loadFollowingPosts()
      }
    } else if (currentTab.value === 'profile') {
      loadMyProfile()
    }
  } catch (error) {
    showToastMessage(error.response?.data?.message || '发布失败')
  }
}

const triggerMediaUpload = (type) => {
  if (type === 'image') {
    imageInput.value?.click()
  } else if (type === 'video') {
    videoInput.value?.click()
  }
}

const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      postImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleVideoUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    // 视频文件较大，需要上传到服务器
    const formData = new FormData()
    formData.append('file', file)

    // 这里应该上传到服务器，获取URL
    // 暂时使用本地预览
    const reader = new FileReader()
    reader.onload = (e) => {
      postVideo.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 编辑资料
const switchToEditProfile = () => {
  editForm.value = {
    nickname: currentUser.value?.nickname || '',
    bio: currentUser.value?.bio || '',
    avatar: currentUser.value?.avatar || ''
  }
  currentTab.value = 'editProfile'
  showBackBtn.value = true
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      editForm.value.avatar = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const saveProfile = async () => {
  try {
    const response = await axios.post('/api/profile', {
      nickname: editForm.value.nickname,
      bio: editForm.value.bio,
      avatar: editForm.value.avatar
    }, { headers: getAuthHeader() })

    currentUser.value = { ...currentUser.value, ...response.data.user }
    localStorage.setItem('user', JSON.stringify(currentUser.value))

    showToastMessage('保存成功')
    switchTab('profile')
  } catch (error) {
    showToastMessage(error.response?.data?.message || '保存失败')
  }
}

// 关注/粉丝列表
const showFollowingList = async () => {
  if (!currentUser.value) return
  listType.value = 'following'
  try {
    const response = await axios.post(`/api/users/${currentUser.value.id}/following`, {}, { headers: getAuthHeader() })
    listUsers.value = response.data.users || []
    currentTab.value = 'followingList'
    showBackBtn.value = true
  } catch (error) {
    showToastMessage('加载失败')
  }
}

const showFollowersList = async () => {
  if (!currentUser.value) return
  listType.value = 'followers'
  try {
    const response = await axios.post(`/api/users/${currentUser.value.id}/followers`, {}, { headers: getAuthHeader() })
    listUsers.value = response.data.users || []
    currentTab.value = 'followersList'
    showBackBtn.value = true
  } catch (error) {
    showToastMessage('加载失败')
  }
}

// 登出
const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('appleUserId')
  router.push('/login')
}

onMounted(() => {
  const user = localStorage.getItem('user')
  const appleUserId = localStorage.getItem('appleUserId') ||
                      (window.tagtaApp && window.tagtaApp.appleUserId)

  if (!user || !appleUserId) {
    router.push('/login')
    return
  }

  currentUser.value = JSON.parse(user)
  loadRecommendedPosts()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 70px;
}

.header {
  position: sticky;
  top: 0;
  background: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border-bottom: 1px solid #eee;
  z-index: 100;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
}

.back-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f0f0f0;
}

.back-btn i {
  font-size: 20px;
}

.header-search {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f0f0f0;
  border-radius: 20px;
  padding: 8px 15px;
  gap: 10px;
}

.header-search i {
  color: #666;
}

.header-search input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
}

.page-container {
  max-width: 600px;
  margin: 0 auto;
}

.tab-content {
  padding: 20px;
}

.tab-switcher {
  display: flex;
  background: #f0f0f0;
  border-radius: 25px;
  padding: 4px;
  margin-bottom: 20px;
}

.tab-switcher button {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-switcher button.active {
  background: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.post-item {
  background: white;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.post-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
}

.post-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-content {
  flex: 1;
  min-width: 0;
}

.post-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.post-name {
  font-weight: 600;
  color: #333;
  cursor: pointer;
}

.post-handle {
  color: #666;
  font-size: 13px;
}

.post-time {
  color: #999;
  font-size: 12px;
}

.post-text {
  color: #333;
  line-height: 1.5;
  word-wrap: break-word;
}

.post-media {
  margin-top: 10px;
  border-radius: 10px;
  overflow: hidden;
}

.post-media img,
.post-media video {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
}

.post-actions {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}

.post-action {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  padding: 5px 10px;
  border-radius: 20px;
  transition: all 0.2s;
}

.post-action:hover {
  background: #f0f0f0;
}

.post-action i {
  font-size: 18px;
}

.post-action .liked {
  color: #e0245e;
}

.post-action.delete:hover {
  background: #ffeef0;
  color: #e0245e;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-item:hover {
  background: #f9f9f9;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.user-handle {
  color: #666;
  font-size: 13px;
}

.profile-header {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 20px;
}

.profile-banner {
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-info {
  padding: 0 20px 20px;
  text-align: center;
  margin-top: -40px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 10px;
  border: 4px solid white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.profile-handle {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.profile-bio {
  color: #333;
  margin-bottom: 15px;
  line-height: 1.5;
}

.profile-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 15px;
}

.profile-stats span {
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.profile-stats strong {
  color: #333;
  margin-right: 5px;
}

.profile-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding-top: 15px;
}

.my-posts,
.user-posts {
  margin-bottom: 20px;
}

.my-posts h3,
.user-posts h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 15px;
  padding-left: 5px;
}

.edit-profile-form {
  background: white;
  border-radius: 15px;
  padding: 20px;
}

.edit-avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #667eea;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}

.modal.active {
  opacity: 1;
  pointer-events: all;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 600px;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  max-height: 90vh;
  overflow-y: auto;
  transform: translateY(100%);
  transition: transform 0.3s;
}

.modal.active .modal-content {
  transform: translateY(0);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.close-btn i {
  font-size: 20px;
}

.modal-title {
  font-weight: 600;
  font-size: 16px;
}

.post-textarea {
  width: 100%;
  min-height: 150px;
  padding: 15px;
  border: none;
  resize: none;
  font-size: 16px;
  line-height: 1.5;
  outline: none;
}

.post-char-count {
  text-align: right;
  color: #999;
  font-size: 12px;
  margin-bottom: 15px;
}

.media-upload-section {
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.media-type-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.media-type-selector button {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.media-type-selector button.active {
  border-color: #667eea;
  background: #f0f5ff;
  color: #667eea;
}

.media-upload-area {
  border: 2px dashed #ddd;
  border-radius: 15px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.media-upload-area:hover {
  border-color: #667eea;
}

.upload-placeholder {
  color: #999;
}

.upload-placeholder i {
  font-size: 40px;
  margin-bottom: 10px;
  display: block;
}

.media-preview {
  position: relative;
  max-width: 100%;
}

.media-preview img,
.media-preview video {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
}

.remove-media {
  position: absolute;
  top: 10px;
  right: 10px;
  background: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.remove-media i {
  font-size: 20px;
  color: #e0245e;
}

.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  border-top: 1px solid #eee;
  z-index: 100;
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  color: #666;
  transition: color 0.2s;
}

.tabbar-item.active {
  color: #667eea;
}

.tabbar-item i {
  font-size: 24px;
}

.tabbar-item span {
  font-size: 12px;
}

.fab {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  z-index: 99;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.fab i {
  font-size: 24px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state i {
  font-size: 50px;
  margin-bottom: 15px;
  display: block;
}

.load-more {
  text-align: center;
  padding: 15px;
  color: #667eea;
  cursor: pointer;
}

.toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: #333;
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 14px;
  opacity: 0;
  transition: all 0.3s;
  z-index: 1001;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.list-container {
  display: flex;
  flex-direction: column;
}

.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  cursor: pointer;
}

.image-preview-modal img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}
</style>