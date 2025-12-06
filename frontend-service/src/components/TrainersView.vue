<template>
<div>
    <div class="title-row">
    <h2>Trainers</h2>
    <button class="btn" @click="showAdd = !showAdd">{{ showAdd ? 'Close' : 'Add Trainer' }}</button>
    </div>

    <div v-if="showAdd" class="card">
      <h3>Add Trainer</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;align-items:center">
        <input class="search" v-model="newTrainer.name" placeholder="Name" />
        <input class="search" v-model="newTrainer.specialization" placeholder="Specialization" />
        <button class="btn" @click="addTrainer">Save</button>
        <button class="btn" style="background:#ef4444" @click="cancelAdd">Cancel</button>
      </div>
    </div>

    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
    <div v-if="items.length===0" class="muted-block">No trainers found.</div>
    <div class="trainer-grid">
        <div class="trainer-card" v-for="t in items" :key="t.trainer_id || t.id">
        <div class="trainer-avatar">
            <img :src="avatarFor(t.name)" :alt="t.name" style="width:80px;height:80px;border-radius:50%" />
        </div>
        <div class="trainer-info">
            <h3>{{ t.name }}</h3>
            <p class="small">Rating: {{ t.rating ?? '-' }}</p>

            <div v-if="editId === (t.trainer_id || t.id)">
            <input class="search" v-model="editSpec" placeholder="Specialization" />
            <div style="margin-top:8px">
                <button class="btn" @click="saveSpec(t)">Save</button>
                <button class="btn" style="background:#94a3b8;margin-left:8px" @click="cancelEdit">Cancel</button>
            </div>
            </div>
            <div v-else>
            <p class="muted" style="margin-top:6px">{{ t.specialization || '' }}</p>
            </div>

            <p class="muted small" v-if="t.bio" style="margin-top:6px">{{ t.bio }}</p>
        </div>

        <div class="card-actions">
            <button class="btn" @click="startEdit(t)">Edit</button>
            <button class="btn" style="background:#ef4444;margin-left:8px" @click="removeTrainer(t)">Delete</button>
        </div>
        </div>
    </div>
    </div>
</div>
</template>

<script>
import api from '../api'

export default {
  data(){ return { items: [], loading: true, showAdd: false, newTrainer: { name:'', specialization:'' }, editId: null, editSpec: '' } },
  methods: {
    avatarFor(name){
      return 'https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg'
    },
    async addTrainer(){
      if(!this.newTrainer.name || !this.newTrainer.specialization){
        alert('Name and specialization are required')
        return
      }
      try{
        const payload = { name: this.newTrainer.name, specialization: this.newTrainer.specialization }
        const created = await api.post('/trainers', payload)
        this.items.unshift(created)
        this.newTrainer = { name:'', specialization:'' }
        this.showAdd = false
      }catch(e){ console.error('Add trainer failed', e); alert('Failed to add trainer') }
    },
    cancelAdd(){ this.newTrainer = { name:'', specialization:'' }; this.showAdd = false },
    startEdit(t){ this.editId = (t.trainer_id || t.id); this.editSpec = t.specialization || '' },
    cancelEdit(){ this.editId = null; this.editSpec = '' },
    async saveSpec(t){
      try{
        const id = t.trainer_id || t.id
        const payload = { trainer_id: id, name: t.name, specialization: this.editSpec, rating: t.rating }
          const updated = await api.put(`/trainers/${id}`, payload)
          const idx = this.items.findIndex(x => (x.trainer_id||x.id) === id)
          if(idx !== -1) this.items.splice(idx, 1, updated)
          this.cancelEdit()
        }catch(e){
          console.error('Save specialization failed', e)
          const msg = (e && e.response && e.response.data && e.response.data.detail) ? e.response.data.detail : (e.message || 'Failed to save')
          alert(msg)
        }
    },
    async removeTrainer(t){
      if(!confirm(`Delete trainer ${t.name}?`)) return
      try{
        const id = t.trainer_id || t.id
        await api.del(`/trainers/${id}`)
        this.items = this.items.filter(x => (x.trainer_id||x.id) !== id)
      }catch(e){ console.error('Delete failed', e); alert('Failed to delete') }
    }
  },
  async mounted(){
    try{
      const res = await api.get('/trainers')
      const arr = Array.isArray(res) ? res : (res && Array.isArray(res.data) ? res.data : (res ? Object.values(res) : []))
      this.items = arr
    }catch(e){ console.error('TrainersView error', e) }
    finally{ this.loading = false }
  }
}
</script>
