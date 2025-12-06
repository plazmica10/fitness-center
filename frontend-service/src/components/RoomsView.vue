<template>
  <div>
    <h2>Rooms</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <ul>
        <li v-for="r in items" :key="r.room_id || r.id">{{ r.name }} — capacity: {{ r.capacity }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data(){ return { items: [], loading: true } },
  async mounted(){
    try { this.items = await api.get('/rooms') } catch(e){ console.error(e) }
    finally { this.loading = false }
  }
}
</script>
