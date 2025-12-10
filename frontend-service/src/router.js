import { createRouter, createWebHistory } from 'vue-router'
import LandingView from './components/LandingView.vue'
import ClassesView from './components/ClassesView.vue'
import MemberDashboard from './components/MemberDashboard.vue'
import TrainerDashboard from './components/TrainerDashboard.vue'
import TrainersView from './components/TrainersView.vue'
import RoomsView from './components/RoomsView.vue'
import AttendancesView from './components/AttendancesView.vue'
import PaymentsView from './components/PaymentsView.vue'
import AnalyticsView from './components/AnalyticsView.vue'
import LoginView from './components/LoginView.vue'
import RegisterView from './components/RegisterView.vue'

const routes = [
    { path: '/', component: LandingView, meta: { public: true } },
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/register', component: RegisterView, meta: { public: true } },
    { path: '/classes', component: ClassesView, alias: '/classes/', meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/my-classes', component: MemberDashboard, alias: '/my-classes/', meta: { requiresAuth: true, roles: ['member'] } },
    { path: '/trainer-classes', component: TrainerDashboard, alias: '/trainer-classes/', meta: { requiresAuth: true, roles: ['trainer'] } },
    { path: '/trainers', component: TrainersView, alias: '/trainers/', meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/rooms', component: RoomsView, alias: '/rooms/', meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/attendances', component: AttendancesView, alias: '/attendances/', meta: { requiresAuth: true, roles: ['admin', 'trainer'] } },
    { path: '/payments', component: PaymentsView, alias: '/payments/', meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/analytics', component: AnalyticsView, alias: '/analytics/', meta: { requiresAuth: true, roles: ['admin'] } }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard for authentication and authorization
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    // If already authenticated, prevent navigating to public auth pages
    if (token && (to.path === '/login' || to.path === '/register')) {
        if (role === 'admin') return next('/analytics')
        if (role === 'trainer') return next('/trainer-classes')
        if (role === 'member') return next('/my-classes')
        return next('/')
    }

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.meta.requiresAuth && to.meta.roles && !to.meta.roles.includes(role)) {
        // User doesn't have permission for this route - redirect to their home
        if (role === 'admin') {
            next('/analytics')
        } else if (role === 'trainer') {
            next('/trainer-classes')
        } else if (role === 'member') {
            next('/my-classes')
        } else {
            next('/login')
        }
    } else {
        next()
    }
})

export default router