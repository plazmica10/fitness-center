<template>
  <div class="member-dashboard">
    <div class="header-section">
      <div>
        <h2>My Classes</h2>
        <p class="subtitle">View and book classes</p>
      </div>
      <div class="balance-card">
        <div class="balance-label">Account Balance</div>
        <div class="balance-amount">${{ userBalance.toFixed(2) }}</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <!-- Tabs -->
      <div class="tabs">
        <button 
          :class="['tab', {active: activeTab === 'available'}]"
          @click="activeTab = 'available'"
        >
          Available Classes
        </button>
        <button 
          :class="['tab', {active: activeTab === 'booked'}]"
          @click="activeTab = 'booked'"
        >
          My Bookings
        </button>
      </div>

      <!-- Available Classes -->
      <div v-if="activeTab === 'available'" class="classes-grid">
        <div v-for="cls in availableClasses" :key="cls.class_id" class="class-card">
          <div class="class-header">
            <h3>{{ cls.name }}</h3>
            <span class="price-badge">${{ cls.price || 0 }}</span>
          </div>
          <div class="class-details">
            <p><strong>Trainer:</strong> {{ getTrainerName(cls.trainer_id) }}</p>
            <p><strong>Room:</strong> {{ getRoomName(cls.room_id) }}</p>
            <p><strong>Time:</strong> {{ formatDateTime(cls.start_time) }}</p>
            <p><strong>Capacity:</strong> {{ getAttendanceCount(cls.class_id) }}/{{ cls.capacity || 20 }}</p>
            <p v-if="cls.description" class="description">{{ cls.description }}</p>
          </div>
          <div class="class-actions">
            <button 
              v-if="isBooked(cls.class_id)"
              disabled
              class="btn-booked"
            >
              Already Booked
            </button>
            <button 
              v-else-if="isClassFull(cls)"
              disabled
              class="btn-full"
            >
              Class Full
            </button>
            <button 
              v-else
              @click="bookClass(cls)"
              class="btn-book"
              :disabled="booking"
            >
              {{ booking ? 'Booking...' : 'Book Class' }}
            </button>
          </div>
        </div>
        <div v-if="availableClasses.length === 0" class="empty-state">
          <p>No classes available at the moment.</p>
        </div>
      </div>

      <!-- My Bookings -->
      <div v-if="activeTab === 'booked'" class="classes-grid">
        <div v-for="booking in myBookings" :key="booking.event_id || booking.attendance_id" class="class-card booked">
          <div class="class-header">
            <h3>{{ booking.class_name || 'Unknown Class' }}</h3>
            <span v-if="booking.status" class="status-badge">{{ booking.status }}</span>
          </div>
          <div class="class-details">
            <p><strong>Time:</strong> {{ formatDateTime(booking.start_time) }}</p>
            <p><strong>Duration:</strong> {{ formatDuration(booking.start_time, booking.end_time) }}</p>
            <p><strong>Price:</strong> ${{ (booking.paid_amount || booking.price || 0).toFixed(2) }}</p>
            <p><strong>Payment:</strong> <span :class="`payment-status-${booking.payment_status}`">{{ booking.payment_status || 'pending' }}</span></p>
            <p><strong>Booked:</strong> {{ formatDateTime(booking.booking_time) }}</p>
          </div>
        </div>
        <div v-if="myBookings.length === 0" class="empty-state">
          <p>You haven't booked any classes yet.</p>
        </div>
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
      attendances: [],
      myBookings: [],
      userBalance: 0,
      userId: null,
      activeTab: 'available',
      loading: true,
      booking: false,
      error: null
    }
  },
  computed: {
    availableClasses() {
      // Show future classes only
      const now = new Date()
      return this.classes.filter(c => new Date(c.start_time) > now)
    },
    attendanceByClass() {
      // Group attendances by class_id
      const map = {}
      this.attendances.forEach(a => {
        if (!map[a.class_id]) map[a.class_id] = []
        map[a.class_id].push(a)
      })
      return map
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      try {
        // Get current user info from /me endpoint
        const currentUser = await api.get('/me')
        
        if (currentUser) {
          this.userId = currentUser._id || currentUser.id
          
          // Fetch balance from user-service
          try {
            const balanceData = await api.get(`/users/${this.userId}/balance`)
            this.userBalance = balanceData.balance || 0
          } catch (err) {
            console.warn('Could not fetch balance:', err)
            this.userBalance = 0
          }
        }

        // Fetch all data
        const [classesData, trainersData, roomsData, attendancesData] = await Promise.all([
          api.get('/classes'),
          api.get('/trainers'),
          api.get('/rooms'),
          api.get('/attendances')
        ])
        
        this.classes = classesData
        this.trainers = trainersData
        this.rooms = roomsData
        this.attendances = attendancesData

        // Fetch my bookings
        if (this.userId) {
          try {
            const bookingsData = await api.get('/bookings/my-bookings')
            this.myBookings = bookingsData.bookings || []
          } catch (err) {
            console.warn('Could not fetch bookings:', err)
            this.myBookings = []
          }
        }
      } catch (err) {
        console.error('Error fetching data:', err)
        this.error = 'Failed to load classes'
      } finally {
        this.loading = false
      }
    },
    getTrainerName(trainerId) {
      const trainer = this.trainers.find(t => (t.trainer_id || t.id) === trainerId)
      return trainer ? trainer.name : 'Unknown'
    },
    getRoomName(roomId) {
      const room = this.rooms.find(r => (r.room_id || r.id) === roomId)
      return room ? room.name : 'Unknown'
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
    formatDuration(startTime, endTime) {
      if (!startTime || !endTime) return 'N/A'
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diffMs = end - start
      const diffMins = Math.round(diffMs / 60000)
      return `${diffMins} min`
    },
    getAttendanceCount(classId) {
      const attendances = this.attendanceByClass[classId] || []
      return attendances.length
    },
    isClassFull(cls) {
      const capacity = cls.capacity || 20
      const attendanceCount = this.getAttendanceCount(cls.class_id)
      return attendanceCount >= capacity
    },
    isBooked(classId) {
      if (!this.userId) return false
      const attendances = this.attendanceByClass[classId] || []
      return attendances.some(a => a.member_id === this.userId)
    },
    async bookClass(cls) {
      if (!this.userId) {
        alert('User information not loaded. Please refresh the page.')
        return
      }

      const price = cls.price || 0
      if (this.userBalance < price) {
        alert(`Insufficient balance. You need $${price} but have $${this.userBalance.toFixed(2)}`)
        return
      }

      if (!confirm(`Book "${cls.name}" for $${price}?`)) {
        return
      }

      this.booking = true
      try {
        const response = await api.post('/bookings/book-class', {
          class_id: cls.class_id,
          member_id: this.userId
        })
        
        alert(`Successfully booked "${cls.name}"!\n\nPayment ID: ${response.payment_id}\nAmount: $${response.amount}`)
        
        // Refresh data to update balance and bookings
        await this.fetchData()
        
        // Switch to bookings tab
        this.activeTab = 'booked'
      } catch (err) {
        console.error('Booking error:', err)
        const errorMsg = err.response?.data?.detail || err.message || 'Unknown error'
        alert('Failed to book class: ' + errorMsg)
      } finally {
        this.booking = false
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
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

h2 {
  margin: 0 0 8px 0;
  color: #1e293b;
}

.subtitle {
  color: #64748b;
  margin: 0;
}

.balance-card {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
  text-align: right;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
}

.balance-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.balance-amount {
  font-size: 28px;
  font-weight: 700;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}

.tab {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 600;
  color: #64748b;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab:hover {
  color: #1e293b;
}

.tab.active {
  color: #10b981;
  border-bottom-color: #10b981;
}

.loading {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto;
  border: 4px solid #e2e8f0;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 40px;
  color: #dc2626;
  font-size: 16px;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.class-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.class-card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.class-card.booked {
  border-left: 4px solid #10b981;
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

.price-badge {
  background: #10b981;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
}

.status-badge {
  background: #e0e7ff;
  color: #4338ca;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.class-details {
  margin-bottom: 16px;
}

.class-details p {
  margin: 8px 0;
  color: #475569;
  font-size: 14px;
}

.description {
  color: #64748b;
  font-style: italic;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.class-actions {
  display: flex;
  gap: 10px;
}

.btn-book, .btn-booked, .btn-full {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.btn-book {
  background: #10b981;
  color: white;
}

.btn-book:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-book:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-booked {
  background: #cbd5e1;
  color: #475569;
  cursor: not-allowed;
}

.btn-full {
  background: #fee2e2;
  color: #991b1b;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  grid-column: 1 / -1;
}

.empty-state p {
  font-size: 16px;
}

.payment-status-completed {
  color: #059669;
  font-weight: 600;
}

.payment-status-pending {
  color: #f59e0b;
  font-weight: 600;
}

.payment-status-refunded {
  color: #dc2626;
  font-weight: 600;
}
</style>
