<template>
  <div class="landing-page">
    <div class="hero">
      <h1>Welcome to Fitness Center</h1>
      <p class="subtitle">Manage your fitness journey with ease</p>
      <div class="cta-buttons">
        <template v-if="!isLoggedIn">
          <router-link to="/login" class="btn btn-primary">Login</router-link>
          <router-link to="/register" class="btn btn-secondary">Get Started</router-link>
        </template>
        <template v-else>
          <router-link :to="dashboardPath" class="btn btn-primary">Go to Dashboard</router-link>
        </template>
      </div>
    </div>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">📅</div>
        <h3>Class Scheduling</h3>
        <p>Browse and book fitness classes with professional trainers</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">👥</div>
        <h3>Expert Trainers</h3>
        <p>Work with certified fitness professionals</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Track Progress</h3>
        <p>Monitor your attendance and payments</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">💳</div>
        <h3>Easy Payments</h3>
        <p>Manage your membership and class payments</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LandingView',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    role() {
      return localStorage.getItem('role') || ''
    },
    dashboardPath() {
      if (this.role === 'admin') return '/analytics'
      if (this.role === 'trainer') return '/trainer-classes'
      if (this.role === 'member') return '/my-classes'
      return '/'
    }
  },
  mounted() {
    // If logged in and user navigates to landing, redirect to their dashboard
    if (this.isLoggedIn) {
      this.$router.replace(this.dashboardPath)
    }
  }
}
</script>

<style scoped>
.landing-page {
  min-height: calc(100vh - 100px);
}

.hero {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 60px;
}

.hero h1 {
  font-size: 3rem;
  margin: 0 0 20px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.95;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 14px 32px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
  display: inline-block;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

.btn-secondary {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-2px);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  padding: 0 20px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 0 0 15px 0;
  color: #334155;
  font-size: 1.25rem;
}

.feature-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
