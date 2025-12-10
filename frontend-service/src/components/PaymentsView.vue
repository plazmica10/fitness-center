<template>
  <div>
    <h2>Payments</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <table>
        <thead><tr><th>Member</th><th>Class</th><th>Amount</th><th>Timestamp</th></tr></thead>
        <tbody>
          <tr v-for="p in items" :key="p.payment_id || p.id">
            <td>{{ getMemberName(p.member_id) }}</td>
            <td>{{ classesMap[p.class_id] || 'Unknown Class' }}</td>
            <td>${{ p.amount }}</td>
            <td class="small">{{ formatDateTime(p.timestamp) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data(){ return { items: [], loading: true, memberMap: {}, classesMap: {} } },
  methods: {
    getMemberName(memberId) {
      return this.memberMap[memberId] || 'Member ' + (memberId ? memberId.substring(0, 8) : 'Unknown')
    },
    formatDateTime(dateTime) {
      if (!dateTime) return 'N/A'
      const date = new Date(dateTime)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },
  async mounted(){
    try {
      const [payments, classes] = await Promise.all([api.get('/payments'), api.get('/classes')])
      const ensureArray = (v) => {
        if (!v) return []
        if (Array.isArray(v)) return v
        if (v && Array.isArray(v.data)) return v.data
        if (typeof v === 'object') return Object.values(v)
        return []
      }
      
      const paymentsArr = ensureArray(payments)
      const classesArr = ensureArray(classes)
      
      // Build classes map
      const cmap = {}
      classesArr.forEach(c => { if(c) cmap[c.class_id || c.id] = c.name })
      this.classesMap = cmap
      
      // Fetch member names by ID (cached lookups)
      const memberMap = {}
      const uniqueMemberIds = [...new Set(paymentsArr.map(p => p.member_id).filter(Boolean))]
      const unresolved = uniqueMemberIds.filter(id => !this.memberMap[id])
      if (unresolved.length) {
        try {
          const lookups = unresolved.map(async (id) => {
            try {
              const user = await api.get(`/users/${id}`)
              if (user && (user.id || user._id)) {
                const userId = user.id || user._id
                memberMap[userId] = user.full_name || user.username
              }
            } catch (e) {
              // leave unmapped; fallback below
            }
          })
          await Promise.all(lookups)
        } catch (e) {
          // ignore; fallback applies below
        }
      }

      // Fallback for any unmapped IDs (show short token)
      uniqueMemberIds.forEach((id) => {
        if (!memberMap[id] && !this.memberMap[id]) {
          this.memberMap[id] = `Member_${id.substring(0, 8)}`
        }
      })

      // Merge newly resolved names
      this.memberMap = { ...this.memberMap, ...memberMap }
      console.log(`Resolved ${Object.keys(memberMap).length} member names for payments`)
      
      this.items = paymentsArr
    } catch(e){ 
      console.error('Error loading payments:', e) 
    }
    finally { 
      this.loading = false 
    }
  }
}
</script>
