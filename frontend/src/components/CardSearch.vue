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

    <!-- Filter Toggle Button -->
    <button @click="showFilters = !showFilters" class="filter-toggle">
      {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
    </button>

    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Filters Panel -->
      <FilterPanel 
        v-if="showFilters" 
        :allSets="allSets"
        @filters-changed="applyFilters"
      />

      <!-- Results Area -->
      <div class="results-area">
        <!-- Card Grid -->
        <CardGrid 
  v-if="cards && cards.length > 0" 
  :cards="cards" 
  @select-card="showCardDetails"
  @add-to-deck="addCardToDeck" 
/>
        <div v-else-if="hasSearched" class="no-results">
          No cards found matching your criteria
        </div>

        <!-- Pagination Controls -->
        <div v-if="(hasMore || page > 1) && cards.length" class="pagination-controls">
          <button @click="fetchCards(page - 1)" :disabled="page === 1">Previous</button>
          <span>Page {{ page }}</span>
          <button @click="fetchCards(page + 1)" :disabled="!hasMore">Next</button>
        </div>
      </div>

      <!-- Deck Sidebar - for deck management -->
      <DeckSidebar 
        ref="deckSidebar"
        :selectedCard="selectedCard"
        @reset-selected-card="selectedCard = null"
        @view-card="showCardDetails"
        @deck-saved="onDeckSaved"
      />
    </div>

    <!-- Card Details Pop-Up -->
    <CardDetailsPopup
    v-if="selectedCard"
    :card="selectedCard"
    @close="selectedCard = null"
    @add-to-deck="addCardToDeck"
  />
  </div>
</template>

<script>
import axios from "axios";
import debounce from "lodash/debounce";
import CardAutocomplete from "./CardAutocomplete.vue";
import CardGrid from "./CardGrid.vue";
import CardDetailsPopup from "./CardDetailsPopup.vue";
import FilterPanel from "./FilterPanel.vue";
import DeckSidebar from "./DeckSidebar.vue";

export default {
  components: { 
    CardAutocomplete, 
    CardGrid, 
    CardDetailsPopup,
    FilterPanel,
    DeckSidebar
  },
  data() {
    return {
      query: "",
      results: [],
      cards: [],   
      selectedCard: null,
      selectedCardForDeck: null, // track card selected for adding to deck
      page: 1,
      hasMore: false,
      showFilters: false,
      hasSearched: false,
      allSets: [],
      activeFilters: null
    };
  },
  created() {
    this.fetchSets();
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
      this.hasSearched = true;
      this.page = 1;
      this.fetchCards(1);
    },
    
    async fetchCards(newPage = 1) {
      try {
        const params = { 
          page: newPage,
          query: this.query.trim()
        };
        // Apply filters
        if (this.activeFilters) {
          // Mana cost
          if (this.activeFilters.manaCost.min > 0 || this.activeFilters.manaCost.max < 16) {
            params.mana_min = this.activeFilters.manaCost.min;
            params.mana_max = this.activeFilters.manaCost.max;
          }
          // Colors
          if (this.activeFilters.colors.length > 0) {
            params.colors = this.activeFilters.colors.join(',');
          }
          // Types
          if (this.activeFilters.types.length > 0) {
            params.types = this.activeFilters.types.join(',');
          }
          // Rarities
          if (this.activeFilters.rarities.length > 0) {
            params.rarities = this.activeFilters.rarities.join(',');
          }
          // Sets
          if (this.activeFilters.sets.length > 0) {
            params.sets = this.activeFilters.sets.join(',');
          }
          // Power
          if (this.activeFilters.power.value !== 0) {
            params.power_value = this.activeFilters.power.value;
            params.power_operator = this.activeFilters.power.operator;
          }
          // Toughness
          if (this.activeFilters.toughness.value !== 0) {
            params.toughness_value = this.activeFilters.toughness.value;
            params.toughness_operator = this.activeFilters.toughness.operator;
          }
        }
        const response = await axios.get("http://127.0.0.1:8000/search", { params });
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
  this.selectedCard = card; // Just show details, don't add to deck
  this.results = [];
},

    closeCardDetails() {
      // IMPORTANT: Removed the line that assigned selectedCardForDeck to selectedCard
      this.selectedCard = null;
    },
    
    applyFilters(filters) {
      this.activeFilters = filters;
      this.page = 1;
      this.fetchCards(1);
    },
    
    async fetchSets() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/sets");
        this.allSets = response.data.sets || [];
      } catch (error) {
        console.error("Error fetching sets:", error);
        this.allSets = [];
      }
    },
  addCardToDeck(card) {
  console.log("Adding card to deck:", card.name); // Debug
  if (this.$refs.deckSidebar?.addCardToDeck) {
    this.$refs.deckSidebar.addCardToDeck(card);
  } else {
    console.error("DeckSidebar not available");
  }
},

  },
};
</script>

<style scoped>
.search-container {
  position: relative; 
  width: 100%;
  max-width: 600px; 
  margin: 0 auto 20px; 
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

.filter-toggle {
  display: block;
  margin: 0 auto 20px;
  padding: 8px 16px;
  background-color: #4682B4;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.results-area {
  flex: 1;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  align-items: center;
}

.pagination-controls button {
  margin: 0 10px;
  padding: 8px 16px;
  background-color: #4682B4;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.pagination-controls button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination-controls span {
  font-weight: bold;
}

.no-results {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
  font-size: 18px;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
}
</style>