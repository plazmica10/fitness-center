import axios from 'axios'

// Use /api prefix for all API requests
const client = axios.create({ baseURL: '/api', timeout: 10000 })

// Add auth token to requests
client.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Handle 401 errors (unauthorized)
client.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

function normalizePath(path) {
    if (!path.startsWith('/')) path = '/' + path
    const [p, q] = path.split('?')
    const segments = p.split('/').filter(Boolean)

    // List of auth/user endpoints that should NOT have trailing slash
    const authEndpoints = ['me', 'login', 'register', 'verify-token']

    // If this is a top-level collection (e.g. /classes), ensure trailing slash
    // BUT skip auth endpoints and balance endpoints
    if (segments.length === 1 && !authEndpoints.includes(segments[0]) && !path.includes('balance')) {
        const base = `/${segments[0]}/`
        return q ? `${base}?${q}` : base
    }
    // otherwise return unchanged (preserve id paths like /classes/123)
    return path
}

export default {
    get(path, params) { const p = normalizePath(path); return client.get(p, { params }).then(r => r.data) },
    post(path, data) { const p = normalizePath(path); return client.post(p, data).then(r => r.data) },
    put(path, data) { const p = normalizePath(path); return client.put(p, data).then(r => r.data) },
    del(path) { const p = normalizePath(path); return client.delete(p).then(r => r.data) }
}
