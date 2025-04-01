<template>
  <div class="playtest-popup">
      <button @click="$emit('close')" class="close-button">Close</button>
    <!-- Deck Selection Phase -->
    <div v-if="phase === 'select'" class="deck-selection">
  <h2>Select a Deck to Playtest</h2>
  <div v-if="!decks || decks.length === 0" class="no-decks-message">
    <p>No decks available. Please create a deck first.</p>
    <p v-if="loading">Loading decks...</p>
  </div>
      <div v-else>
        <select v-model="selectedDeck" class="deck-selector">
          <option value="" disabled selected>-- Select a deck --</option>
          <option v-for="deck in decks" :key="deck.id" :value="deck.id">
            {{ deck.name }}
          </option>
        </select>
        <button @click="loadDeck" :disabled="!selectedDeck" class="confirm-button">
          Load Deck
        </button>
      </div>
    </div>

    <!-- Initial Draw Phase -->
    <div v-if="phase === 'initialDraw'" class="initial-draw">
      <h2>Your Opening Hand</h2>
      <div class="hand-zone">
        <div 
          v-for="(card, index) in initialHand" 
          :key="index" 
          class="card-wrapper"
          @click="toggleCardSelect(index)"
          :class="{ 'selected': selectedCards.includes(index) }"
        >
          <img :src="card.image_uris?.normal || card.card_faces[0].image_uris.normal" 
               :alt="card.name" 
               class="card-image"
               draggable="false">
        </div>
      </div>
      <div class="action-buttons">
        <button @click="keepHand" class="action-button keep">Keep</button>
        <button @click="mulligan" class="action-button mulligan">Mulligan</button>
        <button @click="drawCard" class="action-button draw">Draw</button>
      </div>
    </div>

    <!-- Playtest Interface -->
    <div v-if="phase === 'playtest'" class="playtest-interface">
      <!-- Command Zone -->
      <div class="command-zone" @drop="dropCard($event, 'command')" @dragover.prevent>
        <h3>Command Zone</h3>
        <div v-for="(card, index) in commandZone" :key="'command-' + index" class="card-wrapper">
          <img :src="getCardImage(card)" 
               :alt="card.name" 
               class="card-image"
               draggable="true"
               @dragstart="dragStart($event, card, 'command', index)"
               @contextmenu.prevent="openCardMenu($event, card, 'command', index)">
          <div v-if="card.isCommander" class="commander-tax">
            Tax: {{ commanderTax }}
          </div>
        </div>
      </div>

      <!-- Exile Zone -->
      <div class="exile-zone" @drop="dropCard($event, 'exile')" @dragover.prevent>
        <h3>Exile</h3>
        <div v-for="(card, index) in exileZone" :key="'exile-' + index" class="card-wrapper">
          <img :src="getCardImage(card)" 
               :alt="card.name" 
               class="card-image"
               draggable="true"
               @dragstart="dragStart($event, card, 'exile', index)"
               @contextmenu.prevent="openCardMenu($event, card, 'exile', index)">
        </div>
      </div>

      <!-- Battlefield -->
      <div class="battlefield" @drop="dropCard($event, 'battlefield')" @dragover.prevent>
        <h3>Battlefield</h3>
        <div class="battlefield-cards">
          <div v-for="(card, index) in battlefield" :key="'battlefield-' + index" 
               class="battlefield-card" 
               :style="{ transform: card.tapped ? 'rotate(90deg)' : 'none' }">
            <img :src="getCardImage(card)" 
                 :alt="card.name" 
                 class="card-image"
                 draggable="true"
                 @dragstart="dragStart($event, card, 'battlefield', index)"
                 @contextmenu.prevent="openCardMenu($event, card, 'battlefield', index)">
            <div v-if="card.counters > 0" class="counter-badge">
              {{ card.counters }}
            </div>
            <div v-if="card.power !== undefined || card.toughness !== undefined" class="pt-indicator">
              {{ card.power }}/{{ card.toughness }}
            </div>
          </div>
        </div>
        <button @click="addToken" class="token-button">Add Token</button>
      </div>

      <!-- Hand Zone -->
      <div class="hand-zone" @drop="dropCard($event, 'hand')" @dragover.prevent>
        <h3>Hand</h3>
        <div class="hand-cards">
          <div v-for="(card, index) in hand" :key="'hand-' + index" class="card-wrapper">
            <img :src="getCardImage(card)" 
                 :alt="card.name" 
                 class="card-image"
                 draggable="true"
                 @dragstart="dragStart($event, card, 'hand', index)"
                 @contextmenu.prevent="openCardMenu($event, card, 'hand', index)">
          </div>
        </div>
      </div>

      <!-- Library and Graveyard -->
      <div class="library-graveyard">
        <div class="library" @drop="dropCard($event, 'library')" @dragover.prevent>
          <h3>Library ({{ library.length }})</h3>
          <img src="@/assets/cards/mtg-card-back.jpg" 
               alt="Library" 
               class="library-image"
               @click="searchLibrary"
               draggable="false">
          <button @click="drawCard" class="draw-button">Draw</button>
        </div>
        <div class="graveyard" @drop="dropCard($event, 'graveyard')" @dragover.prevent>
          <h3>Graveyard</h3>
          <div v-if="graveyard.length > 0" class="top-of-graveyard">
            <img :src="getCardImage(graveyard[graveyard.length - 1])" 
                 :alt="graveyard[graveyard.length - 1].name" 
                 class="card-image"
                 draggable="true"
                 @dragstart="dragStart($event, graveyard[graveyard.length - 1], 'graveyard', graveyard.length - 1)"
                 @contextmenu.prevent="openCardMenu($event, graveyard[graveyard.length - 1], 'graveyard', graveyard.length - 1)">
          </div>
          <div v-else class="empty-graveyard">
            <span>Empty</span>
          </div>
        </div>
      </div>

      <!-- Context Menu -->
      <div v-if="showContextMenu" 
           class="context-menu" 
           :style="{ top: contextMenuPosition.y + 'px', left: contextMenuPosition.x + 'px' }"
           @click.stop>
        <div class="context-menu-item" @click="flipCard">Flip Card</div>
        <div class="context-menu-item" @click="tapCard">{{ draggedCard.tapped ? 'Untap' : 'Tap' }}</div>
        <div class="context-menu-item" @click="addCounter">Add Counter</div>
        <div class="context-menu-item" @click="removeCounter">Remove Counter</div>
        <div class="context-menu-item" @click="setPowerToughness">Set Power/Toughness</div>
        <div class="context-menu-item" @click="createTokenCopy">Create Token Copy</div>
      </div>

      <!-- Token Creation Modal -->
      <div v-if="showTokenModal" class="modal-overlay">
        <div class="token-modal">
          <h3>Create Token</h3>
          <div class="token-form">
            <label>
              Token Name:
              <input v-model="tokenName" type="text" placeholder="Enter token name">
            </label>
            <label>
              Quantity:
              <input v-model="tokenQuantity" type="number" min="1" max="100" value="1">
            </label>
            <label>
              Image URL (optional):
              <input v-model="tokenImageUrl" type="text" placeholder="Enter image URL">
            </label>
            <div class="token-modal-buttons">
              <button @click="createToken" class="confirm-button">Create</button>
              <button @click="cancelTokenCreation" class="cancel-button">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Power/Toughness Modal -->
      <div v-if="showPTModal" class="modal-overlay">
        <div class="pt-modal">
          <h3>Set Power/Toughness</h3>
          <div class="pt-form">
            <label>
              Power:
              <input v-model="newPower" type="number">
            </label>
            <label>
              Toughness:
              <input v-model="newToughness" type="number">
            </label>
            <div class="pt-modal-buttons">
              <button @click="savePT" class="confirm-button">Save</button>
              <button @click="cancelPT" class="cancel-button">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Library Search Modal -->
      <div v-if="showLibrarySearch" class="modal-overlay">
        <div class="library-search-modal">
          <h3>Search Library</h3>
          <input v-model="librarySearchQuery" 
                 type="text" 
                 placeholder="Search for a card..."
                 @input="searchLibraryCards">
          <div class="search-results">
            <div v-for="card in librarySearchResults" 
                 :key="card.id" 
                 class="search-result-card"
                 @click="moveCardToHand(card)">
              <img :src="getCardImage(card)" 
                   :alt="card.name" 
                   class="search-card-image">
              <span>{{ card.name }}</span>
            </div>
          </div>
          <div class="library-search-buttons">
            <button @click="closeLibrarySearch" class="cancel-button">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlaytestPopup',
  props: {
    decks: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedDeck: null,
      phase: 'select', // 'select', 'initialDraw', 'playtest'
      initialHand: [],
      selectedCards: [],
      loading: true,
      
      // Game zones
      hand: [],
      library: [],
      graveyard: [],
      exileZone: [],
      commandZone: [],
      battlefield: [],
      
      // Drag and drop
      draggedCard: null,
      draggedFromZone: null,
      draggedFromIndex: null,
      
      // Context menu
      showContextMenu: false,
      contextMenuPosition: { x: 0, y: 0 },
      contextCard: null,
      contextZone: null,
      contextIndex: null,
      
      // Token creation
      showTokenModal: false,
      tokenName: '',
      tokenQuantity: 1,
      tokenImageUrl: '',
      
      // Power/Toughness
      showPTModal: false,
      newPower: 0,
      newToughness: 0,
      
      // Library search
      showLibrarySearch: false,
      librarySearchQuery: '',
      librarySearchResults: [],
      
      // Game state
      commanderTax: 0,
      mulliganCount: 0
    }
  },
  mounted() {
    // Log decks to help with debugging
    console.log('Decks received in PlaytestPopup:', this.decks);
  if (!this.decks || this.decks.length === 0) {
    console.warn('No decks received in PlaytestPopup');
  }

  console.log('Decks available:', this.decks);
  this.loading = false;
  },
  methods: {
    loadDeck() {
      if (!this.selectedDeck) {
        console.error('No deck selected');
        return;
      }
      
      const deck = this.decks.find(d => d.id === this.selectedDeck);
      if (!deck) {
        console.error('Selected deck not found:', this.selectedDeck);
        return;
      }
      
      console.log('Loading deck:', deck);
      
      // Shuffle the deck
      this.library = [...deck.cards];
      this.shuffleDeck();
      
      // Check for commanders
      if (deck.commanders && deck.commanders.length > 0) {
        this.commandZone = deck.commanders.map(commander => ({
          ...commander,
          isCommander: true
        }));
      }
      
      // Draw initial hand
      this.drawInitialHand();
      this.phase = 'initialDraw';
    },
    
    shuffleDeck() {
      for (let i = this.library.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [this.library[i], this.library[j]] = [this.library[j], this.library[i]];
      }
    },
    
    drawInitialHand() {
      this.initialHand = [];
      for (let i = 0; i < 7; i++) {
        if (this.library.length > 0) {
          this.initialHand.push(this.library.pop());
        }
      }
    },
    
    toggleCardSelect(index) {
      const idx = this.selectedCards.indexOf(index);
      if (idx === -1) {
        this.selectedCards.push(index);
      } else {
        this.selectedCards.splice(idx, 1);
      }
    },
    
    keepHand() {
      this.hand = [...this.initialHand];
      this.phase = 'playtest';
    },
    
    mulligan() {
      this.mulliganCount++;
      
      // Put selected cards back (or all if none selected)
      const cardsToMulligan = this.selectedCards.length > 0 
        ? this.selectedCards.sort((a, b) => b - a).map(i => this.initialHand[i])
        : [...this.initialHand];
      
      // Return cards to library
      cardsToMulligan.forEach(card => {
        this.library.push(card);
      });
      
      // Shuffle
      this.shuffleDeck();
      
      // Draw new hand (one less if not partial mulligan)
      const newHandSize = this.selectedCards.length > 0 
        ? this.initialHand.length 
        : Math.max(0, 7 - this.mulliganCount);
      
      this.initialHand = [];
      this.selectedCards = [];
      
      for (let i = 0; i < newHandSize; i++) {
        if (this.library.length > 0) {
          this.initialHand.push(this.library.pop());
        }
      }
    },
    
    drawCard() {
      if (this.library.length > 0) {
        const card = this.library.pop();
        if (this.phase === 'initialDraw') {
          this.initialHand.push(card);
        } else {
          this.hand.push(card);
        }
      }
    },
    
    // Drag and Drop methods
    dragStart(event, card, zone, index) {
      event.dataTransfer.setData('text/plain', ''); // Required for Firefox
      this.draggedCard = card;
      this.draggedFromZone = zone;
      this.draggedFromIndex = index;
    },
    
    dropCard(event, targetZone) {
      event.preventDefault();
      
      if (!this.draggedCard) return;
      
      // Remove from original zone
      switch (this.draggedFromZone) {
        case 'hand':
          this.hand.splice(this.draggedFromIndex, 1);
          break;
        case 'battlefield':
          this.battlefield.splice(this.draggedFromIndex, 1);
          break;
        case 'graveyard':
          this.graveyard.splice(this.draggedFromIndex, 1);
          break;
        case 'exile':
          this.exileZone.splice(this.draggedFromIndex, 1);
          break;
        case 'command':
          this.commandZone.splice(this.draggedFromIndex, 1);
          break;
        case 'library':
          this.library.splice(this.draggedFromIndex, 1);
          break;
      }
      
      // Add to target zone
      const cardToAdd = { ...this.draggedCard };

      // Handle tokens (they can't go to certain zones)
      if (cardToAdd.isToken) {
        if (targetZone === 'hand' || targetZone === 'library') {
          // Tokens cease to exist when moved to hand or library
          this.draggedCard = null;
          return;
        }
      }

      let randomPos; // Declare the variable outside the switch statement

      switch (targetZone) {
        case 'hand':
          this.hand.push(cardToAdd);
          break;
        case 'battlefield':
          this.battlefield.push(cardToAdd);
          break;
        case 'graveyard':
          this.graveyard.push(cardToAdd);
          break;
        case 'exile':
          this.exileZone.push(cardToAdd);
          break;
        case 'command':
          this.commandZone.push(cardToAdd);
          break;
        case 'library':
          // Add to a random position in library
          randomPos = Math.floor(Math.random() * this.library.length);
          this.library.splice(randomPos, 0, cardToAdd);
          break;
      }
      
      this.draggedCard = null;
    },
    
    // Context menu methods
    openCardMenu(event, card, zone, index) {
      this.contextCard = card;
      this.contextZone = zone;
      this.contextIndex = index;
      this.contextMenuPosition = {
        x: event.clientX,
        y: event.clientY
      };
      this.showContextMenu = true;
      
      // Close menu when clicking elsewhere
      const closeMenu = () => {
        this.showContextMenu = false;
        document.removeEventListener('click', closeMenu);
      };
      document.addEventListener('click', closeMenu);
    },
    
    flipCard() {
      if (!this.contextCard) return;
      
      if (this.contextZone === 'battlefield') {
        const card = this.battlefield[this.contextIndex];
        card.flipped = !card.flipped;
      }
      this.showContextMenu = false;
    },
    
    tapCard() {
      if (!this.contextCard || this.contextZone !== 'battlefield') return;
      
      const card = this.battlefield[this.contextIndex];
      card.tapped = !card.tapped;
      this.showContextMenu = false;
    },
    
    addCounter() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card) {
        if (!card.counters) card.counters = 0;
        card.counters++;
      }
      this.showContextMenu = false;
    },
    
    removeCounter() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card && card.counters && card.counters > 0) {
        card.counters--;
      }
      this.showContextMenu = false;
    },
    
    setPowerToughness() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card) {
        this.newPower = card.power !== undefined ? card.power : 0;
        this.newToughness = card.toughness !== undefined ? card.toughness : 0;
        this.showPTModal = true;
      }
      this.showContextMenu = false;
    },
    
    savePT() {
      const card = this.getCardFromZone();
      if (card) {
        card.power = this.newPower;
        card.toughness = this.newToughness;
      }
      this.showPTModal = false;
    },
    
    cancelPT() {
      this.showPTModal = false;
    },
    
    createTokenCopy() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card) {
        this.tokenName = card.name + " Token";
        this.tokenImageUrl = this.getCardImage(card);
        this.showTokenModal = true;
      }
      this.showContextMenu = false;
    },
    
    getCardFromZone() {
      switch (this.contextZone) {
        case 'hand': return this.hand[this.contextIndex];
        case 'battlefield': return this.battlefield[this.contextIndex];
        case 'graveyard': return this.graveyard[this.contextIndex];
        case 'exile': return this.exileZone[this.contextIndex];
        case 'command': return this.commandZone[this.contextIndex];
        default: return null;
      }
    },
    
    // Token methods
    addToken() {
      this.tokenName = '';
      this.tokenQuantity = 1;
      this.tokenImageUrl = '';
      this.showTokenModal = true;
    },
    
    createToken() {
      for (let i = 0; i < this.tokenQuantity; i++) {
        this.battlefield.push({
          name: this.tokenName || 'Token',
          isToken: true,
          image_uris: {
            normal: this.tokenImageUrl || require('@/assets/cards/mtg-token-default.jpg')
          },
          tapped: false,
          flipped: false,
          counters: 0
        });
      }
      this.showTokenModal = false;
    },
    
    cancelTokenCreation() {
      this.showTokenModal = false;
    },
    
    // Library search methods
    searchLibrary() {
      this.librarySearchQuery = '';
      this.librarySearchResults = [...this.library];
      this.showLibrarySearch = true;
    },
    
    searchLibraryCards() {
      if (!this.librarySearchQuery) {
        this.librarySearchResults = [...this.library];
        return;
      }
      
      const query = this.librarySearchQuery.toLowerCase();
      this.librarySearchResults = this.library.filter(card => 
        card.name.toLowerCase().includes(query)
      );
    },
    
    moveCardToHand(card) {
      const index = this.library.findIndex(c => c.id === card.id);
      if (index !== -1) {
        this.library.splice(index, 1);
        this.hand.push(card);
      }
      this.closeLibrarySearch();
    },
    
    closeLibrarySearch() {
      this.showLibrarySearch = false;
    },
    
    // Helper methods
    getCardImage(card) {
      if (card.flipped) {
        return card.card_faces ? card.card_faces[1].image_uris.normal : require('@/assets/cards/mtg-card-back.jpg');
      }
      return card.image_uris?.normal || (card.card_faces ? card.card_faces[0].image_uris.normal : require('@/assets/cards/mtg-card-back.jpg'));
    }
  },
}
</script>
  
  <style scoped>
  .playtest-popup {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    color: white;
  }
  
  .deck-selection {
    background-color: #2c3e50;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
  }
  
  .deck-selector {
    display: block;
    width: 100%;
    padding: 0.5rem;
    margin: 1rem 0;
    font-size: 1rem;
  }
  
  .confirm-button {
    background-color: #42b983;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .confirm-button:hover {
    background-color: #3aa876;
  }
  
  .initial-draw {
    background-color: #2c3e50;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
  }
  
  .hand-zone {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 1rem 0;
  }
  
  .card-wrapper {
    position: relative;
    cursor: pointer;
  }
  
  .card-wrapper.selected {
    box-shadow: 0 0 10px 5px gold;
  }
  
  .card-image {
    width: 150px;
    height: auto;
    border-radius: 10px;
    transition: transform 0.2s;
  }
  
  .card-image:hover {
    transform: scale(1.05);
  }
  
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .action-button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
  }
  
  .keep {
    background-color: #4CAF50;
    color: white;
  }
  
  .mulligan {
    background-color: #f39c12;
    color: white;
  }
  
  .draw {
    background-color: #3498db;
    color: white;
  }
  
  .playtest-interface {
    width: 90%;
    height: 90%;
    background-color: #2c3e50;
    border-radius: 10px;
    padding: 1rem;
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    overflow: auto;
  }
  
  .command-zone, .exile-zone {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 5px;
  }
  
  .battlefield {
    grid-column: span 2;
    background-color: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 5px;
    min-height: 200px;
  }
  
  .battlefield-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .battlefield-card {
    position: relative;
    transition: transform 0.3s;
  }
  
  .hand-zone {
    grid-column: span 2;
    background-color: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 5px;
  }
  
  .hand-cards {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding: 0.5rem;
  }
  
  .library-graveyard {
    display: flex;
    gap: 1rem;
  }
  
  .library, .graveyard {
    flex: 1;
    background-color: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 5px;
    text-align: center;
  }
  
  .library-image {
    width: 150px;
    height: auto;
    cursor: pointer;
  }
  
  .draw-button {
    display: block;
    margin: 0.5rem auto;
    padding: 0.3rem 0.6rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .top-of-graveyard {
    display: inline-block;
  }
  
  .empty-graveyard {
    padding: 1rem;
    color: #7f8c8d;
  }
  
  .token-button {
    margin-top: 0.5rem;
    padding: 0.3rem 0.6rem;
    background-color: #9b59b6;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .context-menu {
    position: fixed;
    background-color: #34495e;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    z-index: 1001;
  }
  
  .context-menu-item {
    padding: 0.5rem 1rem;
    cursor: pointer;
  }
  
  .context-menu-item:hover {
    background-color: #2c3e50;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1002;
  }
  
  .token-modal, .pt-modal, .library-search-modal {
    background-color: #2c3e50;
    padding: 1.5rem;
    border-radius: 10px;
    min-width: 300px;
    max-width: 80%;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .token-form, .pt-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin: 1rem 0;
  }
  
  .token-form label, .pt-form label {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }
  
  .token-form input, .pt-form input {
    padding: 0.5rem;
    border-radius: 5px;
    border: 1px solid #7f8c8d;
  }
  
  .token-modal-buttons, .pt-modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  
  .cancel-button {
    background-color: #e74c3c;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .counter-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    background-color: #e74c3c;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.8rem;
    font-weight: bold;
  }
  
  .pt-indicator {
    position: absolute;
    bottom: 5px;
    right: 5px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.8rem;
  }
  
  .commander-tax {
    position: absolute;
    bottom: 5px;
    left: 5px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.8rem;
  }
  
  .library-search-modal {
    width: 80%;
    max-width: 800px;
  }
  
  .search-results {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
    max-height: 60vh;
    overflow-y: auto;
  }
  
  .search-result-card {
    cursor: pointer;
    transition: transform 0.2s;
  }
  
  .search-result-card:hover {
    transform: scale(1.05);
  }
  
  .search-card-image {
    width: 100%;
    height: auto;
    border-radius: 5px;
  }
  .close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  z-index: 1001;
}
  </style>