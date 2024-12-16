<template>
    <div class="autocomplete-dropdown">
      <ul>
        <li v-for="card in results" :key="card.id" @click="$emit('select-card', card)">
          {{ card.name }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    name: "CardAutocomplete", // Use the multi-word name here
    props: {
      results: Array,
    },
  };
  </script>
  
  
  <style scoped>
  .autocomplete-dropdown {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-top: 10px;
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
  