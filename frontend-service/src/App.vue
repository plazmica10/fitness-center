<template>
  <div>
    <header>
      <div class="container"><h1>Fitness Center</h1></div>
    </header>
    <div class="container">
      <nav>
        <router-link to="/classes"><button :class="{active: $route.path==='/classes'}">Classes</button></router-link>
        <router-link to="/trainers"><button :class="{active: $route.path==='/trainers'}">Trainers</button></router-link>
        <router-link to="/rooms"><button :class="{active: $route.path==='/rooms'}">Rooms</button></router-link>
        <router-link to="/attendances"><button :class="{active: $route.path==='/attendances'}">Attendances</button></router-link>
        <router-link to="/payments"><button :class="{active: $route.path==='/payments'}">Payments</button></router-link>
        <router-link to="/analytics"><button :class="{active: $route.path==='/analytics'}">Analytics</button></router-link>
      </nav>
      <main>
        <div class="card">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
