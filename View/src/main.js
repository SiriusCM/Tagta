import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import './assets/styles.css'

axios.defaults.withCredentials = true

if (import.meta.env.PROD) {
    axios.defaults.baseURL = 'http://127.0.0.1:8000/'
} else {
    axios.defaults.baseURL = ''
}

createApp(App).use(router).mount('#app')