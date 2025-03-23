<template>
  <div class="deck-sidebar">
    <div v-if="!activeDeck" class="deck-list">
      <h2 class="sidebar-title">Your Decks</h2>
      <div v-for="deck in decks" :key="deck.id" class="deck-item" @click="loadDeck(deck)">
        <span class="deck-name">{{ deck.name }}</span>
        <span class="deck-colors" v-html="formatColors(deck.colors)"></span>
      </div>

      <button class="create-deck-btn" @click="showCreateDeckModal = true">
        <span class="btn-icon">+</span> Create a Deck
      </button>
    </div>
    
    <div v-else class="active-deck">
      <div class="deck-header">
        <div class="deck-header-left">
          <button class="back-btn" @click="backToDecks">
            <span class="back-icon">←</span> Back
          </button>
          <h2 class="deck-title">{{ activeDeck.name }}</h2>
          <div class="deck-meta">
            <span class="deck-colors" v-html="formatColors(activeDeck.colors)"></span>
            <span :class="['card-count', {'over-limit': totalCards > 100}]">
              {{ totalCards }}/100
            </span>
          </div>
        </div>
        <button class="stats-btn" @click="showDeckStats">
          <span class="stats-icon">📊</span> Stats
        </button>
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
          :data-card-id="card.id"
          @click="viewCardDetails(card)"
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
            <div class="card-details">
              <span class="card-type">{{ card.type_line }}</span>
            </div>
          </div>
          <div class="card-actions">
            <button v-if="isBasicLand(card)" class="add-btn" @click.stop="addOneCard(card, $event)">+</button>
            <button class="remove-btn" @click.stop="removeCard(card)">−</button>
          </div>
        </div>
      </div>
      
      <div class="deck-actions">
        <button class="save-deck-btn" :disabled="totalCards > 100" @click="saveDeck">
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
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeckSidebar',
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
      newDeckName: '',
      selectedCommander: null,
      commanderQuery: '',
      commanderResults: [],
      selectedLand: null,
      landCount: 1,
    };
  },
  computed: {
    sortedCards() {
      if (!this.activeDeck) return [];
      // Sort cards by mana value (cmc) in ascending order
      return this.activeDeck.cards
        .slice()
        .sort((a, b) => (a.cmc || 0) - (b.cmc || 0));
    },
    totalCards() {
      if (!this.activeDeck) return 0;
      return this.activeDeck.cards.reduce((total, card) => total + (card.count || 1), 0);
    }
  },
  watch: {
    // Add a watcher for the selectedCard prop
    selectedCard(newCard) {
      if (newCard && this.activeDeck) {
        if (this.isBasicLand(newCard)) {
          this.selectedLand = newCard;
          this.showAddLandsModal = true;
        } else {
          this.addCardToDeck(newCard);
        }
      }
    }
  },
  methods: {
    isBasicLand(card) {
      return card?.type_line?.toLowerCase().includes('basic land');
    },
    formatColors(colors) {
      if (!colors || colors.length === 0) return '<span class="ms ms-c"></span>';
      return colors
        .map(color => `<span class="ms ms-${color.toLowerCase()}"></span>`)
        .join(' ');
    },
    formatManaCost(manaCost) {
      if (!manaCost) return '';
      return manaCost.replace(/\{([^}]+)\}/g, (match, symbol) => {
        const symbolMap = {
          'W': 'ms-w',
          'U': 'ms-u',
          'B': 'ms-b',
          'R': 'ms-r',
          'G': 'ms-g',
          '0': 'ms-0',
          '1': 'ms-1',
          '2': 'ms-2',
          '3': 'ms-3',
          '4': 'ms-4',
          '5': 'ms-5',
          '6': 'ms-6',
          '7': 'ms-7',
          '8': 'ms-8',
          '9': 'ms-9',
          '10': 'ms-10',
          'X': 'ms-x',
          'T': 'ms-tap',
          'Q': 'ms-untap',
        };
        const cssClass = symbolMap[symbol.toUpperCase()] || 'ms';
        return `<span class="ms ${cssClass}">${symbol}</span>`;
      });
    },
    loadDeck(deck) {
      this.activeDeck = JSON.parse(JSON.stringify(deck)); // Create a deep copy
    },
    backToDecks() {
      this.activeDeck = null;
    },
    viewCardDetails(card) {
      this.$emit('view-card', card);
    },
    // Add one copy of a card that's already in the deck
    addOneCard(card, event) {
      const index = this.activeDeck.cards.findIndex(c => c.id === card.id);
      if (index !== -1) {
        if (this.isBasicLand(card)) {
          // For basic lands, set count or increment
          if (!this.activeDeck.cards[index].count) {
            this.activeDeck.cards[index].count = 2; // First increment
          } else {
            this.activeDeck.cards[index].count++;
          }
          
          // Add animation classes
          if (event) {
            const cardElement = event.target.closest('.deck-card');
            if (cardElement) {
              cardElement.classList.add('card-added');
              setTimeout(() => {
                cardElement.classList.remove('card-added');
              }, 300);
            }
          }
        }
      }
    },
    addCardToDeck(card) {
      const cardClone = JSON.parse(JSON.stringify(card)); // Create a deep copy
      // Check if this card is already in the deck
      const index = this.activeDeck.cards.findIndex(c => c.id === card.id);
      
      if (index !== -1) {
        // Card already exists, increment count if it's a basic land
        if (this.isBasicLand(card)) {
          if (!this.activeDeck.cards[index].count) {
            this.activeDeck.cards[index].count = 2;
          } else {
            this.activeDeck.cards[index].count++;
          }
        } else {
          // Non-lands are usually limited to 1 copy in Commander
          // For simplicity we'll just show a message and not add duplicates
          alert('This card is already in your deck. In Commander format, you can only have one copy of each non-basic land card.');
        }
      } else {
        // Card not in deck, add it
        this.activeDeck.cards.push(cardClone);
        
        // Animate the new card
        this.$nextTick(() => {
          const cardElements = document.querySelectorAll('.deck-card');
          const newCard = Array.from(cardElements).find(el => el.dataset.cardId === cardClone.id);
          if (newCard) {
            newCard.classList.add('card-added');
            setTimeout(() => {
              newCard.classList.remove('card-added');
            }, 300);
          }
        });
      }
    },
    addMultipleLands() {
      if (this.selectedLand && this.landCount > 0) {
        const index = this.activeDeck.cards.findIndex(c => c.id === this.selectedLand.id);
        
        if (index !== -1) {
          // Land already exists, update count
          if (!this.activeDeck.cards[index].count) {
            this.activeDeck.cards[index].count = this.landCount;
          } else {
            this.activeDeck.cards[index].count += this.landCount - 1; // -1 because one copy is already counted
          }
        } else {
          // Land not in deck, add it with count
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
          // If multiple copies, reduce count
          this.activeDeck.cards[index].count--;
        } else {
          // Remove the card entirely
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
        if (this.commanderQuery.length < 2) {
          // Default search for legendary creatures if no query
          const response = await axios.get('https://api.scryfall.com/cards/search', {
            params: {
              q: 'type:legendary type:creature',
              order: 'edhrec',
              unique: 'cards',
              page: 1
            }
          });
          this.commanderResults = response.data.data.slice(0, 20);
        } else {
          const response = await axios.get('https://api.scryfall.com/cards/search', {
            params: {
              q: `${this.commanderQuery} type:legendary type:creature`,
              order: 'name',
              unique: 'cards',
              page: 1
            }
          });
          this.commanderResults = response.data.data;
        }
      } catch (error) {
        console.error('Error searching for commanders:', error);
        this.commanderResults = [];
      }
    },
    selectCommander(card) {
      this.selectedCommander = card;
      this.showCommanderSearch = false;
      
      // Extract color identity from commander
      this.commanderColors = card.color_identity || [];
    },
    createDeck() {
      if (this.newDeckName && this.selectedCommander) {
        const newDeck = {
          id: Date.now().toString(),
          name: this.newDeckName,
          commander: this.selectedCommander,
          colors: this.selectedCommander.color_identity || [],
          cards: [this.selectedCommander], // Add commander as the first card
          created: new Date().toISOString()
        };
        
        this.decks.push(newDeck);
        this.saveDeckToStorage();
        
        // Reset and close modal
        this.newDeckName = '';
        this.selectedCommander = null;
        this.showCreateDeckModal = false;
        
        // Activate the new deck
        this.loadDeck(newDeck);
      }
    },
    saveDeck() {
      // Find and update the deck in the decks array
      const index = this.decks.findIndex(deck => deck.id === this.activeDeck.id);
      if (index !== -1) {
        this.decks[index] = JSON.parse(JSON.stringify(this.activeDeck));
        this.saveDeckToStorage();
        alert('Deck saved successfully!');
      }
    },
    saveDeckToStorage() {
      localStorage.setItem('mtg-decks', JSON.stringify(this.decks));
    },
    loadDecksFromStorage() {
      const storedDecks = localStorage.getItem('mtg-decks');
      if (storedDecks) {
        this.decks = JSON.parse(storedDecks);
      }
    },
    showDeckStats() {
      // Calculate type distribution
      const typeDistribution = {
        creatures: 0,
        instants: 0,
        sorceries: 0,
        artifacts: 0,
        enchantments: 0,
        planeswalkers: 0,
        lands: 0
      };
      
      this.activeDeck.cards.forEach(card => {
        const count = card.count || 1;
        const type = card.type_line.toLowerCase();
        
        if (type.includes('creature')) typeDistribution.creatures += count;
        else if (type.includes('instant')) typeDistribution.instants += count;
        else if (type.includes('sorcery')) typeDistribution.sorceries += count;
        else if (type.includes('artifact')) typeDistribution.artifacts += count;
        else if (type.includes('enchantment')) typeDistribution.enchantments += count;
        else if (type.includes('planeswalker')) typeDistribution.planeswalkers += count;
        else if (type.includes('land')) typeDistribution.lands += count;
      });
      
      // Calculate mana curve
      const manaCurve = {
        '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7+': 0
      };
      
      this.activeDeck.cards.forEach(card => {
        const count = card.count || 1;
        const cmc = card.cmc || 0;
        
        if (cmc >= 7) {
          manaCurve['7+'] += count;
        } else {
          manaCurve[Math.floor(cmc).toString()] += count;
        }
      });
      
      // Show stats in an alert for now (could be improved with a modal)
      alert(`
        Deck Stats: ${this.activeDeck.name}
        
        Card Type Distribution:
        - Creatures: ${typeDistribution.creatures}
        - Instants: ${typeDistribution.instants}
        - Sorceries: ${typeDistribution.sorceries}
        - Artifacts: ${typeDistribution.artifacts}
        - Enchantments: ${typeDistribution.enchantments}
        - Planeswalkers: ${typeDistribution.planeswalkers}
        - Lands: ${typeDistribution.lands}
        
        Mana Curve:
        - 0 CMC: ${manaCurve['0']}
        - 1 CMC: ${manaCurve['1']}
        - 2 CMC: ${manaCurve['2']}
        - 3 CMC: ${manaCurve['3']}
        - 4 CMC: ${manaCurve['4']}
        - 5 CMC: ${manaCurve['5']}
        - 6 CMC: ${manaCurve['6']}
        - 7+ CMC: ${manaCurve['7+']}
        
        Total Cards: ${this.totalCards}/100
      `);
    }
  },
  mounted() {
    this.loadDecksFromStorage();
  }
};
</script>


