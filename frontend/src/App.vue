<template>
  <div id="app">
    <CardSearch />
  </div>
</template>

<script>
import CardSearch from "./components/CardSearch.vue";

export default {
  components: {
    CardSearch,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
