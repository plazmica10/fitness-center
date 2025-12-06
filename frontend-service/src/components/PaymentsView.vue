<template>
  <div>
    <h2>Payments</h2>
    <div v-if="loading"><div class="spinner"></div></div>
    <div v-else>
      <table>
        <thead><tr><th>Member</th><th>Amount</th><th>Method</th><th>Created</th></tr></thead>
        <tbody>
          <tr v-for="p in items" :key="p.payment_id || p.id">
            <td>{{ p.member_id }}</td>
            <td>{{ p.amount }}</td>
            <td>{{ p.method }}</td>
            <td class="small">{{ p.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api'
export default {
  data(){ return { items: [], loading: true } },
  async mounted(){
    try { this.items = await api.get('/payments') } catch(e){ console.error(e) }
    finally { this.loading = false }
  }
}
</script>
