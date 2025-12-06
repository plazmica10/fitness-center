import { createRouter, createWebHistory } from 'vue-router'
import ClassesView from './components/ClassesView.vue'
import TrainersView from './components/TrainersView.vue'
import RoomsView from './components/RoomsView.vue'
import AttendancesView from './components/AttendancesView.vue'
import PaymentsView from './components/PaymentsView.vue'
import AnalyticsView from './components/AnalyticsView.vue'

const routes = [
    { path: '/', redirect: '/classes' },
    { path: '/classes', component: ClassesView },
    { path: '/trainers', component: TrainersView },
    { path: '/rooms', component: RoomsView },
    { path: '/attendances', component: AttendancesView },
    { path: '/payments', component: PaymentsView },
    { path: '/analytics', component: AnalyticsView }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    strict: true
})

// Remove trailing slashes from routes
router.beforeEach((to, from, next) => {
    if (to.path !== '/' && to.path.endsWith('/')) {
        next({ path: to.path.slice(0, -1), query: to.query, hash: to.hash })
    } else {
        next()
    }
})

export default router
