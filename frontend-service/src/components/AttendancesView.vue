<template>
  <div>
    <h2>Attendances</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <div v-if="groupByClass" class="grouped-attendances">
        <div v-for="(attendances, className) in groupedByClass" :key="className" class="class-group">
          <h3 class="class-name">{{ className }}</h3>
          <table>
            <thead><tr><th>Member</th><th>Status</th><th>Timestamp</th></tr></thead>
            <tbody>
              <tr v-for="a in attendances" :key="a.event_id">
                <td>{{ getMemberName(a.member_id) }}</td>
                <td><span :class="'status-badge status-' + a.status.replace('-', '')">{{ a.status }}</span></td>
                <td class="small">{{ formatDateTime(a.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <table v-else>
        <thead><tr><th>Member</th><th>Class</th><th>Status</th><th>Timestamp</th></tr></thead>
        <tbody>
          <tr v-for="a in items" :key="a.event_id">
            <td>{{ getMemberName(a.member_id) }}</td>
            <td>{{ classesMap[a.class_id] || a.class_id }}</td>
            <td><span :class="'status-badge status-' + a.status.replace('-', '')">{{ a.status }}</span></td>
            <td class="small">{{ formatDateTime(a.timestamp) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data(){ return { items: [], loading: true, classesMap: {}, memberMap: {}, groupByClass: false } },
  computed: {
    groupedByClass() {
      if (!this.groupByClass) return {}
      const grouped = {}
      this.items.forEach(a => {
        const className = this.classesMap[a.class_id] || 'Unknown Class'
        if (!grouped[className]) grouped[className] = []
        grouped[className].push(a)
      })
      return grouped
    }
  },
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
    // Check if trainer to enable grouping
    const role = localStorage.getItem('role')
    this.groupByClass = role === 'trainer'
    
    try {
      const [att, classes] = await Promise.all([api.get('/attendances'), api.get('/classes')])
      const ensureArray = (v) => {
        if (!v) return []
        if (Array.isArray(v)) return v
        if (v && Array.isArray(v.data)) return v.data
        if (typeof v === 'object') return Object.values(v)
        return []
      }
      const attArr = ensureArray(att)
      const classesArr = ensureArray(classes)
      const cmap = {}
      classesArr.forEach(c => { if(c) cmap[c.class_id || c.id] = c.name })
      this.classesMap = cmap
      
      // Build member map from unique member_ids
      const uniqueMemberIds = [...new Set(attArr.map(a => a.member_id).filter(Boolean))]
      const memberMap = {}
      
      // Fetch member names by ID (cached lookups)
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
          
          console.log(`Loaded ${Object.keys(memberMap).length} member names`)
        } catch (err) {
          console.log('Could not fetch users, using fallback names:', err)
        }
      }
      
      // Fallback: Generate simple member names for any unmapped IDs
      uniqueMemberIds.forEach((id) => {
        if (!memberMap[id]) {
          const hash = id.split('-')[0]
          memberMap[id] = `Member_${hash}`
        }
      })
      
      this.memberMap = { ...this.memberMap, ...memberMap }
      this.items = attArr
    } catch(e){ console.error('AttendancesView error', e) }
    finally { this.loading = false }
  }
}
</script>

<style scoped>
.grouped-attendances {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.class-group {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}

.class-name {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-checkedin {
  background: #dcfce7;
  color: #166534;
}

.status-checkedout {
  background: #dbeafe;
  color: #1e40af;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}
</style>
