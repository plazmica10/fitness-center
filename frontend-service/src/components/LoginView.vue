<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username:</label>
        <input 
          id="username" 
          v-model="username" 
          type="text" 
          required 
          placeholder="Enter username"
        />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input 
          id="password" 
          v-model="password" 
          type="password" 
          required 
          placeholder="Enter password"
        />
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
    <p class="register-link">
      Don't have an account? <router-link to="/register">Register here</router-link>
    </p>
    <div class="demo-credentials">
      <h3>Demo Credentials:</h3>
      <p>Admin: <code>admin / 123456</code></p>
      <p>Trainer: <code>mikechen / 123456</code></p>
      <p>Member: <code>alex_chen / 123456</code></p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

// Create a separate axios instance without interceptors for auth endpoints
const authClient = axios.create({ 
  baseURL: '/api',
  timeout: 10000
})

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    }
  },
  mounted() {
    // Redirect if already logged in
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    if (token && role) {
      if (role === 'admin') {
        this.$router.push('/analytics')
      } else if (role === 'trainer') {
        this.$router.push('/trainer-classes')
      } else if (role === 'member') {
        this.$router.push('/my-classes')
      }
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.loading = true

      try {
        const response = await authClient.post('/login', {
          username: this.username,
          password: this.password
        })

        const token = response.data.access_token
        localStorage.setItem('token', token)
        localStorage.setItem('username', this.username)

        // Fetch user details to get role and full name
        try {
          const userResponse = await authClient.get('/me', {
            headers: { Authorization: `Bearer ${token}` }
          })
          localStorage.setItem('role', userResponse.data.role)
          localStorage.setItem('full_name', userResponse.data.full_name || this.username)
        } catch (err) {
          console.error('Failed to fetch user details:', err)
        }

        // Trigger parent component to check auth state
        if (this.$root.checkAuthState) {
          this.$root.checkAuthState()
        }

        // Redirect based on role
        const role = localStorage.getItem('role')
        if (role === 'admin') {
          this.$router.push('/analytics')
        } else if (role === 'trainer') {
          this.$router.push('/trainer-classes')
        } else {
          this.$router.push('/my-classes')
        }
      } catch (err) {
        console.error('Login error:', err)
        this.error = err.response?.data?.detail || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #334155;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #475569;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
}

button {
  width: 100%;
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: #2563eb;
}

button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.error-message {
  color: #dc2626;
  margin-bottom: 15px;
  padding: 10px;
  background: #fee2e2;
  border-radius: 4px;
  font-size: 14px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #64748b;
}

.register-link a {
  color: #3b82f6;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

.demo-credentials {
  margin-top: 30px;
  padding: 20px;
  background: #f1f5f9;
  border-radius: 4px;
  border-left: 4px solid #3b82f6;
}

.demo-credentials h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #334155;
}

.demo-credentials p {
  margin: 5px 0;
  font-size: 13px;
  color: #475569;
}

.demo-credentials code {
  background: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
