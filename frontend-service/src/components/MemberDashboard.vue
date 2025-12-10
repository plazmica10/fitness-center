<template>
  <div class="member-dashboard">
    <h2>My Classes</h2>
    <p class="subtitle">View and manage your class attendance</p>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div class="classes-grid">
        <div v-for="cls in classes" :key="cls.id" class="class-card">
          <div class="class-header">
            <h3>{{ cls.name }}</h3>
            <span class="class-type">{{ cls.type }}</span>
          </div>
          <div class="class-details">
            <p><strong>Trainer:</strong> {{ getTrainerName(cls.trainer_id) }}</p>
            <p><strong>Room:</strong> {{ getRoomName(cls.room_id) }}</p>
            <p><strong>Time:</strong> {{ formatDateTime(cls.start_time) }}</p>
            <p><strong>Duration:</strong> {{ cls.duration }} minutes</p>
            <p><strong>Capacity:</strong> {{ cls.current_capacity }}/{{ cls.max_capacity }}</p>
          </div>
          <div class="class-actions">
            <button 
              v-if="isAttending(cls.id)" 
              @click="cancelAttendance(cls.id)"
              class="btn-cancel"
            >
              Cancel Attendance
            </button>
            <button 
              v-else-if="cls.current_capacity < cls.max_capacity"
              @click="bookClass(cls.id)"
              class="btn-book"
            >
              Book Class
            </button>
            <span v-else class="class-full">Class Full</span>
          </div>
        </div>
      </div>

      <div v-if="classes.length === 0" class="empty-state">
        <p>No classes available at the moment.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'MemberDashboard',
  data() {
    return {
      classes: [],
      trainers: [],
      rooms: [],
      myAttendances: [],
      loading: true,
      error: null
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      try {
        const [classesData, trainersData, roomsData, attendancesData] = await Promise.all([
          api.get('/classes'),
          api.get('/trainers'),
          api.get('/rooms'),
          api.get('/attendances')
        ])
        
        this.classes = classesData
        this.trainers = trainersData
        this.rooms = roomsData
        this.myAttendances = attendancesData.filter(a => 
          a.member_username === localStorage.getItem('username')
        )
      } catch (err) {
        console.error('Error fetching data:', err)
        this.error = 'Failed to load classes'
      } finally {
        this.loading = false
      }
    },
    getTrainerName(trainerId) {
      const trainer = this.trainers.find(t => t.id === trainerId)
      return trainer ? trainer.name : 'Unknown'
    },
    getRoomName(roomId) {
      const room = this.rooms.find(r => r.id === roomId)
      return room ? room.name : 'Unknown'
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
    },
    isAttending(classId) {
      return this.myAttendances.some(a => a.class_id === classId)
    },
    async bookClass(classId) {
      try {
        await api.post('/attendances', {
          class_id: classId,
          member_username: localStorage.getItem('username'),
          attendance_date: new Date().toISOString()
        })
        await this.fetchData()
      } catch (err) {
        alert('Failed to book class: ' + (err.response?.data?.detail || err.message))
      }
    },
    async cancelAttendance(classId) {
      const attendance = this.myAttendances.find(a => a.class_id === classId)
      if (!attendance) return
      
      try {
        await api.del(`/attendances/${attendance.id}`)
        await this.fetchData()
      } catch (err) {
        alert('Failed to cancel attendance: ' + (err.response?.data?.detail || err.message))
      }
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.member-dashboard {
  padding: 20px;
}

h2 {
  margin-bottom: 8px;
  color: #1e293b;
}

.subtitle {
  color: #64748b;
  margin-bottom: 24px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 16px;
}

.error {
  color: #dc2626;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.class-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  transition: box-shadow 0.2s;
}

.class-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

.class-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
}

.class-type {
  background: #e0e7ff;
  color: #4338ca;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.class-details {
  margin-bottom: 16px;
}

.class-details p {
  margin: 8px 0;
  color: #475569;
  font-size: 14px;
}

.class-actions {
  display: flex;
  gap: 10px;
}

.btn-book, .btn-cancel {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-book {
  background: #10b981;
  color: white;
}

.btn-book:hover {
  background: #059669;
}

.btn-cancel {
  background: #ef4444;
  color: white;
}

.btn-cancel:hover {
  background: #dc2626;
}

.class-full {
  flex: 1;
  text-align: center;
  padding: 10px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}
</style>
