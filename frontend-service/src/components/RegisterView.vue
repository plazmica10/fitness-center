<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username:</label>
        <input 
          id="username" 
          v-model="username" 
          type="text" 
          required 
          placeholder="Choose a username"
        />
      </div>
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          id="email" 
          v-model="email" 
          type="email" 
          required 
          placeholder="your@email.com"
        />
      </div>
      <div class="form-group">
        <label for="fullName">Full Name:</label>
        <input 
          id="fullName" 
          v-model="fullName" 
          type="text" 
          required 
          placeholder="Your full name"
        />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input 
          id="password" 
          v-model="password" 
          type="password" 
          required 
          minlength="6"
          placeholder="At least 6 characters"
        />
      </div>
      <div class="form-group">
        <label for="role">Role:</label>
        <select id="role" v-model="role" required>
          <option value="member">Member</option>
          <option value="trainer">Trainer</option>
        </select>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    <p class="login-link">
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
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
  name: 'RegisterView',
  data() {
    return {
      username: '',
      email: '',
      fullName: '',
      password: '',
      role: 'member',
      error: '',
      success: '',
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.success = ''
      this.loading = true

      try {
        await authClient.post('/register', {
          username: this.username,
          email: this.email,
          full_name: this.fullName,
          password: this.password,
          role: this.role
        })

        this.success = 'Registration successful! Redirecting to login...'
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (err) {
        console.error('Registration error:', err)
        this.error = err.response?.data?.detail || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
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

input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus, select:focus {
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

.success-message {
  color: #059669;
  margin-bottom: 15px;
  padding: 10px;
  background: #d1fae5;
  border-radius: 4px;
  font-size: 14px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #64748b;
}

.login-link a {
  color: #3b82f6;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
