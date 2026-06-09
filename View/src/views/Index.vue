<template>
  <div class="app-container">
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
      <DiscoverTab
        v-show="currentTab === 'discover'"
        :discoverTab="discoverTab"
        :searchKeyword="searchKeyword"
        :searchResults="searchResults"
        :recommendedPosts="recommendedPosts"
        :followingPosts="followingPosts"
        :hasMorePosts="hasMorePosts"
        :currentUser="currentUser"
        @switchDiscoverTab="switchDiscoverTab"
        @loadMorePosts="loadMorePosts"
        @viewProfile="viewProfile"
        @viewPostDetail="viewPostDetail"
        @previewImage="previewImage"
        @toggleLike="toggleLike"
        @sharePost="sharePost"
        @deletePost="deletePost"
      />

      <ProfileTab
        v-show="currentTab === 'profile'"
        :currentUser="currentUser"
        :myPosts="myPosts"
        @editProfile="switchToEditProfile"
        @logout="logout"
        @showFollowingList="showFollowingList"
        @showFollowersList="showFollowersList"
        @toggleLike="toggleLike"
        @deletePost="deletePost"
      />

      <EditProfile
        v-show="currentTab === 'editProfile'"
        :currentUser="currentUser"
        @saved="handleProfileSaved"
        @cancel="switchTab('profile')"
      />

      <UserProfile
        v-show="currentTab === 'userProfile'"
        :userId="viewingUserId"
        :isMyProfile="isMyProfile"
        @error="showToastMessage"
      />

      <FollowList
        v-show="currentTab === 'followingList'"
        :userId="currentUser?.id"
        type="following"
        @viewProfile="viewProfile"
        @error="showToastMessage"
      />

      <FollowList
        v-show="currentTab === 'followersList'"
        :userId="currentUser?.id"
        type="followers"
        @viewProfile="viewProfile"
        @error="showToastMessage"
      />
    </div>

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

    <button class="fab" @click="showPostModal = true">
      <i class="ri-edit-line"></i>
    </button>

    <PostModal
      :show="showPostModal"
      @submit="handlePostSubmit"
      @close="showPostModal = false"
    />

    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>

    <div class="image-preview-modal" v-if="previewImageUrl" @click="previewImageUrl = null">
      <img :src="previewImageUrl" alt="预览">
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DiscoverTab from '../components/DiscoverTab.vue'
import ProfileTab from '../components/ProfileTab.vue'
import EditProfile from '../components/EditProfile.vue'
import UserProfile from '../components/UserProfile.vue'
import FollowList from '../components/FollowList.vue'
import PostModal from '../components/PostModal.vue'

const router = useRouter()

const DEFAULT_PAGE_SIZE = 20

const getAuthHeader = () => {
  const token = localStorage.getItem('identityToken')
  return token ? { 'Authorization': token } : {}
}

// 状态
const currentUser = ref(null)
const currentTab = ref('discover')
const discoverTab = ref('recommended')
const showBackBtn = ref(false)

const searchKeyword = ref('')
const searchResults = ref([])

// 帖子
const recommendedPosts = ref([])
const followingPosts = ref([])
const myPosts = ref([])
const currentPage = ref(1)
const hasMorePosts = ref(true)

// 查看他人资料
const viewingUserId = ref(null)
const isMyProfile = ref(false)

// 发帖
const showPostModal = ref(false)

// Toast
const showToast = ref(false)
const toastMessage = ref('')

