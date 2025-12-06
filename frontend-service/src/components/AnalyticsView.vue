<template>
  <div>
    <div class="title-row">
      <h2>Analytics</h2>
    </div>

    <div v-if="loading"><div class="spinner"></div></div>

    <div v-else class="analytics-grid">
      <div class="kpi-card card">
        <h3>Total Revenue</h3>
        <div class="kpi-value">{{ totalRevenueDisplay }}</div>
        <div class="kpi-sub">Payments: {{ totalPayments }} • Avg: {{ avgPaymentDisplay }}</div>
      </div>

      <div class="chart-card card">
        <h3>Revenue by Class</h3>
        <canvas ref="revByClassCanvas"></canvas>
      </div>

      <div class="chart-card card">
        <h3>Daily Revenue</h3>
        <canvas ref="dailyRevenueCanvas"></canvas>
      </div>

      <div class="chart-card card">
        <h3>Rooms Occupancy (classes count)</h3>
        <canvas ref="roomsCanvas"></canvas>
      </div>

      <div class="chart-card card">
        <h3>Class Capacity Utilization</h3>
        <canvas ref="capacityCanvas"></canvas>
      </div>

      <div class="chart-card card">
        <h3>Trainer Workload Distribution</h3>
        <canvas ref="trainersCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import api from '../api'
import Chart from 'chart.js/auto'

const loading = ref(true)
const totalRevenue = ref(0)
const totalPayments = ref(0)
const avgPayment = ref(0)

const revByClassCanvas = ref(null)
const dailyRevenueCanvas = ref(null)
const roomsCanvas = ref(null)
const capacityCanvas = ref(null)
const trainersCanvas = ref(null)

let revByClassChart = null
let dailyChart = null
let roomsChart = null
let capacityChart = null
let trainersChart = null

const totalRevenueDisplay = computed(() => totalRevenue.value != null ? ('$'+Number(totalRevenue.value).toFixed(2)) : '-')
const avgPaymentDisplay = computed(() => avgPayment.value != null ? ('$'+Number(avgPayment.value).toFixed(2)) : '-')

// temporary holders for datasets
const revByClassDataset = { labels: [], data: [] }
const dailyDataset = { labels: [], data: [] }
const roomsDataset = { labels: [], data: [] }
const capDataset = { labels: [], data: [] }
const trainersDataset = { labels: [], data: [] }

function tryCreateCharts(){
  // revenue by class
  if(revByClassCanvas.value && revByClassCanvas.value.getContext){
    try{
      const ctx = revByClassCanvas.value.getContext('2d')
      revByClassChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: revByClassDataset.labels, datasets: [{ label: 'Revenue', data: revByClassDataset.data, backgroundColor: '#2563eb' }] },
        options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.7,
          plugins: {
            legend: { display: true }
          }
        }
      })
    }catch(e){ console.error('Failed to create revByClassChart', e) }
  } else console.warn('revByClassCanvas not available when creating charts')

  // daily
  if(dailyRevenueCanvas.value && dailyRevenueCanvas.value.getContext){
    try{
      const ctx = dailyRevenueCanvas.value.getContext('2d')
      dailyChart = new Chart(ctx, {
        type: 'line',
        data: { labels: dailyDataset.labels, datasets: [{ label: 'Daily Revenue', data: dailyDataset.data, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', fill: true }] },
        options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.7,
          plugins: {
            legend: { display: true }
          }
        }
      })
    }catch(e){ console.error('Failed to create dailyChart', e) }
  } else console.warn('dailyRevenueCanvas not available when creating charts')

  // rooms
  if(roomsCanvas.value && roomsCanvas.value.getContext){
    try{
      const ctx = roomsCanvas.value.getContext('2d')
      roomsChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: roomsDataset.labels, datasets: [{ label: 'Classes', data: roomsDataset.data, backgroundColor: '#f59e0b' }] },
        options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.7,
          plugins: {
            legend: { display: true }
          }
        }
      })
    }catch(e){ console.error('Failed to create roomsChart', e) }
  } else console.warn('roomsCanvas not available when creating charts')

  // capacity
  if(capacityCanvas.value && capacityCanvas.value.getContext){
    try{
      const ctx = capacityCanvas.value.getContext('2d')
      capacityChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: capDataset.labels, datasets: [{ label: '% Utilization', data: capDataset.data, backgroundColor: '#ef4444' }] },
        options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.7,
          plugins: {
            legend: { display: true }
          },
          scales: { y: { beginAtZero: true, max: 100 } } 
        }
      })
    }catch(e){ console.error('Failed to create capacityChart', e) }
  } else console.warn('capacityCanvas not available when creating charts')

  // trainers pie
  if(trainersCanvas.value && trainersCanvas.value.getContext){
    try{
      const ctx = trainersCanvas.value.getContext('2d')
      trainersChart = new Chart(ctx, {
        type: 'pie',
        data: { 
          labels: trainersDataset.labels, 
          datasets: [{ 
            label: 'Classes', 
            data: trainersDataset.data, 
            backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
          }] 
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: true,
          aspectRatio: 1.7,
          plugins: {
            legend: { display: true, position: 'right' }
          }
        }
      })
    }catch(e){ console.error('Failed to create trainersChart', e) }
  } else console.warn('trainersCanvas not available when creating charts')
}

