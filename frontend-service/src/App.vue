<template>
  <div id="app">
    <header class="main-header">
      <div class="header-container">
        <router-link to="/" class="logo">
          <h1>Fitness Center</h1>
        </router-link>
        <div class="header-actions">
          <div v-if="isLoggedIn" class="user-info">
            <span class="welcome-text">Welcome, {{ username }}</span>
            <button @click="logout" class="logout-btn">Logout</button>
          </div>
          <div v-else class="auth-links">
            <router-link to="/login" class="auth-link">Login</router-link>
            <router-link to="/register" class="auth-link register">Register</router-link>
          </div>
        </div>
      </div>
    </header>
    
    <div class="main-container">
      <nav v-if="isLoggedIn && !isAuthPage" class="main-nav">
        <router-link 
          v-for="link in visibleNavLinks" 
          :key="link.path"
          :to="link.path" 
          class="nav-link" 
          :class="{active: isActive(link.path)}"
        >
          {{ link.label }}
        </router-link>
      </nav>
      
      <main class="main-content">
        <div v-if="!isAuthPage && !isLandingPage" class="content-card">
          <router-view :key="$route.fullPath" />
        </div>
        <router-view v-else :key="$route.fullPath" />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      loggedIn: false,
      currentUsername: '',
      currentFullName: '',
      userRole: ''
    }
  },
  computed: {
    isLoggedIn() {
      return this.loggedIn
    },
    username() {
      return this.currentFullName || this.currentUsername || 'User'
    },
    role() {
      return this.userRole
    },
    isAuthPage() {
      return ['/login', '/register'].includes(this.$route.path)
    },
    isLandingPage() {
      return this.$route.path === '/'
    },
    visibleNavLinks() {
      const role = this.userRole
      
      if (role === 'admin') {
        return [
          { path: '/analytics', label: 'Analytics' },
          { path: '/classes', label: 'Classes' },
          { path: '/trainers', label: 'Trainers' },
          { path: '/rooms', label: 'Rooms' },
          { path: '/attendances', label: 'Attendances' },
          { path: '/payments', label: 'Payments' }
        ]
      } else if (role === 'trainer') {
        return [
          { path: '/trainer-classes', label: 'My Classes' },
          { path: '/attendances', label: 'Attendances' }
        ]
      } else if (role === 'member') {
        return [
          { path: '/my-classes', label: 'My Classes' }
        ]
      }
      
      return []
    }
  },
  methods: {
    checkAuthState() {
      this.loggedIn = !!localStorage.getItem('token')
      this.currentUsername = localStorage.getItem('username') || ''
      this.currentFullName = localStorage.getItem('full_name') || ''
      this.userRole = localStorage.getItem('role') || ''
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('full_name')
      localStorage.removeItem('role')
      this.checkAuthState()
      this.$router.push('/')
    },
    isActive(path) {
      return this.$route.path === path || this.$route.path === path + '/'
    }
  },
  watch: {
    $route() {
      // Check auth state on route change
      this.checkAuthState()
    }
  },
  mounted() {
    // Initial auth check
    this.checkAuthState()
    
    // Listen for storage events (for multi-tab sync)
    window.addEventListener('storage', this.checkAuthState)
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.checkAuthState)
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  background: linear-gradient(90deg, #0f172a, #071032);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  text-decoration: none;
  color: white;
}

.logo h1 {
  margin: 0;
  font-weight: 600;
  font-size: 1.5rem;
}

.header-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  font-size: 14px;
  color: #cbd5e1;
}

.logout-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.1);
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.3);
}

.auth-links {
  display: flex;
  gap: 15px;
}

.auth-link {
  padding: 8px 16px;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.auth-link:hover {
  background: rgba(255,255,255,0.1);
}

.auth-link.register {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
}

.auth-link.register:hover {
  background: rgba(255,255,255,0.3);
}

.main-container {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

.main-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 14px 0;
  margin-bottom: 20px;
}

.nav-link {
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s;
  background: white;
  border: 1px solid #e2e8f0;
}

.nav-link:hover {
  background: #f8fafc;
  color: #334155;
}

.nav-link.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.main-content {
  flex: 1;
}

.content-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .main-nav {
    justify-content: center;
  }
  
  .nav-link {
    font-size: 14px;
    padding: 8px 12px;
  }
}
</style>
