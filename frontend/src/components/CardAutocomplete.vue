<template>
  <div class="autocomplete-dropdown" v-if="results.length" @click.stop>
    <ul>
      <li v-for="card in results" :key="card.id" @click="$emit('select-card', card)">
        {{ card.name }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "CardAutocomplete", 
  props: {
      results: Array,
  },
  mounted() {
      document.addEventListener("click", this.closeDropdown);
  },
  beforeUnmount() {
      document.removeEventListener("click", this.closeDropdown);
  },
  methods: {
      closeDropdown() {
          this.$emit("select-card", null);
      }
  }
};
</script>

<style scoped>
.autocomplete-dropdown {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-top: 10px;
  position: absolute;
  background: white;
  width: 100%;
  z-index: 1000;
}
.autocomplete-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.autocomplete-dropdown li {
  padding: 10px;
  cursor: pointer;
}
.autocomplete-dropdown li:hover {
  background-color: #f0f0f0;
}
</style>