<style scoped>
.deck-sidebar {
  width: 320px;
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  background-color: white;
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
  padding: 16px;
  box-shadow: var(--sidebar-shadow);
  z-index: 100;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-color);
}

.sidebar-title, .deck-title, .section-title, .modal-title, .modal-subtitle {
  font-weight: 600;
  color: var(--text-color);
  letter-spacing: -0.5px;
}

.sidebar-title, .deck-title {
  margin-top: 0;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--primary-color);
  font-size: 1.5rem;
}

.section-title {
  font-size: 1.2rem;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
}

.deck-list h2, .active-deck h2 {
  margin-top: 0;
}

.deck-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: var(--border-radius);
  margin-bottom: 8px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.deck-name {
  font-weight: 500;
}

.deck-item:hover {
  background-color: var(--background-color);
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--card-shadow);
}

.create-deck-btn {
  width: 100%;
  padding: 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  margin-top: 16px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-speed) ease;
}

.create-deck-btn:hover {
  background-color: var(--primary-hover);
}

.btn-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.deck-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.deck-header-left {
  flex: 1;
}

/* Updated back button style with new accent color */
.back-btn {
  padding: 8px 12px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  transition: all var(--transition-speed) ease;
}

.back-btn:hover {
  background-color: var(--accent-hover);
}

