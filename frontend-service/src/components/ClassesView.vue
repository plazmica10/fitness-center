<template>
  <div>
    <h2>Classes</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <div v-if="groupedRooms.length===0" class="muted-block">No classes found.</div>

      <div class="rooms-list">
        <div class="room-group" v-for="room in groupedRooms" :key="room.room_id || room.id">
          <div class="room-header card">
            <h3>
              <template v-if="room.room_name">{{ room.room_name }}</template>
              <template v-else-if="room.name">{{ room.name }}</template>
              <template v-else-if="room.room_id">
                <span class="inline-spinner"></span>
                {{ room.room_id }}
              </template>
              <template v-else>Room {{ room.room_id || room.id }}</template>
            </h3>
            <p class="small muted">{{ room.room_meta || '' }}</p>
          </div>

          <div class="class-grid">
            <div class="class-card" v-for="c in room.classes" :key="c.class_id || c.id">
              <div class="class-main">
                <div class="class-name">{{ c.name }}</div>
                <div class="class-time small">{{ formatDate(c.start_time) }} • {{ formatTime(c.start_time) }} — {{ formatTime(c.end_time) }}</div>
              </div>
              <div class="class-meta">
                <div class="small">Trainer:
                  <template v-if="trainersMap[c.trainer_id]">{{ trainersMap[c.trainer_id] }}</template>
                  <template v-else-if="c.trainer_id"> <span class="inline-spinner"></span> {{ c.trainer_id }}</template>
                  <template v-else>-</template>
                </div>
              </div>
              <div class="class-price small">Price: {{ c.price != null ? ('$'+c.price) : '-' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() { return { items: [], loading: true, roomsMap: {}, trainersMap: {} } },
  async mounted(){
    try {
      // Fetch classes, rooms, trainers and attendances in parallel
      const results = await Promise.all([
        api.get('/classes'),
        api.get('/rooms'),
        api.get('/trainers'),
        api.get('/attendances')
      ])

      let [classes, rooms, trainers, attendances] = results

      // Debug: log fetched shapes to help diagnose runtime issues
      console.debug('ClassesView fetched:', { classes, rooms, trainers })

      // Normalize responses: accept arrays, {data: [...]}, or objects
      const ensureArray = (v) => {
        if (!v) return []
        if (Array.isArray(v)) return v
        if (v && Array.isArray(v.data)) return v.data
        if (typeof v === 'object') return Object.values(v)
        return []
      }

      classes = ensureArray(classes)
      rooms = ensureArray(rooms)
      trainers = ensureArray(trainers)
      attendances = ensureArray(attendances)

      // Build attendance counts per class (only non-cancelled)
      const attendanceCounts = {}
      attendances.forEach(a => {
        if(!a) return
        if(a.status === 'cancelled') return
        const cid = a.class_id || a.classId || a.class
        if(!cid) return
        attendanceCounts[cid] = (attendanceCounts[cid] || 0) + 1
      })

      // Build maps for quick lookup
      const roomsMap = {}
      rooms.forEach(r => { if (r) roomsMap[r.room_id || r.id] = r.name })

      const trainersMap = {}
      trainers.forEach(t => { if (t) trainersMap[t.trainer_id || t.id] = t.name })

      // Attach readable names to classes
      const enriched = classes.map(c => {
        const attendee_count = attendanceCounts[c.class_id] || attendanceCounts[c.id] || 0
        const capacity = c.capacity == null ? null : Number(c.capacity)
        const fullness = capacity ? (attendee_count / capacity) : 0
        return ({
          ...c,
          room_name: roomsMap[c.room_id] || c.room_name || null,
          trainer_name: trainersMap[c.trainer_id] || c.trainer_name || null,
          attendee_count,
          capacity,
          fullness
        })
      })
      this.items = enriched
      this.roomsMap = roomsMap
      this.trainersMap = trainersMap

      // Group classes by room
      const byRoom = {}
      enriched.forEach(c => {
        const rid = c.room_id || c.room_id || 'ungrouped'
        if(!byRoom[rid]) byRoom[rid] = { room_id: rid, room_name: c.room_name || (this.roomsMap[rid] || null), classes: [] }
        byRoom[rid].classes.push(c)
      })

      // Include rooms that have no classes as empty groups
      rooms.forEach(r => {
        const rid = r.room_id || r.id
        if(!byRoom[rid]) byRoom[rid] = { ...r, room_name: r.name || null, classes: [] }
      })

      // Sort classes inside each room by fullness (descending: fullest first)
      Object.values(byRoom).forEach(rg => {
        rg.classes.sort((x,y)=> {
          // treat null capacity as lowest fullness
          const fx = x.fullness || 0
          const fy = y.fullness || 0
          if(fy === fx) return 0
          return fy - fx
        })
      })

      // Convert to array and sort by number of classes (descending), then by room name
      this.groupedRooms = Object.values(byRoom).sort((a,b)=>{
        const ca = (a.classes && a.classes.length) || 0
        const cb = (b.classes && b.classes.length) || 0
        if(cb !== ca) return cb - ca
        const an = (a.room_name||'').toString().toLowerCase()
        const bn = (b.room_name||'').toString().toLowerCase()
        return an < bn ? -1 : (an>bn?1:0)
      })
    } catch(e){ console.error('ClassesView mounted error:', e) }
    finally { this.loading = false }
  }
}
</script>

<script setup>
// helper formatting functions for template
const pad = (n) => n.toString().padStart(2,'0')
function formatDate(v){
  try{
    const d = new Date(v)
    if(isNaN(d)) return v
    const mm = pad(d.getMonth()+1)
    const dd = pad(d.getDate())
    const yyyy = d.getFullYear()
    return `${mm}/${dd}/${yyyy}`
  }catch(e){ return v }
}
function formatTime(v){
  try{
    const d = new Date(v)
    if(isNaN(d)) return v
    let h = d.getHours()
    const m = pad(d.getMinutes())
    const ampm = h >= 12 ? 'PM' : 'AM'
    h = h % 12
    if(h === 0) h = 12
    return `${h}:${m} ${ampm}`
  }catch(e){ return v }
}
</script>

<style scoped>
.rooms-list { display:flex;flex-direction:column;gap:18px }
.room-header { display:flex;align-items:center;justify-content:space-between }
.class-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;margin-top:12px }
.class-card { background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 6px 14px rgba(15,23,42,0.04);display:flex;flex-direction:column;gap:8px;min-width:320px }
.class-main { font-weight:600 }
.class-time { color:var(--muted); white-space:nowrap }
.class-meta { display:flex;justify-content:flex-start;color:var(--muted);font-size:0.9rem;gap:12px }
.class-price { margin-top:8px; color:var(--muted); font-weight:600 }
.inline-spinner { display:inline-block; width:14px; height:14px; border-radius:50%; border:2px solid #e6eefb; border-top-color:var(--primary); animation:spin 1s linear infinite; vertical-align:middle; margin-right:6px }
</style>
