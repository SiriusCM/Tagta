import {createRouter, createWebHashHistory} from 'vue-router'
import Index from '../views/Index.vue'

const routes = [
    {path: '/', redirect: '/index'},
    {path: '/index', name: 'Index', component: Index}
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router