.back-icon {
  margin-right: 6px;
}

/* New stats button */
.stats-btn {
  padding: 8px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: background-color var(--transition-speed) ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.stats-btn:hover {
  background-color: var(--primary-hover);
}

.stats-icon {
  font-size: 0.9em;
}

.deck-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 8px 0;
}

.card-count {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: var(--border-radius);
  background-color: var(--background-color);
}

.card-count.over-limit {
  color: white;
  background-color: var(--error-color);
}

.commander-section {
  margin-bottom: 20px;
}

.commander-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  background-color: var(--background-color);
}

.commander-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--card-shadow);
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

/* Revised deck card layout */
.deck-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: var(--border-radius);
  margin-bottom: 6px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.deck-card:hover {
  background-color: var(--background-color);
  border-color: var(--primary-color);
}

.card-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.card-name {
  font-weight: 600;
  color: var(--text-color);
}

.card-count {
  transition: all var(--transition-speed) ease;
  display: inline-block;
  font-size: 0.9rem;
  margin-left: 8px;
  padding: 2px 6px;
  background-color: var(--background-color);
  border-radius: 12px;
}

.count-changed {
  color: var(--success-color);
  font-weight: bold;
}

.card-type {
  font-size: 0.9rem;
  color: var(--secondary-color);
}

