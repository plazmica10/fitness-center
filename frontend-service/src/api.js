import axios from 'axios'

// No /api prefix — requests are sent to root paths (e.g. /classes)
const client = axios.create({ baseURL: '', timeout: 10000 })

function normalizePath(path) {
    if (!path.startsWith('/')) path = '/' + path
    const [p, q] = path.split('?')
    const segments = p.split('/').filter(Boolean)
    // If this is a top-level collection (e.g. /classes), ensure trailing slash
    if (segments.length === 1) {
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
