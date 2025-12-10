<template>
  <div>
    <div class="card title-row">
      <h2>Rooms</h2>
      <div style="display:flex; gap:8px; align-items:center;">
        <button class="btn" @click="openCreate">+ New Room</button>
      </div>
    </div>

    <div v-if="loading"><div class="spinner"></div></div>

    <div v-else>
      <div v-if="items.length===0" class="card muted-block">No rooms yet. Create your first room.</div>

      <div class="rooms-grid">
        <div class="room-card card" v-for="r in items" :key="r.room_id || r.id">
          <div class="room-head">
            <div class="room-name">{{ r.name }}</div>
            <div class="room-capacity small">Capacity: {{ r.capacity }}</div>
          </div>
          <div class="room-meta small">
            <span :class="['tag', r.has_equipment ? 'tag-on' : 'tag-off']">
              {{ r.has_equipment ? 'Equipment available' : 'No equipment' }}
            </span>
          </div>
          <div class="card-actions">
            <button class="btn" @click="openEdit(r)">Edit</button>
            <button class="btn btn-danger" @click="confirmDelete(r)" style="background:#ef4444">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Create/Edit Form -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal-card">
        <h3 style="margin:0 0 12px 0;">{{ formTitle }}</h3>
        <form @submit.prevent="saveRoom" class="form-grid">
          <label>
            <div>Name</div>
            <input class="text-input" v-model="form.name" required placeholder="e.g. Studio A" />
          </label>
          <label>
            <div>Capacity</div>
            <input class="text-input" v-model.number="form.capacity" type="number" min="1" required />
          </label>
          <label class="checkbox-row" style="grid-column:1/-1">
            <input v-model="form.has_equipment" type="checkbox" />
            <span>Has equipment</span>
          </label>
          <div style="display:flex; gap:8px; margin-top:8px; grid-column:1/-1; justify-content:flex-end;">
            <button class="btn" type="button" @click="closeForm" style="background:#475569">Cancel</button>
            <button class="btn" type="submit">Save</button>
          </div>
          <div v-if="error" class="small" style="color:#ef4444; grid-column:1/-1">{{ error }}</div>
        </form>
      </div>
    </div>
  </div>
  
</template>

<script>
import api from '../api'
export default {
  data(){
    return {
      items: [],
      loading: true,
      showForm: false,
      editingId: null,
      form: { name: '', capacity: 10, has_equipment: false },
      error: ''
    }
  },
  computed: {
    formTitle(){ return this.editingId ? 'Edit Room' : 'Create Room' }
  },
  methods: {
    async loadRooms(){
      this.loading = true
      try { this.items = await api.get('/rooms') } catch(e){ console.error(e) }
      finally { this.loading = false }
    },
    openCreate(){
      this.editingId = null
      this.form = { name: '', capacity: 10, has_equipment: false }
      this.error = ''
      this.showForm = true
    },
    openEdit(r){
      this.editingId = r.room_id || r.id
      this.form = { name: r.name || '', capacity: Number(r.capacity)||0, has_equipment: !!r.has_equipment }
      this.error = ''
      this.showForm = true
    },
    closeForm(){ this.showForm = false },
    async saveRoom(){
      this.error = ''
      try {
        if(this.editingId){
          await api.put(`/rooms/${this.editingId}`, this.form)
        } else {
          await api.post('/rooms', this.form)
        }
        this.showForm = false
        await this.loadRooms()
      } catch(e){
        console.error(e)
        this.error = e?.response?.data?.detail || 'Save failed'
      }
    },
    async confirmDelete(r){
      if(!confirm(`Delete room "${r.name}"?`)) return
      try {
        const id = r.room_id || r.id
        await api.del(`/rooms/${id}`)
        await this.loadRooms()
      } catch(e){ console.error(e); alert('Delete failed') }
    }
  },
  async mounted(){
    await this.loadRooms()
  }
}
</script>

<style scoped>
.rooms-grid { display:grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap:16px }
.room-card { display:flex; flex-direction:column; gap:6px }
.room-head { display:flex; align-items:center; justify-content:space-between }
.room-name { font-weight:600 }
.room-meta { margin-top:4px }
.tag { display:inline-block; padding:4px 8px; border-radius:999px; font-size:12px }
.tag-on { background:#e8f3ff; color:#2563eb }
.tag-off { background:#f1f5f9; color:#64748b }
.form-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:12px }
.form-grid input[type="text"], .form-grid input[type="number"], .form-grid input[type="datetime-local"], .form-grid select { padding:8px 10px; border:1px solid #e6eefb; border-radius:8px }
.checkbox-row { display:flex; align-items:center; gap:8px; margin-top:6px }
.modal-overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); display:flex; align-items:center; justify-content:center; z-index:1000 }
.modal-card { width:min(560px,92vw); background:#fff; border-radius:12px; padding:18px; box-shadow:0 16px 40px rgba(0,0,0,0.25) }
</style>
