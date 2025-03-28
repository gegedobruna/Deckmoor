<template>
  <div class="deck-sidebar">
    <div class="connection-status" :class="firebaseStatus">
      <span class="status-icon"></span>
      {{ statusMessage }}
      <span v-if="lastSyncTime" class="sync-time">({{ formatTime(lastSyncTime) }})</span>
    </div>
    <div v-if="!activeDeck" class="deck-list">
      <h2 class="sidebar-title">Your Decks</h2>
      <div v-for="deck in decks" :key="deck.id" class="deck-item" @click="loadDeck(deck)">
        <span class="deck-name">{{ deck.name }}</span>
        <span class="deck-colors" v-html="formatColors(deck.colors)"></span>
        <span v-if="getDeckCardCount(deck) > 100" class="deck-warning">!</span>
        <button class="delete-deck-btn" @click.stop="promptDeleteDeck(deck)">
          🗑️
        </button>
      </div>

      <button class="create-deck-btn" @click="showCreateDeckModal = true">
        <span class="btn-icon">+</span> Create a Deck
      </button>
      <button class="import-deck-btn" @click="showImportModal = true">
        <span class="btn-icon">📥</span> Import Deck
      </button>
    </div>
    
    
    <div v-else class="active-deck">
      <div class="deck-header">
        <div class="deck-header-top">
          <button class="back-btn" @click="backToDecks">
            <span class="back-icon">←</span> Back to Decks
          </button>
          <button class="delete-deck-btn" @click="promptDeleteDeck(activeDeck)">
              🗑️ Delete
            </button>
        </div>
        
        <div class="deck-title-section">
          <div class="title-wrapper">
            <h2 class="deck-title">{{ activeDeck.name }}</h2>
            <div class="deck-meta-row">
              <div class="deck-meta">
                <div class="deck-colors" v-html="formatColors(activeDeck.colors)"> </div>
                <span :class="['card-count', {'over-limit': totalCards > 100}]">
                  {{ totalCards }}/100 </span>
                <div class="deck-header-actions">
                <button class="stats-btn" @click="showDeckStats">
                  <span class="stats-icon">📊</span> Stats
                </button>
              </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      
      <div v-if="activeDeck.commander" class="commander-section">
        <h3 class="section-title">Commander</h3>
        <div class="commander-card" @click="viewCardDetails(activeDeck.commander)">
          <img :src="activeDeck.commander.image_uris?.small || activeDeck.commander.card_faces?.[0]?.image_uris?.small" :alt="activeDeck.commander.name">
          <span class="commander-name">{{ activeDeck.commander.name }}</span>
        </div>
      </div>
      
      <div class="deck-cards">
        <h3 class="section-title">Cards</h3>
        <div 
          v-for="card in sortedCards" 
          :key="card.id" 
          class="deck-card"
          :class="{ 
            'invalid-color': !isColorIdentityValid(card),
            'invalid-format': !isLegalInCommander(card) 
          }"
          :style="getCardBorderStyle(card)"
          :data-invalid-reason="
            !isColorIdentityValid(card) ? 'Wrong colors for commander' : 
            !isLegalInCommander(card) ? 'Banned/unserious set' : ''
          "
          @click="$emit('view-card', card)"
        >
          <div class="card-info">
            <div class="card-header">
              <span class="card-name">
                {{ card.name }}
              </span>
              <span class="card-count" :class="{'count-changed': card.count > 1}">
                x{{ card.count || 1 }}
              </span>
            </div>
          </div>
          <div class="card-actions">
            <button 
              v-if="canHaveMultipleCopies(card)" 
              class="add-btn" 
              @click.stop="addOneCard(card, $event)" 
            >
              +
            </button>
            <button 
              class="remove-btn" 
              @click.stop="removeCard(card)"
            >
              −
            </button>
          </div>
        </div>
      </div>
      
      <div class="deck-actions">
        <button class="save-deck-btn" @click="saveDeck">
          Save Deck
        </button>
      </div>
    </div>
    
    <!-- Create Deck Modal -->
    <div v-if="showCreateDeckModal" class="modal-overlay" @click.self="showCreateDeckModal = false">
      <div class="modal-content">
        <h2 class="modal-title">Create New Deck</h2>
        <div class="form-group">
          <label for="deckName">Deck Name:</label>
          <input id="deckName" v-model="newDeckName" placeholder="Enter deck name">
        </div>
        <div class="form-group">
          <button class="search-commander-btn" @click="searchCommander">Search for Commander</button>
        </div>
        <div v-if="selectedCommander" class="selected-commander">
          <h3 class="modal-subtitle">Selected Commander:</h3>
          <div class="commander-preview">
            <img :src="selectedCommander.image_uris?.small || selectedCommander.card_faces?.[0]?.image_uris?.small" :alt="selectedCommander.name">
            <span class="selected-card-name">{{ selectedCommander.name }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCreateDeckModal = false">Cancel</button>
          <button class="confirm-btn" :disabled="!newDeckName || !selectedCommander" @click="createDeck">Create</button>
        </div>
      </div>
    </div>
    
    <!-- Commander Search Modal -->
    <div v-if="showCommanderSearch" class="modal-overlay" @click.self="showCommanderSearch = false">
      <div class="modal-content commander-search">
        <h2 class="modal-title">Select Commander</h2>
        <div class="search-box">
          <input v-model="commanderQuery" @input="searchCommanderCards" placeholder="Search for legendary creatures...">
        </div>
        <div class="commander-results">
          <div v-for="card in commanderResults" :key="card.id" class="commander-option" @click="selectCommander(card)">
            <img :src="card.image_uris?.small || card.card_faces?.[0]?.image_uris?.small" :alt="card.name">
            <span class="search-result-name">{{ card.name }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showCommanderSearch = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Add Multiple Lands Modal -->
    <div v-if="showAddLandsModal" class="modal-overlay" @click.self="showAddLandsModal = false">
      <div class="modal-content">
        <h2 class="modal-title">Add Multiple Lands</h2>
        <div class="form-group">
          <label for="landCount">How many copies?</label>
          <input id="landCount" v-model.number="landCount" type="number" min="1" max="99">
        </div>
        <div class="selected-land">
          <h3 class="modal-subtitle">Selected Land:</h3>
          <div class="land-preview">
            <img :src="selectedLand.image_uris?.small || selectedLand.card_faces?.[0]?.image_uris?.small" :alt="selectedLand.name">
            <span class="selected-card-name">{{ selectedLand.name }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showAddLandsModal = false">Cancel</button>
          <button class="confirm-btn" @click="addMultipleLands">Add</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-overlay" @click.self="showDeleteConfirmation = false">
      <div class="modal-content">
        <h2 class="modal-title">Delete Deck</h2>
        <p>Are you sure you want to delete "{{ deckToDelete?.name }}"? This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteConfirmation = false">Cancel</button>
          <button class="confirm-btn delete-btn" @click="confirmDeleteDeck">Delete</button>
        </div>
      </div>
    </div>
    <ImportPopup 
      v-if="showImportModal"
      :isOpen="showImportModal"
      @close="showImportModal = false"
      @import="handleDeckImport"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { saveDeck, loadDecks, deleteDeck } from '../services/deckService';
import ImportPopup from './ImportPopup.vue'; 
export default {
  name: 'DeckSidebar',
  components: { ImportPopup },
  props: {
    selectedCard: Object,
  },
  data() {
    return {
      decks: [],
      activeDeck: null,
      showCreateDeckModal: false,
      showCommanderSearch: false,
      showAddLandsModal: false,
      showDeleteConfirmation: false,
      newDeckName: '',
      selectedCommander: null,
      commanderQuery: '',
      commanderResults: [],
      selectedLand: null,
      landCount: 1,
      deckToDelete: null,
      firebaseStatus: 'checking', // 'connected', 'disconnected', 'error'
      lastSyncTime: null,
      connectionInterval: null,
      showImportModal: false
    };
  },
  computed: {
    sortedCards() {
      if (!this.activeDeck) return [];
      return this.activeDeck.cards
        .slice()
        .sort((a, b) => (a.cmc || 0) - (b.cmc || 0));
    },
    totalCards() {
      if (!this.activeDeck) return 0;
      return this.activeDeck.cards.reduce((total, card) => total + (card.count || 1), 0);
    },
    statusMessage() {
      return {
        'checking': 'Checking connection...',
        'connected': 'Connected to Cloud',
        'disconnected': 'Offline (using local storage)',
        'error': 'Connection error'
      }[this.firebaseStatus];
    },
  deckCardCounts() {
    return this.decks.reduce((acc, deck) => {
      acc[deck.id] = deck.cards.reduce((total, card) => total + (card.count || 1), 0);
      return acc;
    }, {});
  }
},

methods: {
    async checkConnection() {
      try {
        const startTime = Date.now();
        await loadDecks(); // Simple test query
        this.firebaseStatus = 'connected';
        this.lastSyncTime = new Date();
        console.log(`Firebase connection OK (${Date.now() - startTime}ms)`);
      } catch (error) {
        this.firebaseStatus = 'disconnected';
        console.error('Firebase connection failed:', error);
      }
    },

    formatTime(date) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },

    async checkDataSource() {
      try {
        console.group('Data Source Debugging');
        
        // Check Firebase connection
        console.log('Testing Firebase connection...');
        const firebaseDecks = await loadDecks();
        console.log('Firebase response:', firebaseDecks);
        
        // Check local storage
        const localDecks = localStorage.getItem('mtg-decks');
        console.log('Local storage contents:', localDecks ? JSON.parse(localDecks) : 'Empty');
        
        // Check current component state
        console.log('Component decks state:', this.decks);
        
        console.groupEnd();
        
        // Show summary to user
        if (firebaseDecks && firebaseDecks.length > 0) {
          alert(`Using Firebase (${firebaseDecks.length} decks found)`);
        } else if (localDecks) {
          alert('Using local storage (Firebase not available)');
        } else {
          alert('No decks found in either Firebase or local storage');
        }
        
        return firebaseDecks ? 'firebase' : 'local';
      } catch (error) {
        console.error('Debug check failed:', error);
        alert('Debug check failed - check console for details');
        return 'error';
      }
    },

    promptDeleteDeck(deck) {
      this.deckToDelete = deck;
      this.showDeleteConfirmation = true;
    },

    async confirmDeleteDeck() {
      if (!this.deckToDelete) return;
      
      try {
        await deleteDeck(this.deckToDelete.id);
        const index = this.decks.findIndex(d => d.id === this.deckToDelete.id);
        if (index !== -1) {
          this.decks.splice(index, 1);
          localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
          
          if (this.activeDeck && this.activeDeck.id === this.deckToDelete.id) {
            this.activeDeck = null;
          }
        }
      } catch (error) {
        console.error('Error deleting deck:', error);
        // Fallback to local storage if Firebase fails
        const index = this.decks.findIndex(d => d.id === this.deckToDelete.id);
        if (index !== -1) {
          this.decks.splice(index, 1);
          localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
          
          if (this.activeDeck && this.activeDeck.id === this.deckToDelete.id) {
            this.activeDeck = null;
          }
        }
      }
      
      this.showDeleteConfirmation = false;
      this.deckToDelete = null;
    },

    async handleDeckImport(deckData) {
      const newDeck = {
        id: Date.now().toString(),
        name: deckData.name,
        commander: deckData.commander,
        colors: deckData.colors,
        cards: deckData.cards,
        created: deckData.created
      };
      
      try {
        // Save to Firebase
        await saveDeck(newDeck);
        // Add to local state
        this.decks.push(newDeck);
        // Update localStorage as backup
        localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
        
        this.showImportModal = false;
        this.loadDeck(newDeck);
      } catch (error) {
        console.error('Error importing deck:', error);
        // Fallback to local storage
        this.decks.push(newDeck);
        localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
        
        this.showImportModal = false;
        this.loadDeck(newDeck);
      }
    },

    getCardBorderStyle(card) {
      const colors = card.color_identity || [];
      if (colors.length === 0) return 'background: rgba(200, 200, 200, 0.1)';
      
      if (colors.length === 1) {
        const colorMap = {
          'W': 'rgba(248, 231, 185, 0.3)',
          'U': 'rgba(179, 206, 234, 0.3)',
          'B': 'rgba(136, 135, 135, 0.3)',
          'R': 'rgba(235, 159, 130, 0.3)',
          'G': 'rgba(196, 211, 202, 0.3)'
        };
        return `background: linear-gradient(to right, ${colorMap[colors[0]]}, transparent)`;
      }
      
      const gradientStops = colors.map((color, index) => {
        const colorMap = {
          'W': 'rgba(248, 231, 185, 0.3)',
          'U': 'rgba(179, 206, 234, 0.3)',
          'B': 'rgba(135, 135, 135, 0.3)',
          'R': 'rgba(235, 159, 130, 0.3)',
          'G': 'rgba(196, 211, 202, 0.3)'
        };
        const position = (index / colors.length) * 100;
        return `${colorMap[color]} ${position}%`;
      }).join(', ');
      
      return `background: linear-gradient(135deg, ${gradientStops}, transparent 90%)`;
    },

    canHaveMultipleCopies(card) {
      const isBasicLand = /basic (snow )?land/i.test(card.type_line);
      const allowsMultiples = card.oracle_text?.toLowerCase()
        .includes("a deck can have any number of cards named");
      return isBasicLand || allowsMultiples;
    },

    isColorIdentityValid(card) {
      if (!this.activeDeck?.commander) return true;
      
      const commanderColors = this.activeDeck.commander.color_identity || [];
      const cardColors = card.color_identity || [];

      if (cardColors.length === 0 && card.type_line?.toLowerCase().includes("land")) {
        return true;
      }

      return cardColors.every(color => commanderColors.includes(color));
    },

    isLegalInCommander(card) {
      if (card.legalities?.commander === "banned") return false;

      const unseriousSets = ["unf", "ugl", "unh", "ust", "und"];
      if (unseriousSets.includes(card.set?.toLowerCase())) {
        return false;
      }

      if (card.border_color === "silver" || card.frame_effects?.includes("acorn")) {
        return false;
      }

      return true;
    },

    formatColors(colors) {
      if (!colors || colors.length === 0) return '<span class="mana small sc"></span>';
      return colors
        .map(color => `<span class="mana small s${color.toLowerCase()}"></span>`)
        .join(' ');
    },

    formatManaCost(manaCost) {
      if (!manaCost) return '';
      return manaCost.replace(/\{([^}]+)\}/g, (match, symbol) => {
        let cssClass = symbol.toLowerCase();
        
        if (cssClass === 't' || cssClass === 'tap') {
          cssClass = 't';
        }
        if (cssClass === 'q' || cssClass === 'untap') {
          cssClass = 'q';
        }
        if (cssClass.includes('/')) {
          cssClass = cssClass.replace('/', '');
        }
        if (/^\d+$/.test(cssClass)) {
          cssClass = cssClass.padStart(2, '0').slice(-2);
        }
        
        return `<span class="mana small s${cssClass}"></span>`;
      });
    },
    
    loadDeck(deck) {
      this.activeDeck = JSON.parse(JSON.stringify(deck));
    },

    backToDecks() {
      this.activeDeck = null;
    },

    viewCardDetails(card) {
      this.$emit('view-card', card);
    },

    addCardToDeck(card) {
      if (!this.activeDeck) {
        alert("Please select a deck first!");
        return false;
      }
      if (!this.isColorIdentityValid(card)) {
        alert(`❌ This card (${card.name}) doesn't match your commander's color identity!`);
        return false;
      }

      if (!this.isLegalInCommander(card)) {
        const confirmAdd = confirm(
          `⚠️ "${card.name}" is not legal in Commander (banned/unserious set). Add anyway?`
        );
        if (!confirmAdd) return false;
      }

      const existingIndex = this.activeDeck.cards.findIndex(c => c.id === card.id);
      
      if (existingIndex >= 0) {
        if (this.canHaveMultipleCopies(card)) {
          if (!this.activeDeck.cards[existingIndex].count) {
            this.activeDeck.cards[existingIndex].count = 2;
          } else {
            this.activeDeck.cards[existingIndex].count++;
          }
        } else {
          alert("This non-land card is already in your deck (max 1 copy).");
        }
      } else {
        const newCard = JSON.parse(JSON.stringify(card));
        this.activeDeck.cards.push(newCard);
      }
      this.$forceUpdate(); 
    },

    addOneCard(card, event) {
      const index = this.activeDeck.cards.findIndex(c => c.id === card.id);
      if (index !== -1 && this.canHaveMultipleCopies(card)) {
        if (!this.activeDeck.cards[index].count) {
          this.activeDeck.cards[index].count = 2;
        } else {
          this.activeDeck.cards[index].count++;
        }
        if (event) {
          const cardElement = event.target.closest('.deck-card');
          if (cardElement) {
            cardElement.classList.add('card-added');
            setTimeout(() => cardElement.classList.remove('card-added'), 300);
          }
        }
      }
    },

    addMultipleLands() {
      if (this.selectedLand && this.landCount > 0) {
        const index = this.activeDeck.cards.findIndex(c => c.id === this.selectedLand.id);
        if (index !== -1) {
          if (!this.activeDeck.cards[index].count) {
            this.activeDeck.cards[index].count = this.landCount;
          } else {
            this.activeDeck.cards[index].count += this.landCount - 1;
          }
        } else {
          const landClone = JSON.parse(JSON.stringify(this.selectedLand));
          landClone.count = this.landCount;
          this.activeDeck.cards.push(landClone);
        }
        this.showAddLandsModal = false;
        this.selectedLand = null;
        this.landCount = 1;
      }
    },

    removeCard(card) {
      const index = this.activeDeck.cards.findIndex(c => c.id === card.id);
      if (index !== -1) {
        if (card.count && card.count > 1) {
          this.activeDeck.cards[index].count--;
        } else {
          this.activeDeck.cards.splice(index, 1);
        }
      }
    },

    searchCommander() {
      this.showCommanderSearch = true;
      this.searchCommanderCards();
    },

    async searchCommanderCards() {
      try {
        const params = this.commanderQuery.length < 2 
          ? { q: 'type:legendary type:creature', order: 'edhrec' } 
          : { q: `${this.commanderQuery} type:legendary type:creature`, order: 'name' };
        
        const response = await axios.get('https://api.scryfall.com/cards/search', { params });
        this.commanderResults = response.data.data.slice(0, 20);
      } catch (error) {
        console.error('Error searching commanders:', error);
        this.commanderResults = [];
      }
    },

    selectCommander(card) {
      this.selectedCommander = card;
      this.showCommanderSearch = false;
    },

    async createDeck() {
      if (this.newDeckName && this.selectedCommander) {
        const newDeck = {
          id: Date.now().toString(),
          name: this.newDeckName,
          commander: this.selectedCommander,
          colors: this.selectedCommander.color_identity || [],
          cards: [this.selectedCommander],
          created: new Date().toISOString()
        };
        
        try {
          // Save to Firebase
          await saveDeck(newDeck);
          // Add to local state
          this.decks.push(newDeck);
          // Update localStorage as backup
          localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
          
          this.newDeckName = '';
          this.selectedCommander = null;
          this.showCreateDeckModal = false;
          this.loadDeck(newDeck);
        } catch (error) {
          console.error('Error saving deck:', error);
          // Fallback to local storage
          this.decks.push(newDeck);
          localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
          
          this.newDeckName = '';
          this.selectedCommander = null;
          this.showCreateDeckModal = false;
          this.loadDeck(newDeck);
        }
      }
    },

    async saveDeck() {
      const index = this.decks.findIndex(deck => deck.id === this.activeDeck.id);
      if (index !== -1) {
        try {
          this.firebaseStatus = 'checking';
          await saveDeck(this.activeDeck);
          this.decks[index] = JSON.parse(JSON.stringify(this.activeDeck));
          this.firebaseStatus = 'connected';
          this.lastSyncTime = new Date();
        } catch (error) {
          this.firebaseStatus = 'disconnected';
          localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
        }
      }
    },

    async loadDecksFromStorage() {
      try {
        this.firebaseStatus = 'checking';
        const firebaseDecks = await loadDecks();
        if (firebaseDecks && firebaseDecks.length > 0) {
          this.decks = firebaseDecks;
          this.firebaseStatus = 'connected';
          this.lastSyncTime = new Date();
        } else {
          const storedDecks = localStorage.getItem('mtg-decks');
          if (storedDecks) {
            this.decks = JSON.parse(storedDecks);
            this.firebaseStatus = 'disconnected';
          }
        }
      } catch (error) {
        this.firebaseStatus = 'error';
        const storedDecks = localStorage.getItem('mtg-decks');
        if (storedDecks) this.decks = JSON.parse(storedDecks);
      }
    },

    showDeckStats() {
      // Deck stats functionality
    },

    getDeckCardCount(deck) {
      return this.deckCardCounts[deck.id] || deck.cards.reduce((total, card) => total + (card.count || 1), 0);
    },
  },
  mounted() {
    this.loadDecksFromStorage();
    this.connectionInterval = setInterval(this.checkConnection, 30000); // Check every 30 seconds
  },
  beforeUnmount() {
    clearInterval(this.connectionInterval);
  }
};
</script>


<style>
@import '../assets/mana-master/css/mana-cost.css';
.ms {
  margin-right: 2px;
}

/* Custom sizing for DeckSidebar */
.deck-sidebar .mana {
  vertical-align: middle;
  margin: 0 2px;
}

/* Larger size for color identity symbols */
.deck-sidebar .deck-colors .mana {
  width: 1.4em !important;
  height: 1.4em !important;
  background-size: auto 700% !important;
}

/* Larger size for mana costs in card text */
.deck-sidebar .mana-symbols .mana {
  width: 1em !important;
  height: 1em !important;
  background-size: auto 700% !important;
}

/* Commander section symbols */
.deck-sidebar .commander-section .mana {
  width: 1.1em !important;
  height: 1.1em !important;
}

/* Modal symbols */
.deck-sidebar .modal-content .mana {
  width: 1.4em !important;
  height: 1.4em !important;
}
</style>

<style scoped>
.deck-sidebar {
  width: 320px;
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  background-color: white;
  border-left: 1px solid #e2e8f0;
  overflow-y: auto;
  padding: 16px;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #2d3748;
}

.sidebar-title, .section-title, .modal-title, .modal-subtitle {
  font-weight: 600;
  color: #2d3748;
  letter-spacing: -0.5px;
}

.sidebar-title {
  margin-top: 0;
  padding-bottom: 14px;
  border-bottom: 2px solid #4299e1;
  font-size: 1.5rem;
}

.section-title {
  font-size: 1.2rem;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e2e8f0;
}

.deck-list h2 {
  margin-top: 0;
}

.deck-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.deck-name {
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}

.deck-item:hover {
  background-color: #f7fafc;
  border-color: #4299e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.delete-deck-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #e53e3e;
  font-size: 1.1rem;
  padding: 4px 8px;
  margin-left: 8px;
  transition: all 0.2s ease;
  z-index: 2;
}

.delete-deck-btn:hover {
  transform: scale(1.2);
  color: #c53030;
}

.create-deck-btn {
  width: 100%;
  padding: 12px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  margin-top: 16px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.create-deck-btn:hover {
  background-color: #3182ce;
}

.import-deck-btn {
  width: 100%;
  padding: 12px;
  background-color: #38a169;
  color: white;
  border: none;
  border-radius: 8px;
  margin-top: 10px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.import-deck-btn:hover {
  background-color: #2f855a;
}

.deck-warning {
  display: inline-block;
  width: 18px;
  height: 18px;
  background-color: #e53e3e;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 18px;
  font-weight: bold;
  margin-right: 8px;
  font-size: 12px;
}

.btn-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.deck-header {
  margin-bottom: 20px;
}

.deck-header-top {
  margin-bottom: 12px;
  display: flex;
    gap: 82px;
}

.deck-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.title-wrapper {
  flex: 1;
  min-width: 0;
}

.deck-title {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-bottom: 8px;
  border-bottom: 2px solid #4299e1;
}

.deck-meta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}


.deck-colors {
  display: flex;
  gap: 4px;
}

.title-wrapper .deck-meta-row .deck-meta .card-count {
  padding: 8px 12px;
  background-color: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}


.card-count {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  font-size: 0.9rem;
}

.card-count.over-limit {
  color: white;
  background-color: #e53e3e;
  border-color: #e53e3e;
}

.deck-header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.back-btn {
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
}

.back-btn:hover {
  background-color: #edf2f7;
  border-color: #cbd5e0;
}

.back-icon {
  margin-right: 6px;
}

.stats-btn {
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
}

.stats-btn:hover {
  background-color: #ebf8ff;
  border-color: #bee3f8;
  color: #3182ce;
}

.stats-icon {
  margin-right: 6px;
}

.delete-deck-btn {
  padding: 8px 12px;
  background-color: #fff5f5;
  color: #e53e3e;
  border: 1px solid #fed7d7;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.delete-deck-btn:hover {
  background-color: #fee2e2;
  border-color: #feb2b2;
}

.commander-section {
  margin-bottom: 20px;
}

.commander-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #f7fafc;
}

.commander-card:hover {
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.commander-card img {
  width: 60px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.commander-name {
  font-weight: 600;
}

.deck-cards {
  margin-bottom: 20px;
}

.deck-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  margin: 4px 0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.deck-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: inherit;
  z-index: -1;
  border-radius: 6px;
}

.deck-card[style*="White"] { --color-intensity: 0.8; }
.deck-card[style*="Blue"] { --color-intensity: 0.7; }
.deck-card[style*="Black"] { --color-intensity: 0.6; }
.deck-card[style*="Red"] { --color-intensity: 0.7; }
.deck-card[style*="Green"] { --color-intensity: 0.7; }

.deck-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.card-info {
  flex: 1;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.card-count {
  font-size: 12px;
  color: #595959;
  margin-left: 8px;
  margin-right: 8px;
}

.color-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 4px;
}

.card-actions {
  display: flex;
  align-items: center;
}

.add-btn {
  background: none;
  border: 1px solid #e2e8f0;
  color: #718096;
  font-size: 1.125rem;
  cursor: pointer;
  width: 10px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background-color: #f7fafc;
}

.add-btn:hover {
  color: white;
  background-color: #4299e1;
  border-color: #4299e1;
  transform: scale(1.1);
}

.remove-btn {
  background: none;
  border: 1px solid #e2e8f0;
  color: #718096;
  font-size: 1rem;
  cursor: pointer;
  width: 10px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background-color: #f7fafc;
}

.remove-btn:hover {
  color: white;
  background-color: #e53e3e;
  border-color: #e53e3e;
  transform: scale(1.1);
}

.add-btn:active, .remove-btn:active {
  transform: scale(0.9);
}

.deck-actions {
  margin-top: 20px;
  position: sticky;
  bottom: 16px;
  background-color: white;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
}

.save-deck-btn {
  width: 100%;
  padding: 12px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s ease;
  margin-bottom: 10px;
}

.save-deck-btn:hover:not(:disabled) {
  background-color: #3182ce;
}

.save-deck-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.7;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.modal-content {
  background: white;
  border-radius: 10px;
  padding: 24px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.5rem;
  color: #4299e1;
  border-bottom: 2px solid #4299e1;
  padding-bottom: 10px;
}

.modal-subtitle {
  font-size: 1.1rem;
  margin-bottom: 10px;
}

.commander-search {
  width: 700px;
  max-width: 90%;
}

.search-box {
  margin-bottom: 16px;
}

.search-box input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.search-box input:focus {
  border-color: #4299e1;
  outline: none;
}

.commander-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 16px;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.commander-option {
  text-align: center;
  cursor: pointer;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.commander-option:hover {
  border-color: #4299e1;
  background-color: #f7fafc;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.commander-option img, .land-preview img, .selected-commander img {
  width: 100%;
  border-radius: 5px;
  margin-bottom: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.search-result-name {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.selected-commander, .selected-land {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #f7fafc;
}

.commander-preview, .land-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.commander-preview img, .land-preview img {
  width: 70px;
  border-radius: 5px;
}

.selected-card-name {
  font-weight: 500;
  font-size: 1rem;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus {
  border-color: #4299e1;
  outline: none;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn, .confirm-btn, .search-commander-btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn {
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  color: #4a5568;
}

.cancel-btn:hover {
  border-color: #a0aec0;
  background-color: #edf2f7;
}

.confirm-btn {
  background-color: #4299e1;
  border: 1px solid #4299e1;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #3182ce;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.delete-btn {
  background-color: #e53e3e !important;
  border-color: #e53e3e !important;
}

.delete-btn:hover {
  background-color: #c53030 !important;
  border-color: #c53030 !important;
}

.search-commander-btn {
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  width: 100%;
  text-align: center;
  font-weight: 500;
}

.search-commander-btn:hover {
  border-color: #4299e1;
  color: #4299e1;
}

@keyframes cardAdded {
  0% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(56, 161, 105, 0.2);
  }
  100% {
    background-color: transparent;
  }
}

.card-added {
  animation: cardAdded 0.3s ease-in-out;
}

@keyframes countChanged {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
    color: #38a169;
  }
  100% {
    transform: scale(1);
  }
}

.count-changed {
  animation: countChanged 0.3s ease-in-out;
}

.ms {
  display: inline-block;
  width: 1.3em;
  height: 1.3em;
  font-size: 1em;
  border-radius: 50%;
  margin: 0 2px;
  text-align: center;
  line-height: 1.3em;
  color: white;
  font-weight: bold;
  box-shadow: -0.05em 0.12em 0 0 rgba(0, 0, 0, 0.3);
  vertical-align: middle;
  position: relative;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ms-w {
  background-color: #f0f2c0;
}

.ms-u {
  background-color: #b5cde3;
}

.ms-b {
  background-color: #aca29a;
  color: #fff;
}

.ms-r {
  background-color: #db8664;
}

.ms-g {
  background-color: #93b483;
}

.ms-c {
  background-color: #ccc;
}

@media (max-width: 768px) {
  .deck-sidebar {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    height: 100vh;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  
  .deck-sidebar.open {
    transform: translateX(0);
  }
  
  .commander-results {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}

.deck-sidebar::-webkit-scrollbar {
  width: 8px;
}

.deck-sidebar::-webkit-scrollbar-track {
  background: #f7fafc;
}

.deck-sidebar::-webkit-scrollbar-thumb {
  background-color: #a0aec0;
  border-radius: 20px;
}

.commander-results::-webkit-scrollbar {
  width: 8px;
}

.commander-results::-webkit-scrollbar-track {
  background: #f7fafc;
}

.commander-results::-webkit-scrollbar-thumb {
  background-color: #a0aec0;
  border-radius: 20px;
}

.deck-card.invalid-color {
  background: linear-gradient(to right, rgba(255, 59, 48, 0.2), transparent) !important;
  border-left: 3px solid rgba(255, 59, 48, 0.5);
}

.deck-card.invalid-format {
  background: linear-gradient(to right, rgba(255, 149, 0, 0.2), transparent) !important;
  border-left: 3px solid rgba(255, 149, 0, 0.5);
}

.deck-card.invalid-color::after,
.deck-card.invalid-format::after {
  content: attr(data-invalid-reason);
  position: absolute;
  right: 10px;
  top: 10px;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  opacity: 0;
  transition: opacity 0.2s;
}

.deck-card:hover::after {
  opacity: 1;
}

.color-W { background: #f8f8f7; }
.color-U { background: #0e68ab; }
.color-B { background: #150b00; }
.color-R { background: #d3202a; }
.color-G { background: #00733e; }

.connection-status {
  padding: 8px 12px;
  margin-bottom: 16px;
  border-radius: 4px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
}

.status-icon {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.connection-status.checking .status-icon {
  background-color: #ed8936; /* orange */
  animation: pulse 1.5s infinite;
}

.connection-status.connected .status-icon {
  background-color: #48bb78; /* green */
}

.connection-status.disconnected .status-icon,
.connection-status.error .status-icon {
  background-color: #e53e3e; /* red */
}

.sync-time {
  color: #718096;
  font-size: 0.8rem;
  margin-left: auto;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

</style>