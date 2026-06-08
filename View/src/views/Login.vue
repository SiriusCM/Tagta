<template>
  <div class="auth-container">
    <div class="logo">
      <i class="ri-tag-fill"></i>
      <h1>Tagta</h1>
    </div>
    <div class="auth-card">
      <h2>欢迎使用 Tagta</h2>
      <p class="subtitle">类似Twitter的社交分享平台</p>

      <div class="status-section">
        <div v-if="checking" class="loading">
          <div class="spinner"></div>
          <p>验证登录状态...</p>
        </div>

        <div v-else-if="!isAuthenticated" class="not-authenticated">
          <i class="ri-shield-cross-line"></i>
          <p>请先在iOS App中登录</p>
        </div>

        <div v-else class="authenticated">
          <i class="ri-check-line"></i>
          <p>登录验证成功！</p>
        </div>
      </div>

      <div class="features">
        <div class="feature-item">
          <i class="ri-video-upload-line"></i>
          <span>分享视频</span>
        </div>
        <div class="feature-item">
          <i class="ri-image-add-line"></i>
          <span>发布图文</span>
        </div>
        <div class="feature-item">
          <i class="ri-user-follow-line"></i>
          <span>关注好友</span>
        </div>
      </div>
    </div>

    <div class="toast" :class="{ show: showToast }">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const checking = ref(true)
const isAuthenticated = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const showToastMessage = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 验证登录状态
const verifyLogin = async () => {
  const appleUserId = localStorage.getItem('appleUserId') ||
                       (window.tagtaApp && window.tagtaApp.appleUserId)

  const user = localStorage.getItem('user')

  if (appleUserId && user) {
    // 已有登录信息，尝试验证
    try {
      const response = await axios.post(`/api/apple/verify`, {
        apple_user_id: appleUserId
      })

      if (response.data.success && response.data.verified) {
        isAuthenticated.value = true
        showToastMessage('登录成功')
        setTimeout(() => router.push('/index'), 500)
        return
      }
    } catch (error) {
      console.error('验证失败:', error)
    }

    // 验证失败，尝试重新登录
    try {
      const response = await axios.post('/api/apple/login', {
        apple_user_id: appleUserId,
        authorization_code: '',
        identity_token: ''
      })

      if (response.data.success) {
        localStorage.setItem('user', JSON.stringify(response.data.user))
        if (response.data.token) {
          localStorage.setItem('token', response.data.token)
        }
        isAuthenticated.value = true
        showToastMessage('登录成功')
        setTimeout(() => router.push('/index'), 500)
        return
      }
    } catch (error) {
      console.error('登录失败:', error)
    }
  }

  isAuthenticated.value = false
  checking.value = false
}

onMounted(() => {
  verifyLogin()
})
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.logo {
  text-align: center;
  margin-bottom: 40px;
}

.logo i {
  font-size: 60px;
  color: white;
}

.logo h1 {
  font-size: 40px;
  color: white;
  margin-top: 10px;
  font-weight: 700;
}

.auth-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.auth-card h2 {
  text-align: center;
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.status-section {
  text-align: center;
  padding: 30px 0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.not-authenticated {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  color: #e0245e;
}

.not-authenticated i {
  font-size: 50px;
}

.authenticated {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  color: #4caf50;
}

.authenticated i {
  font-size: 50px;
}

.features {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid #eee;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-item i {
  font-size: 24px;
  color: #667eea;
}

.feature-item span {
  font-size: 12px;
  color: #666;
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
</style>