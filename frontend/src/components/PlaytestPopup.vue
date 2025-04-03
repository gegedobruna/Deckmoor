<template>
  <div class="playtest-popup">
    <div v-if="isInitialized" class="playtest-content">
      <div class="popup-header">
        <h2>Playtest</h2>
        <button class="close-btn" @click="closePopup">×</button>
      </div>
      
      <div v-if="phase === 'select'" class="deck-selection">
        <h3>Select a deck to playtest</h3>
        <div v-if="!decks || decks.length === 0" class="no-decks-message">
          <p>No decks available. Please create a deck first.</p>
          <p v-if="loading">Loading decks...</p>
        </div>
        <div v-else>
          <div v-for="deck in decks" :key="deck.id" class="deck-option" @click="selectAndLoadDeck(deck.id)">
            {{ deck.name }}
          </div>
        </div>
      </div>
      
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
            <img :src="getCardImage(card)" 
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

      <div v-if="phase === 'playtest'" class="playtest-interface">
        <div class="top-row">
          <div class="command-zone" @drop="dropCard($event, 'command')" @dragover.prevent @click="toggleZoneExpansion('command')">
            <h3>Command Zone</h3>
            <div v-if="commandZone.length > 0" class="zone-preview">
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
            <div v-else class="empty-zone-message">
              No commander
            </div>
            <button @click="toggleZoneExpansion('command')" class="collapse-button">Collapse</button>
          </div>
          
          <div class="exile-zone" @drop="dropCard($event, 'exile')" @dragover.prevent @click="toggleZoneExpansion('exile')">
            <h3>Exile ({{ exileZone.length }})</h3>
            <div v-if="!isZoneExpanded.exile" class="zone-preview">
              <div v-for="(card, index) in exileZone.slice(0, 3)" :key="'exile-' + index" class="card-wrapper">
                <img :src="getCardImage(card)" 
                     :alt="card.name" 
                     class="card-image"
                     draggable="true"
                     @dragstart="dragStart($event, card, 'exile', index)"
                     @contextmenu.prevent="openCardMenu($event, card, 'exile', index)">
              </div>
              <div v-if="exileZone.length > 3" class="more-cards-indicator">
                +{{ exileZone.length - 3 }} more
              </div>
            </div>
            <div v-if="isZoneExpanded.exile" class="expanded-zone">
              <div class="expanded-cards">
                <div v-for="(card, index) in exileZone" :key="'exile-expanded-' + index" class="card-wrapper">
                  <img :src="getCardImage(card)" 
                       :alt="card.name" 
                       class="card-image"
                       draggable="true"
                       @dragstart="dragStart($event, card, 'exile', index)"
                       @contextmenu.prevent="openCardMenu($event, card, 'exile', index)">
                </div>
              </div>
              <button @click="toggleZoneExpansion('exile')" class="collapse-button">Collapse</button>
            </div>
          </div>
        </div>

        <div class="battlefield" @drop="dropCard($event, 'battlefield')" @dragover.prevent>
          <h3>Battlefield</h3>
          <div class="battlefield-cards">
            <div v-for="(card, index) in battlefield" :key="'battlefield-' + index" 
                 class="battlefield-card" 
                 :style="{ 
                   transform: card.tapped ? 'rotate(90deg)' : 'none',
                   left: card.position?.x + 'px',
                   top: card.position?.y + 'px',
                   position: 'absolute'
                 }"
                 @mousedown="startDrag($event, card, index)"
                 @mouseup="stopDrag"
                 @mousemove="handleDrag($event, card, index)">
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

        <div class="hand-zone" @drop="dropCard($event, 'hand')" @dragover.prevent>
          <h3>Hand ({{ hand.length }})</h3>
          <div class="hand-cards">
            <div v-for="(cardGroup, index) in groupedHand" :key="'hand-' + index" class="card-wrapper">
              <img :src="getCardImage(cardGroup.card)" 
                  :alt="cardGroup.card.name" 
                  class="card-image"
                  draggable="true"
                  @dragstart="dragStart($event, cardGroup.card, 'hand', index)"
                  @contextmenu.prevent="openCardMenu($event, cardGroup.card, 'hand', index)">
              <div v-if="cardGroup.count > 1" class="quantity-badge">
                {{ cardGroup.count }}
              </div>
            </div>
          </div>
        </div>

        <div class="bottom-row">
          <div class="library" @drop="dropCard($event, 'library')" @dragover.prevent>
            <h3>Library ({{ library.length }})</h3>
            <img src="@/assets/cards/mtg-card-back.jpg" 
                 alt="Library" 
                 class="library-image"
                 @click="searchLibrary"
                 draggable="false">
            <button @click="drawCard" class="draw-button">Draw</button>
          </div>

          <div class="graveyard" @drop="dropCard($event, 'graveyard')" @dragover.prevent @click="toggleZoneExpansion('graveyard')">
            <h3>Graveyard ({{ graveyard.length }})</h3>
            <div v-if="!isZoneExpanded.graveyard" class="zone-preview">
              <div v-for="(card, index) in graveyard.slice(0, 3)" :key="'graveyard-' + index" class="card-wrapper">
                <img :src="getCardImage(card)" 
                     :alt="card.name" 
                     class="card-image"
                     draggable="true"
                     @dragstart="dragStart($event, card, 'graveyard', index)"
                     @contextmenu.prevent="openCardMenu($event, card, 'graveyard', index)">
              </div>
              <div v-if="graveyard.length > 3" class="more-cards-indicator">
                +{{ graveyard.length - 3 }} more
              </div>
            </div>
            <div v-if="isZoneExpanded.graveyard" class="expanded-zone">
              <div class="expanded-cards">
                <div v-for="(card, index) in graveyard" :key="'graveyard-expanded-' + index" class="card-wrapper">
                  <img :src="getCardImage(card)" 
                       :alt="card.name" 
                       class="card-image"
                       draggable="true"
                       @dragstart="dragStart($event, card, 'graveyard', index)"
                       @contextmenu.prevent="openCardMenu($event, card, 'graveyard', index)">
                </div>
              </div>
              <button @click="toggleZoneExpansion('graveyard')" class="collapse-button">Collapse</button>
            </div>
          </div>
        </div>

        <div v-if="showContextMenu && contextCard" 
             class="context-menu" 
             :style="{ top: contextMenuPosition.y + 'px', left: contextMenuPosition.x + 'px' }"
             @click.stop>
          <div v-if="contextZone !== 'battlefield'" class="context-menu-item" @click="moveToBattlefield">
            Move to Battlefield
          </div>
          <div v-if="contextZone !== 'exile'" class="context-menu-item" @click="moveToZone('exile')">
            Move to Exile
          </div>
          <div v-if="contextZone !== 'graveyard'" class="context-menu-item" @click="moveToZone('graveyard')">
            Move to Graveyard
          </div>
          <div v-if="contextZone !== 'command'" class="context-menu-item" @click="moveToZone('command')">
            Move to Command Zone
          </div>
          <div v-if="contextZone !== 'hand'" class="context-menu-item" @click="moveToZone('hand')">
            Move to Hand
          </div>
          <div v-if="contextZone !== 'library'" class="context-menu-item" @click="moveToTopOfLibrary">
            Put on Top of Library
          </div>
          <div v-if="contextZone !== 'library'" class="context-menu-item" @click="moveToBottomOfLibrary">
            Put on Bottom of Library
          </div>
          <div v-if="contextCard?.isCommander" class="context-menu-item" @click="increaseCommanderTax">
            Increase Commander Tax
          </div>
          <div class="context-menu-divider"></div>
          <div class="context-menu-item" @click="flipCard">Flip Card</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="tapCard">
            {{ contextCard.tapped ? 'Untap' : 'Tap' }}
          </div>
          <div class="context-menu-item" @click="addCounter">Add Counter</div>
          <div class="context-menu-item" @click="removeCounter">Remove Counter</div>
          <div class="context-menu-item" @click="setPowerToughness">Set Power/Toughness</div>
          <div class="context-menu-item" @click="createTokenCopy">Create Token Copy</div>
        </div>

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
    
    <div v-else class="loading">
      Loading...
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
      
      // Zone expansion states
      isZoneExpanded: {
        command: false,
        exile: false,
        graveyard: false
      },
      
      // Drag and drop
      draggedCard: null,
      draggedFromZone: null,
      draggedFromIndex: null,
      isDragging: false,
      dragStartPos: { x: 0, y: 0 },
      currentDragPos: { x: 0, y: 0 },
      
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
      mulliganCount: 0,

      // Miscellaneous
      contextMenuCloseHandler: null,
      isInitialized: false,

    }
  },
  computed: {
    actualLibraryCount() {
      return this.library.length; 
    },

    groupedHand() {
      const groups = [];
      const cardMap = new Map();
      
      this.hand.forEach(card => {
        const key = card.id || card.name;
        if (cardMap.has(key)) {
          cardMap.get(key).count++;
        } else {
          const group = { card, count: 1 };
          cardMap.set(key, group);
          groups.push(group);
        }
      });
      
      return groups;
    }
  },
  mounted() {
  console.log('PlaytestPopup mounted');
  this.isInitialized = true;
},

