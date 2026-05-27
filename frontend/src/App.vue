<template>
  <NavBar />
  <main class="main-content">
    <router-view />
  </main>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<style>
.main-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
}
</style>