// 图片预览
const previewImageUrl = ref(null)

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
  const skip = (currentPage.value - 1) * DEFAULT_PAGE_SIZE
  if (discoverTab.value === 'recommended') {
    try {
      const response = await axios.post('/api/discover', { skip }, { headers: getAuthHeader() })
      const newPosts = response.data.posts || []
      if (newPosts.length === 0) {
        hasMorePosts.value = false
      } else {
        recommendedPosts.value = [...recommendedPosts.value, ...newPosts]
      }
    } catch (error) {
      console.error('加载更多失败:', error)
    }
  } else {
    try {
      const response = await axios.post('/api/feed', { skip }, { headers: getAuthHeader() })
      const newPosts = response.data.posts || []
      if (newPosts.length === 0) {
        hasMorePosts.value = false
      } else {
        followingPosts.value = [...followingPosts.value, ...newPosts]
      }
    } catch (error) {
      console.error('加载更多失败:', error)
    }
  }
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

    const response = await axios.post(`/api/users/${userData.id}`, {}, { headers: getAuthHeader() })
    currentUser.value = response.data.user

    const postsResponse = await axios.post(`/api/users/${userData.id}/posts`, {}, { headers: getAuthHeader() })
    myPosts.value = postsResponse.data.posts || []
  } catch (error) {
    console.error('加载失败:', error)
  }
}

// 查看用户资料
const viewProfile = async (userId) => {
  const userData = JSON.parse(localStorage.getItem('user') || '{}')
  isMyProfile.value = userData.id === userId
  viewingUserId.value = userId
  currentTab.value = 'userProfile'
  showBackBtn.value = true
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
    recommendedPosts.value = recommendedPosts.value.filter(p => p.id !== post.id)
    followingPosts.value = followingPosts.value.filter(p => p.id !== post.id)
    myPosts.value = myPosts.value.filter(p => p.id !== post.id)
  } catch (error) {
    showToastMessage(error.response?.data?.detail || '删除失败')
  }
}

// 查看帖子详情
const viewPostDetail = (post) => {
  showToastMessage('详情页开发中')
}

// 分享帖子
const sharePost = (post) => {
  const text = `${post.content || ''} - ${post.user?.nickname || post.user?.username || 'Tagta'}`
  if (navigator.share) {
    navigator.share({
      title: 'Tagta',
      text: text
    }).catch(() => {
      // 用户取消分享，忽略
    })
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToastMessage('已复制到剪贴板')
    }).catch(() => {
      showToastMessage('分享失败')
    })
  } else {
    showToastMessage('当前浏览器不支持分享')
  }
}

// 预览图片
const previewImage = (url) => {
  previewImageUrl.value = url
}

// 编辑资料
const switchToEditProfile = () => {
  currentTab.value = 'editProfile'
  showBackBtn.value = true
}

// 关注/粉丝列表
const showFollowingList = async () => {
  if (!currentUser.value) return
  currentTab.value = 'followingList'
  showBackBtn.value = true
}

const showFollowersList = async () => {
  if (!currentUser.value) return
  currentTab.value = 'followersList'
  showBackBtn.value = true
}

// 登出
const logout = async () => {
  try {
    const identityToken = localStorage.getItem('identityToken')
    if (identityToken) {
      await axios.post('/api/logout', {
        token: identityToken
      }, { headers: getAuthHeader() })
    }
  } catch (error) {
    console.error('登出请求失败:', error)
  }

  localStorage.removeItem('user')
  localStorage.removeItem('identityToken')
  localStorage.removeItem('appleUserId')
  router.push('/login')
}

// 发帖成功回调
const handlePostSubmit = () => {
  showPostModal.value = false
  showToastMessage('发布成功')
  if (currentTab.value === 'discover') {
    if (discoverTab.value === 'recommended') {
      loadRecommendedPosts()
    } else {
      loadFollowingPosts()
    }
  } else if (currentTab.value === 'profile') {
    loadMyProfile()
  }
}

// 保存资料成功回调
const handleProfileSaved = (user) => {
  currentUser.value = { ...currentUser.value, ...user }
  localStorage.setItem('user', JSON.stringify(currentUser.value))
  showToastMessage('保存成功')
  switchTab('profile')
}

onMounted(() => {
  const user = localStorage.getItem('user')
  const token = localStorage.getItem('identityToken')

  if (!user || !token) {
    router.push('/login')
    return
  }

  currentUser.value = JSON.parse(user)
  loadRecommendedPosts()
})
</script>