<template>
  <div>
    <h1>MTG Card Search</h1>

    <!-- Search bar and dropdown container -->
    <div class="search-container">
      <input 
        v-model="query" 
        @input="debouncedSearch" 
        @keyup.enter="submitSearch" 
        placeholder="Search cards..."
      />

      <!-- Autocomplete component -->
      <CardAutocomplete 
        v-if="results.length" 
        :results="results" 
        @select-card="showCardDetails" 
      />
    </div>

    <!-- Card Grid -->
    <CardGrid 
      v-if="cards.length" 
      :cards="cards" 
      @select-card="showCardDetails" 
    />

    <!-- Card Details Pop-Up -->
    <CardDetailsPopup 
      v-if="selectedCard" 
      :card="selectedCard" 
      @close="selectedCard = null" 
    />
  </div>
</template>

<script>
import CardAutocomplete from "./CardAutocomplete.vue";
import CardGrid from "./CardGrid.vue";
import CardDetailsPopup from "./CardDetailsPopup.vue";

export default {
  components: { CardAutocomplete, CardGrid, CardDetailsPopup },
  data() {
    return {
      query: "",
      results: [], // Autocomplete results
      cards: [],   // Full search results
      selectedCard: null,
      debounceTimeout: null,
    };
  },
  methods: {
    debouncedSearch() {
      if (this.debounceTimeout) clearTimeout(this.debounceTimeout);

      this.debounceTimeout = setTimeout(() => {
        if (this.query.trim()) this.fetchAutocomplete(this.query);
        else this.results = [];
      }, 300);
    },
    async fetchAutocomplete(query) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/search?query=${query}`);
        const data = await response.json();
        this.results = data.slice(0, 10); // Show up to 10 suggestions
      } catch (error) {
        console.error("Error fetching autocomplete results:", error);
        this.results = [];
      }
    },
    async submitSearch() {
      if (!this.query.trim()) return;

      try {
        const response = await fetch(`http://127.0.0.1:8000/search?query=${this.query}`);
        this.cards = await response.json();
        this.results = []; // Clear autocomplete dropdown
      } catch (error) {
        console.error("Error fetching cards:", error);
      }
    },
    showCardDetails(card) {
      this.selectedCard = card;
      this.results = []; // Close the autocomplete dropdown
    },
  },
};
</script>

<style scoped>
/* Positioning container for the search bar and dropdown */
.search-container {
  position: relative; /* Position relative for dropdown */
  width: 100%;
  max-width: 600px; /* Limit width for a clean look */
  margin: 0 auto; /* Center horizontally */
}

/* Style the input field */
.search-container input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  margin: 0;
}

/* Add a subtle shadow to the dropdown for visibility */
.autocomplete-dropdown {
  position: absolute;
  top: 100%; /* Dropdown directly below input */
  left: 0;
  width: 100%; /* Match input field width */
  z-index: 1000; /* Ensure it appears above other elements */
  background-color: white;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
