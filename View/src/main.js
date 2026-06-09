import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './assets/styles.css'
import './assets/index.css'

axios.defaults.withCredentials = true

if (import.meta.env.PROD) {
    axios.defaults.baseURL = 'https://gcsng.jr.jd.com/wjzgTest/'
} else {
    axios.defaults.baseURL = ''
}

// 全局 401 拦截器
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('user')
            localStorage.removeItem('identityToken')
            localStorage.removeItem('appleUserId')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

createApp(App).use(router).mount('#app')