beforeUnmount() {
  console.log('PlaytestPopup unmounting');
  this.cleanup();
},

  methods: {
    closePopup() {
    this.cleanup();
    this.$emit('close');
  },

  selectAndLoadDeck(deckId) {
      console.log('Selecting deck:', deckId);
      this.selectedDeck = deckId;
      this.loadDeck();
    },
    
  loadDeck() {
  try {
    if (!this.selectedDeck) {
      console.error('No deck selected');
      return;
    }
    
    console.log('Loading deck:', this.selectedDeck);
    console.log('Available decks:', this.decks);
    
    const deck = this.decks.find(d => d.id === this.selectedDeck);
    if (!deck) {
      console.error('Selected deck not found:', this.selectedDeck);
      return;
    }
    
    console.log('Found deck:', deck.name);
    
    // Reset game state - create fresh arrays rather than clearing existing ones
    this.hand = [];
    this.library = [];
    this.graveyard = [];
    this.exileZone = [];
    this.battlefield = [];
    this.commandZone = [];
    this.commanderTax = 0;
    this.mulliganCount = 0;
    
    // Create a deep copy of the deck to avoid reference issues
    const deckCopy = JSON.parse(JSON.stringify(deck));
    
    // Process deck cards - handle quantities more efficiently
    if (deckCopy.cards && Array.isArray(deckCopy.cards)) {
      // Create a separate array for library cards to avoid manipulation during iteration
      const libraryCards = [];
      
      deckCopy.cards.forEach(card => {
        // Skip commander card if it exists in the main deck
        if (deckCopy.commander && card.id === deckCopy.commander.id) {
          return;
        }
        
        // Add copies based on count (or quantity for backward compatibility)
        const count = card.count || card.quantity || 1;
        for (let i = 0; i < count; i++) {
          // Create a unique instance of each card with a game ID
          libraryCards.push({
            ...card,
            gameId: `card-${card.id}-${i}-${Date.now()}`
          });
        }
      });
      
      // Assign the prepared cards to the library
      this.library = libraryCards;
    } else {
      console.error('Deck has no cards or cards is not an array:', deckCopy);
    }
    
    // Shuffle the deck
    this.shuffleDeck();
    
    // Load commander if it exists
    if (deckCopy.commander) {
      this.commandZone = [{
        ...deckCopy.commander,
        isCommander: true,
        gameId: `commander-${deckCopy.commander.id}-${Date.now()}`
      }];
    }
    
    // Draw initial hand
    this.drawInitialHand();
    this.phase = 'initialDraw';
    
    console.log('Deck loaded successfully', {
      librarySize: this.library.length,
      handSize: this.hand.length,
      hasCommander: this.commandZone.length > 0
    });
  } catch (error) {
    console.error('Error in loadDeck:', error);
  }
},
    
    shuffleDeck() {
      for (let i = this.library.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [this.library[i], this.library[j]] = [this.library[j], this.library[i]];
      }
    },
    
    drawInitialHand() {
      this.initialHand = [];
      this.selectedCards = [];
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
      
      // Return cards to library (excluding any that might be commander, though they shouldn't be here)
      cardsToMulligan.forEach(card => {
        if (!card.isCommander) {
          this.library.push(card);
        }
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
        if (!card.isCommander) { // Additional safety check
          if (this.phase === 'initialDraw') {
            this.initialHand.push(card);
          } else {
            this.hand.push(card);
          }
        }
      }
    },

    // Zone expansion methods
    toggleZoneExpansion(zone) {
      this.isZoneExpanded[zone] = !this.isZoneExpanded[zone];
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
  
  // Create a copy of the card first
  const cardToAdd = { ...this.draggedCard };

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
      // Library cards are not removed on drag and drop
      break;
  }

  // Handle tokens
  if (cardToAdd.isToken) {
    if (targetZone === 'hand' || targetZone === 'library') {
      // Tokens cease to exist when moved to hand or library
      this.draggedCard = null;
      return;
    }
  }

  // Add to target zone
  switch (targetZone) {
    case 'hand':
      this.hand.push(cardToAdd);
      break;
    case 'battlefield':
      // Ensure position exists
      if (!cardToAdd.position) {
        cardToAdd.position = { x: 0, y: 0 };
      }
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
    case 'library': {
      // Add to a random position in library
      const randomPos = Math.floor(Math.random() * (this.library.length + 1));
      this.library.splice(randomPos, 0, cardToAdd);
      break;
    }
  }
  
  this.draggedCard = null;
},
    
    // Battlefield card dragging
    startDrag(event, card, index) {
  if (event.button !== 0) return; // Only left mouse button
  
  this.isDragging = true;
  this.draggedCard = card;
  this.draggedFromZone = 'battlefield';
  this.draggedFromIndex = index;
  
  // Ensure the card has a position object
  if (!card.position) {
    card.position = { x: 0, y: 0 };
  }
  
  this.dragStartPos = {
    x: event.clientX - (card.position?.x || 0),
    y: event.clientY - (card.position?.y || 0)
  };
  
  document.addEventListener('mousemove', this.handleDrag);
  document.addEventListener('mouseup', this.stopDrag);
  
  event.preventDefault();
},
    
    handleDrag(event) {
  if (!this.isDragging || !this.draggedCard) return;
  
  // Throttle updates for performance
  if (this.dragThrottle) return;
  this.dragThrottle = true;
  
  requestAnimationFrame(() => {
    const newPosition = {
      x: event.clientX - this.dragStartPos.x,
      y: event.clientY - this.dragStartPos.y
    };
    
    // Make sure the card index is valid
    if (this.draggedFromIndex >= 0 && this.draggedFromIndex < this.battlefield.length) {
      // Ensure the card exists and has a position object
      if (!this.battlefield[this.draggedFromIndex].position) {
        this.battlefield[this.draggedFromIndex].position = { x: 0, y: 0 };
      }
      
      this.battlefield[this.draggedFromIndex].position = newPosition;
    }
    
    this.dragThrottle = false;
  });
},
    
    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.handleDrag);
      document.removeEventListener('mouseup', this.stopDrag);
    },
    
    // Context menu methods
    openCardMenu(event, card, zone, index) {
      event.preventDefault();
      this.contextCard = card;
      this.contextZone = zone;
      this.contextIndex = index;
      this.contextMenuPosition = {
        x: event.clientX,
        y: event.clientY
      };
      this.showContextMenu = true;
        
      // Remove previous handler if it exists
      if (this.contextMenuCloseHandler) {
        document.removeEventListener('click', this.contextMenuCloseHandler);
      }
      
      // Create new handler
      this.contextMenuCloseHandler = () => {
        this.showContextMenu = false;
      };
      
      document.addEventListener('click', this.contextMenuCloseHandler);
    },
    
    flipCard() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card) {
        card.flipped = !card.flipped;
      }
      this.showContextMenu = false;
    },
    
    tapCard() {
      if (!this.contextCard) return;
      
      const card = this.getCardFromZone();
      if (card && this.contextZone === 'battlefield') {
        card.tapped = !card.tapped;
      }
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
    
    moveToTopOfLibrary() {
      const card = this.getCardFromZone();
      if (card) {
        this.removeCardFromZone();
        this.library.unshift(card);
      }
      this.showContextMenu = false;
    },
    
    moveToBottomOfLibrary() {
      const card = this.getCardFromZone();
      if (card) {
        this.removeCardFromZone();
        this.library.push(card);
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
    
    removeCardFromZone() {
      switch (this.contextZone) {
        case 'hand': 
          this.hand.splice(this.contextIndex, 1);
          break;
        case 'battlefield': 
          this.battlefield.splice(this.contextIndex, 1);
          break;
        case 'graveyard': 
          this.graveyard.splice(this.contextIndex, 1);
          break;
        case 'exile': 
          this.exileZone.splice(this.contextIndex, 1);
          break;
        case 'command': 
          this.commandZone.splice(this.contextIndex, 1);
          break;
      }
    },

    moveToZone(targetZone) {
      const card = this.getCardFromZone();
      if (!card) return;

      this.removeCardFromZone();

      switch (targetZone) {
        case 'battlefield':
          card.position = { x: 0, y: 0 }; // Reset position when moving to battlefield
          this.battlefield.push(card);
          break;
        case 'hand':
          this.hand.push(card);
          break;
        case 'graveyard':
          this.graveyard.push(card);
          break;
        case 'exile':
          this.exileZone.push(card);
          break;
        case 'command':
          this.commandZone.push(card);
          break;
      }
      
      this.showContextMenu = false;
    },
    
    moveToBattlefield() {
      this.moveToZone('battlefield');
    },
    
    increaseCommanderTax() {
      this.commanderTax += 2;
      this.showContextMenu = false;
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
          counters: 0,
          position: { x: 0, y: 0 }
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

    cleanup() {
    console.log('Cleaning up PlaytestPopup');
    // Clear any timers
    if (this.loadingTimer) clearTimeout(this.loadingTimer);
    
    // Release references that might cause memory leaks
    this.hand = [];
    this.library = [];
    this.graveyard = [];
    this.exileZone = [];
    this.battlefield = [];
    this.commandZone = [];
    this.selectedDeck = null;
  },
    // Helper methods
    getCardImage(card) {
      if (!card) return require('@/assets/cards/mtg-card-back.jpg');
      if (card.flipped && card.card_faces && card.card_faces[1]) {
        return card.card_faces[1].image_uris?.normal || require('@/assets/cards/mtg-card-back.jpg');
      }
      return card.image_uris?.normal || 
             (card.card_faces ? card.card_faces[0].image_uris?.normal : require('@/assets/cards/mtg-card-back.jpg'));
    }
  }
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

.deck-selection {
  background-color: #2c3e50;
  padding: 2rem;
  border-radius: 10px;
  text-align: center;
  width: 400px;
  max-width: 90%;
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
  width: 90%;
  max-width: 800px;
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
  width: 95%;
  height: 95%;
  background-color: #2c3e50;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: auto;
}

.top-row {
  display: flex;
  gap: 1rem;
}

.command-zone, .exile-zone {
  flex: 1;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 5px;
  min-height: 200px;
  cursor: pointer;
}

.quantity-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.7rem;
  font-weight: bold;
}

.zone-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 0.5rem;
}

.expanded-zone {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #2c3e50;
  padding: 1rem;
  border-radius: 10px;
  z-index: 1002;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
}

.expanded-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.collapse-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.more-cards-indicator {
  background-color: rgba(0, 0, 0, 0.5);
  padding: 0.3rem 0.6rem;
  border-radius: 3px;
  font-size: 0.9rem;
}

.battlefield {
  flex: 1;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 5px;
  min-height: 300px;
  position: relative;
}

.battlefield-cards {
  position: relative;
  height: 100%;
  min-height: 250px;
}

.battlefield-card {
  position: absolute;
  cursor: move;
  transition: transform 0.1s;
}

.battlefield-card:hover {
  z-index: 10;
}

.hand-zone {
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

.bottom-row {
  display: flex;
  gap: 1rem;
}

.library, .graveyard {
  flex: 1;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 5px;
  text-align: center;
  min-height: 200px;
}

.library-image {
  width: 150px;
  height: auto;
  cursor: pointer;
  margin: 0.5rem auto;
  display: block;
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

.empty-zone-message {
  color: #7f8c8d;
  font-style: italic;
  margin-top: 1rem;
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
  text-align: center;
}

.search-result-card:hover {
  transform: scale(1.05);
}

.search-card-image {
  width: 100%;
  height: auto;
  border-radius: 5px;
}
</style>