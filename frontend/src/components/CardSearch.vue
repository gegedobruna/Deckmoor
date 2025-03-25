<template>
  <div class="card-search-container">
    <h1>MTG Card Search</h1>

    <div class="search-controls">
      <div class="search-box-wrapper">
        <div class="search-box">
          <input 
            v-model="query" 
            @input="debouncedSearch" 
            @keyup.enter="submitSearch" 
            placeholder="Search cards..." 
            class="search-input"
          />
          <button @click="submitSearch" class="search-button">
            <i class="fas fa-search"></i> Search
          </button>
        </div>
        
        <CardAutocomplete 
          v-if="results?.length > 0"
          :results="results" 
          @select-card="showCardDetails" 
        />
      </div>
      
      <button @click="showFilterPopup = true" class="filter-button">
        <i class="fas fa-filter"></i> Advanced Options
      </button>
    </div>

    <!-- Filter Popup -->
    <FilterPopup 
    v-if="showFilterPopup"
    :isOpen="showFilterPopup"
    :allSets="allSets"
    :currentFilters="activeFilters"
    @close-popup="showFilterPopup = false"
    @apply-filters="handleApplyFilters"
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
import FilterPopup from "./FilterPopup.vue"; // Changed from FilterPanel to FilterPopup
import DeckSidebar from "./DeckSidebar.vue";

export default {
  components: { 
    CardAutocomplete, 
    CardGrid, 
    CardDetailsPopup,
    FilterPopup, // Changed from FilterPanel to FilterPopup
    DeckSidebar
  },
  data() {
    return {
      showFilterPopup: false, // This was missing
      query: "",
      results: [],
      cards: [],   
      selectedCard: null,
      selectedCardForDeck: null,
      page: 1,
      hasMore: false,
      hasSearched: false,
      allSets: [],
      activeFilters: {
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        colors: [],
        // subtype: "",
        manaCost: { min: 0, max: 20 },
        power: { operator: "=", value: null },
        toughness: { operator: "=", value: null }
      },
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
      query: this.query.trim(),
      colors: this.activeFilters.colors.join(','),
      mana_min: this.activeFilters.manaCost?.min || 0,
      mana_max: this.activeFilters.manaCost?.max || 20,
    };
    
    // Apply all filters if they exist
    if (this.activeFilters) {
      // Set filters
      if (this.activeFilters.sets.length > 0) {
        params.sets = this.activeFilters.sets.join(',');
      }
      
      // Rarity filters
      if (this.activeFilters.rarities.length > 0) {
        params.rarities = this.activeFilters.rarities.join(',');
      }
      
      // Type filters
      if (this.activeFilters.types.length > 0) {
        params.types = this.activeFilters.types.join(',');
      }
      
      // Supertype filters
      if (this.activeFilters.supertypes.length > 0) {
        params.supertypes = this.activeFilters.supertypes.join(',');
      }
      
      // // Subtype filter
      // if (this.activeFilters.subtype) {
      //   params.subtype = this.activeFilters.subtype;
      // }
      
      // Power filter
      if (this.activeFilters.power.value !== null) {
        params.power_value = this.activeFilters.power.value;
        params.power_operator = this.activeFilters.power.operator;
      }
      
      // Toughness filter
      if (this.activeFilters.toughness.value !== null) {
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
      this.selectedCard = card;
      this.results = [];
    },

    applyFilters(filters) {
      this.activeFilters = filters;
      this.page = 1;
      this.fetchCards(1);
    },

    handleApplyFilters(newFilters) {
      this.activeFilters = newFilters;
      this.page = 1;
      this.fetchCards(1);
    },
    
    clearFilters() {
      this.activeFilters = { 
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        colors: [],
        // subtype: "",
        manaCost: { min: 0, max: 20 },
        power: { operator: "=", value: null },
        toughness: { operator: "=", value: null }
      };
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
      console.log("Adding card to deck:", card.name);
      if (this.$refs.deckSidebar?.addCardToDeck) {
        this.$refs.deckSidebar.addCardToDeck(card);
      } else {
        console.error("DeckSidebar not available");
      }
    },
    
    onDeckSaved() {
      // Handle deck saved event if needed
    }
  }
}
</script>

<style scoped>
.card-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.search-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.search-box-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-container {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-width: 200px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
}


.search-container input {
  flex: 1;
  padding: 10px 15px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  min-width: 300px;
}

.search-button {
  background-color: #4299e1;
  color: white;

}

.search-button, .filter-button {
  padding: 10px;
  height: 40px;
  border: none;
  border-radius: 10%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.search-button:hover {
  background-color: #3182ce;
  transform: scale(1.05);
}


.filter-button {
  padding: 8px 12px;
    background-color: #f7fafc;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    margin-top: 10px;
}

.filter-button:hover {
  background-color: #ebf8ff;
  border-color: #bee3f8;
  color: #3182ce;
  transform: scale(1.05)
}

.autocomplete-container {
  position: absolute;
  width: calc(100% - 48px); /* Accounts for search button */
  max-width: 552px; /* Matches search box width minus button */
  z-index: 10;
  top: 100%;
  left: 0;
  margin-top: 4px;
}

.results-area {
  flex: 1;
  padding: 0 20px;
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