/* Simplified card actions */
.card-actions {
  display: flex;
  align-items: center;
}

/* Show add button only for lands */
.add-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  color: var(--secondary-color);
  font-size: 1.125rem;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-speed) ease;
  margin-left: 8px;
}

.add-btn:hover {
  color: white;
  background-color: var(--success-color);
  border-color: var(--success-color);
  transform: scale(1.1);
}

.remove-btn {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--secondary-color);
  font-size: 1rem;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-speed) ease;
  border-radius: 50%;
}

.remove-btn:hover {
  color: white;
  background-color: var(--error-color);
  border-color: var(--error-color);
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
  border-top: 1px solid var(--border-color);
}

.save-deck-btn {
  width: 100%;
  padding: 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed) ease;
}

.save-deck-btn:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.save-deck-btn:disabled {
  background-color: var(--secondary-color);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Modal styles */
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
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
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
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: border-color var(--transition-speed) ease;
}

.search-box input:focus {
  border-color: var(--primary-color);
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
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  transition: all var(--transition-speed) ease;
}

.commander-option:hover {
  border-color: var(--primary-color);
  background-color: var(--background-color);
  transform: translateY(-2px);
  box-shadow: var(--card-shadow);
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
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background-color: var(--background-color);
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
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 1rem;
}

.form-group input:focus {
  border-color: var(--primary-color);
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
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.cancel-btn {
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.cancel-btn:hover {
  border-color: var(--secondary-color);
  background-color: #edf2f7;
}

.confirm-btn {
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-commander-btn {
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  width: 100%;
  text-align: center;
  font-weight: 500;
}

.search-commander-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* Animation for adding cards */
@keyframes cardAdded {
  0% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(56, 161, 105, 0.2); /* Light green flash */
  }
  100% {
    background-color: transparent;
  }
}

.card-added {
  animation: cardAdded 0.3s ease-in-out;
}

/* Card count animation */
@keyframes countChanged {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
    color: var(--success-color);
  }
  100% {
    transform: scale(1);
  }
}

.count-changed {
  animation: countChanged 0.3s ease-in-out;
}

/* Mana symbols styling */
.ms {
  display: inline-block;
  height: 15px;
  width: 15px;
  font-size: 15px;
  line-height: 15px;
  vertical-align: middle;
  border-radius: 50%;
  color: #111;
  text-align: center;
  box-shadow: -1px 1px 0 rgba(0, 0, 0, 0.85);
  background-color: #ccc;
  margin: 0 1px;
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

/* Media queries for responsive design */
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

/* Scrollbar styling */
.deck-sidebar::-webkit-scrollbar {
  width: 8px;
}

.deck-sidebar::-webkit-scrollbar-track {
  background: var(--background-color);
}

.deck-sidebar::-webkit-scrollbar-thumb {
  background-color: var(--secondary-color);
  border-radius: 20px;
}

.commander-results::-webkit-scrollbar {
  width: 8px;
}

.commander-results::-webkit-scrollbar-track {
  background: var(--background-color);
}

.commander-results::-webkit-scrollbar-thumb {
  background-color: var(--secondary-color);
  border-radius: 20px;
}
</style>