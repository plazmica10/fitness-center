<template>
  <div class="trainer-dashboard">
    <h2>My Classes</h2>
    <p class="subtitle">Manage your scheduled classes and view attendance</p>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-value">{{ myClasses.length }}</div>
          <div class="stat-label">Total Classes</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalAttendees }}</div>
          <div class="stat-label">Total Attendees</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ upcomingClasses }}</div>
          <div class="stat-label">Upcoming Classes</div>
        </div>
      </div>

      <div class="classes-list">
        <div v-for="cls in myClasses" :key="cls.class_id" class="class-item">
          <div class="class-main">
            <div class="class-info">
              <h3>{{ cls.name }}</h3>
              <div class="class-meta">
                <span class="meta-item">
                  <strong>Room:</strong> {{ getRoomName(cls.room_id) }}
                </span>
                <span class="meta-item">
                  <strong>Time:</strong> {{ formatDateTime(cls.start_time) }}
                </span>
                <span class="meta-item">
                  <strong>Capacity:</strong> {{ cls.capacity || 'N/A' }}
                </span>
                <span class="meta-item">
                  <strong>Price:</strong> ${{ cls.price || 'N/A' }}
                </span>
              </div>
            </div>
            <div class="class-capacity">
              <div class="capacity-badge" :class="getCapacityClass(cls)">
                {{ getAttendees(cls.class_id).length }}/{{ cls.capacity || 20 }}
              </div>
            </div>
          </div>
          
          <div class="class-attendees">
            <h4>Attendees ({{ getAttendees(cls.class_id).length }})</h4>
            <div v-if="getAttendees(cls.class_id).length > 0" class="attendees-list">
              <div v-for="attendee in getAttendees(cls.class_id)" :key="attendee.event_id" class="attendee-item">
                <span class="attendee-name">{{ getMemberName(attendee.member_id) }}</span>
                <span class="attendee-date">{{ formatDate(attendee.timestamp) }}</span>
              </div>
            </div>
            <div v-else class="no-attendees">
              No attendees yet
            </div>
          </div>
        </div>
      </div>

      <div v-if="myClasses.length === 0" class="empty-state">
        <p>You don't have any scheduled classes yet.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'TrainerDashboard',
  data() {
    return {
      classes: [],
      rooms: [],
      attendances: [],
      memberMap: {},
      myTrainerId: null,
      loading: true,
      error: null
    }
  },
  computed: {
    myClasses() {
      return this.classes.filter(cls => cls.trainer_id === this.myTrainerId)
    },
    totalAttendees() {
      return this.myClasses.reduce((sum, cls) => 
        sum + this.getAttendees(cls.class_id).length, 0
      )
    },
    upcomingClasses() {
      const now = new Date()
      return this.myClasses.filter(cls => 
        new Date(cls.start_time) > now
      ).length
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      try {
        // Get current trainer's ID
        const username = localStorage.getItem('username')
        const trainersData = await api.get('/trainers')
        const currentTrainer = trainersData.find(t => 
          t.name.toLowerCase().replace(/\s+/g, '') === username
        )
        
        if (!currentTrainer) {
          this.error = 'Trainer profile not found'
          this.loading = false
          return
        }
        
        this.myTrainerId = currentTrainer.trainer_id

        const [classesData, roomsData, attendancesData] = await Promise.all([
          api.get('/classes'),
          api.get('/rooms'),
          api.get('/attendances')
        ])
        
        this.classes = classesData
        this.rooms = roomsData
        this.attendances = attendancesData
        
        // Resolve member names by fetching each member by id (with cache)
        try {
          const memberMap = {}
          const uniqueMemberIds = [...new Set(this.attendances.map(a => a.member_id).filter(Boolean))]
          const unresolved = uniqueMemberIds.filter(id => !this.memberMap[id])
          if (unresolved.length) {
            const lookups = unresolved.map(async (id) => {
              try {
                const user = await api.get(`/users/${id}`)
                if (user && (user.id || user._id)) {
                  const userId = user.id || user._id
                  memberMap[userId] = user.full_name || user.username
                }
              } catch (e) {
                // ignore; fallback below
              }
            })
            await Promise.all(lookups)
          }
          // Fallback for any remaining ids
          uniqueMemberIds.forEach((id) => {
            if (!memberMap[id] && !this.memberMap[id]) {
              this.memberMap[id] = `Member_${id.substring(0, 8)}`
            }
          })
          this.memberMap = { ...this.memberMap, ...memberMap }
          console.log(`Loaded ${Object.keys(memberMap).length} member names`)
        } catch (e) {
          console.error('Failed to fetch member names:', e)
        }
      } catch (err) {
        console.error('Error fetching data:', err)
        this.error = 'Failed to load dashboard data'
      } finally {
        this.loading = false
      }
    },
    getRoomName(roomId) {
      const room = this.rooms.find(r => r.room_id === roomId)
      return room ? room.name : 'Unknown'
    },
    getAttendees(classId) {
      return this.attendances.filter(a => a.class_id === classId)
    },
    getMemberName(memberId) {
      return this.memberMap[memberId] || (memberId ? `Member_${memberId.substring(0, 8)}` : 'Unknown')
    },
    formatDateTime(dateTime) {
      if (!dateTime) return 'N/A'
      const date = new Date(dateTime)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatDate(dateTime) {
      if (!dateTime) return 'N/A'
      const date = new Date(dateTime)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    },
    getCapacityClass(cls) {
      const attendeeCount = this.getAttendees(cls.class_id).length
      const capacity = cls.capacity || 20
      const ratio = attendeeCount / capacity
      if (ratio >= 0.9) return 'capacity-full'
      if (ratio >= 0.7) return 'capacity-high'
      return 'capacity-normal'
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.trainer-dashboard {
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.class-item {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  transition: box-shadow 0.2s;
}

.class-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.class-main {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.class-info h3 {
  margin: 0 0 12px 0;
  color: #1e293b;
  font-size: 20px;
}

.class-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  color: #64748b;
  font-size: 14px;
}

.class-capacity {
  display: flex;
  align-items: center;
}

.capacity-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 16px;
}

.capacity-normal {
  background: #dcfce7;
  color: #166534;
}

.capacity-high {
  background: #fef3c7;
  color: #92400e;
}

.capacity-full {
  background: #fee2e2;
  color: #991b1b;
}

.class-attendees h4 {
  margin: 0 0 12px 0;
  color: #475569;
  font-size: 16px;
}

.attendees-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.attendee-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.attendee-name {
  font-weight: 500;
  color: #1e293b;
}

.attendee-date {
  font-size: 12px;
  color: #64748b;
}

.no-attendees {
  padding: 16px;
  text-align: center;
  color: #94a3b8;
  background: #f8fafc;
  border-radius: 6px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}
</style>
