<template>
  <div>
    <h2>Attendances</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <table>
        <thead><tr><th>Member</th><th>Class</th><th>Status</th><th>Created</th></tr></thead>
        <tbody>
          <tr v-for="a in items" :key="a.event_id || a.attendance_id || a.id">
            <td>{{ a.member_id }}</td>
            <td>{{ classesMap[a.class_id] || a.class_id }}</td>
            <td>{{ a.status }}</td>
            <td class="small">{{ a.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data(){ return { items: [], loading: true, classesMap: {} } },
  async mounted(){
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
      this.items = attArr
    } catch(e){ console.error('AttendancesView error', e) }
    finally { this.loading = false }
  }
}
</script>
