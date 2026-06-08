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

createApp(App).use(router).mount('#app')