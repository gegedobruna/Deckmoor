<template>
  <div>
    <h1>MTG Card Search (Autocomplete)</h1>
    <input v-model="query" @input="debouncedSearch" placeholder="Search cards..." />
    
    <!-- Autocomplete Dropdown -->
    <div v-if="results.length" class="autocomplete-dropdown">
      <ul>
        <li v-for="card in results" :key="card.id" @click="showCardDetails(card)">
          {{ card.name }}
        </li>
      </ul>
    </div>

    <!-- Card Details Section -->
    <div v-if="selectedCard" class="card-details">
      <div class="card-info">
        <div class="card-name">{{ selectedCard.name }}</div>
        <div class="card-type">{{ selectedCard.type_line }}</div>
        <div class="card-cost">{{ selectedCard.mana_cost || 'No Mana Cost' }}</div>
        <div class="card-power">
          <span v-if="selectedCard.power && selectedCard.toughness">
            Power/Toughness: {{ selectedCard.power }}/{{ selectedCard.toughness }}
          </span>
        </div>
      </div>
      <div class="card-image">
        <img :src="selectedCard.image_uris.normal" :alt="selectedCard.name" />
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      query: "",
      results: [],
      debounceTimeout: null, // For debouncing
      selectedCard: null, // To hold selected card's details
    };
  },
  methods: {
    // This function will be called when the user types
    debouncedSearch() {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout); // Clear the previous timeout
      }

      // Set a new timeout to make the API call after typing stops for 500ms
      this.debounceTimeout = setTimeout(() => {
        if (this.query.trim()) {
          this.searchCards(this.query); // Call the API
        } else {
          this.results = []; // Clear results if query is empty
        }
      }, 500); // Adjust debounce time as necessary (500ms here)
    },

    // Call the FastAPI backend to search cards
    async searchCards(query) {
      try {
        const response = await axios.get("http://127.0.0.1:8000/search", {
          params: { query },
        });
        console.log("API Response:", response.data);
        this.results = response.data; // Update the results
      } catch (error) {
        console.error("Error fetching cards:", error);
        this.results = [];
      }
    },

    // This function is called when a card is clicked to show its details
    showCardDetails(card) {
      this.selectedCard = card;
    },
  },
};
</script>

<style scoped>
/* Autocomplete Dropdown */
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

/* Card Details Section */
.card-details {
  margin-top: 30px;
  padding: 20px;
  border-radius: 10px;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-info div {
  background-color: #d3d3d3;
  padding: 8px 15px;
  margin: 5px;
  border-radius: 8px;
}

.card-name {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.card-type {
  font-size: 18px;
  color: #555;
}

.card-cost {
  font-size: 18px;
  color: #444;
}

.card-power {
  font-size: 18px;
  color: #444;
}

.card-image img {
  max-width: 300px;
  margin-top: 20px;
  border-radius: 5px;
  border: 1px solid #ddd;
}
</style>
