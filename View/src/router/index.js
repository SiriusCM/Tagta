import {createRouter, createWebHashHistory} from 'vue-router'
import Login from '../views/Login.vue'
import Index from '../views/Index.vue'

const routes = [
    {path: '/', redirect: '/login'},
    {path: '/login', name: 'Login', component: Login, meta: {public: true}},
    {path: '/index', name: 'Index', component: Index}
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 路由守卫：拦截未登录用户
router.beforeEach((to, from, next) => {
    const isPublic = to.meta && to.meta.public
    const hasToken = localStorage.getItem('identityToken')

    if (!isPublic && !hasToken) {
        next('/login')
    } else {
        next()
    }
})

export default router