async function loadData(){
  try{
    const [tot, byClass, rooms, cap, daily, classes, roomsList, trainers, trainerUtil] = await Promise.all([
      api.get('/analytics/revenue/total'),
      api.get('/analytics/revenue/by-class'),
      api.get('/analytics/rooms/occupancy'),
      api.get('/analytics/classes/capacity-utilization'),
      api.get('/analytics/revenue/daily'),
      api.get('/classes'),
      api.get('/rooms'),
      api.get('/trainers'),
      api.get('/analytics/trainers/utilization')
    ])

    // total
    totalRevenue.value = tot.total_revenue || tot.totalRevenue || 0
    totalPayments.value = tot.total_payments || tot.totalPayments || 0
    avgPayment.value = tot.average_payment || tot.averagePayment || 0

    // Build lookup maps
    const ensureArray = (v) => {
      if (!v) return []
      if (Array.isArray(v)) return v
      if (v && Array.isArray(v.data)) return v.data
      if (typeof v === 'object') return Object.values(v)
      return []
    }
    const classesArr = ensureArray(classes)
    const roomsListArr = ensureArray(roomsList)
    const classNamesMap = {}
    classesArr.forEach(c => { if(c) classNamesMap[c.class_id || c.id] = c.name })
    const roomNamesMap = {}
    roomsListArr.forEach(r => { if(r) roomNamesMap[r.room_id || r.id] = r.name })
    const trainersArr = ensureArray(trainers)
    const trainerNamesMap = {}
    trainersArr.forEach(t => { if(t) trainerNamesMap[t.trainer_id || t.id] = t.name })

    // Prepare chart datasets (do not create charts yet)
    const byClassArr = Array.isArray(byClass) ? byClass : (byClass && byClass.data) ? byClass.data : Object.values(byClass||{})
    // Limit to top 5 classes by revenue
    const top5Classes = byClassArr.slice(0, 5)
    const labelsClass = top5Classes.map(r => classNamesMap[r.class_id || r.classId] || r.class_id || r.classId || 'Unknown')
    const dataClass = top5Classes.map(r => Number(r.total_revenue || r.totalRevenue || 0))

    const dailyArr = Array.isArray(daily) ? daily : (daily && daily.data) ? daily.data : Object.values(daily||{})
    const labelsDaily = dailyArr.map(r => r.date)
    const dataDaily = dailyArr.map(r => Number(r.daily_revenue || r.dailyRevenue || 0))

    const roomsArr = Array.isArray(rooms) ? rooms : (rooms && rooms.data) ? rooms.data : Object.values(rooms||{})
    const labelsRooms = roomsArr.map(r => roomNamesMap[r.room_id || r.roomId] || r.room_id || r.roomId || 'Unknown')
    const dataRooms = roomsArr.map(r => Number(r.total_classes || r.totalClasses || 0))

    const capArr = Array.isArray(cap) ? cap : (cap && cap.data) ? cap.data : Object.values(cap||{})
    const labelsCap = capArr.map(r => r.name || r.class_id || '')
    const dataCap = capArr.map(r => Number(r.utilization_percentage || r.utilizationPercentage || 0))

    const trainerUtilArr = Array.isArray(trainerUtil) ? trainerUtil : (trainerUtil && trainerUtil.data) ? trainerUtil.data : Object.values(trainerUtil||{})
    const labelsTrainers = trainerUtilArr.map(t => trainerNamesMap[t.trainer_id || t.trainerId] || t.trainer_id || t.trainerId || 'Unknown')
    const dataTrainers = trainerUtilArr.map(t => Number(t.total_classes || t.totalClasses || 0))

    // Store prepared datasets on refs so we can create charts after DOM update
    revByClassDataset.labels = labelsClass
    revByClassDataset.data = dataClass
    dailyDataset.labels = labelsDaily
    dailyDataset.data = dataDaily
    roomsDataset.labels = labelsRooms
    roomsDataset.data = dataRooms
    capDataset.labels = labelsCap
    capDataset.data = dataCap
    trainersDataset.labels = labelsTrainers
    trainersDataset.data = dataTrainers

    // Now allow DOM to render canvases
    loading.value = false
    await nextTick()

    // Create charts now that canvases are present
    tryCreateCharts()

  }catch(err){
    console.error('Analytics load error', err)
  }finally{
    loading.value = false
  }
}

onMounted(()=>{ loadData() })
onBeforeUnmount(()=>{
  if(revByClassChart) revByClassChart.destroy()
  if(dailyChart) dailyChart.destroy()
  if(roomsChart) roomsChart.destroy()
  if(capacityChart) capacityChart.destroy()
  if(trainersChart) trainersChart.destroy()
})
</script>

<style scoped>
.analytics-grid { display:grid;grid-template-columns:repeat(2,1fr);gap:16px }
.kpi-card { display:flex;flex-direction:column;gap:8px;align-items:flex-start }
.kpi-value { font-size:1.6rem;font-weight:700 }
.chart-card { min-height:320px; padding:14px; display:flex; flex-direction:column; overflow:hidden; width:100% }
.chart-card h3 { margin-bottom:8px; align-self:flex-start; font-size:1rem }
.chart-card canvas { display:block; width:100% !important; height:auto !important; }
</style>
