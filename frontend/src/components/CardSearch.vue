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
        v-if="results?.length > 0"
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

    <!-- Pagination Controls -->
    <div v-if="hasMore || page > 1" class="pagination-controls">
      <button @click="fetchCards(page - 1)" :disabled="page === 1">Previous</button>
      <span>Page {{ page }}</span>
      <button @click="fetchCards(page + 1)" :disabled="!hasMore">Next</button>
    </div>

    <!-- Card Details Pop-Up -->
    <CardDetailsPopup 
      v-if="selectedCard" 
      :card="selectedCard" 
      @close="selectedCard = null" 
    />
  </div>
</template>

<script>
import axios from "axios";
import debounce from "lodash/debounce";
import CardAutocomplete from "./CardAutocomplete.vue";
import CardGrid from "./CardGrid.vue";
import CardDetailsPopup from "./CardDetailsPopup.vue";

export default {
  components: { CardAutocomplete, CardGrid, CardDetailsPopup },
  data() {
    return {
      query: "",
      results: [],
      cards: [],   
      selectedCard: null,
      page: 1,
      hasMore: false,
    };
  },
  methods: {
    debouncedSearch: debounce(function () {
      if (this.query.trim()) {
        this.fetchAutocomplete(this.query);
      } else {
        this.results = [];
      }
    }, 300),
    async fetchAutocomplete(query) {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/search?query=${query}&page=1`);
    this.results = response.data.cards?.slice(0, 10) || [];
  } catch (error) {
    console.error("Error fetching autocomplete results:", error);
    this.results = [];
  }
},
    async submitSearch() {
      if (!this.query.trim()) return;
      this.page = 1;
      this.fetchCards(1);
    },
    async fetchCards(newPage = 1) {
  if (!this.query.trim()) return;
  try {
    const response = await axios.get("http://127.0.0.1:8000/search", {
      params: { query: this.query, page: newPage },
    });
    this.cards = response.data.cards || [];
    this.hasMore = response.data.has_more || false;
    this.page = newPage;
  } catch (error) {
    console.error("Error fetching cards:", error);
    this.cards = [];
    this.hasMore = false;
  }
},
    showCardDetails(card) {
      this.selectedCard = card;
      this.results = [];
    },
  },
};
</script>

<style scoped>
.search-container {
  position: relative; 
  width: 100%;
  max-width: 600px; 
  margin: 0 auto; 
}

.search-container input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  margin: 0;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%; 
  left: 0;
  width: 100%; 
  z-index: 1000;
  background-color: white;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.pagination-controls {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

button {
  margin: 0 10px;
}
</style>
