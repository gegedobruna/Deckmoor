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
        <div class="initial-draw-hand-container">
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
          <button @click="drawCard" class="action-button draw">Draw</button> </div>
      </div>

      <div v-if="phase === 'playtest'" class="playtest-interface">
        <div class="top-row">
          <div class="command-zone" @drop="dropCard($event, 'command')" @dragover.prevent @click="!isZoneExpanded.command && toggleZoneExpansion('command')">
            <h3>Command Zone</h3>
            <div v-if="!isZoneExpanded.command" class="zone-preview">
              <div v-if="commandZone.length > 0">
                <div v-for="(card, index) in commandZone" :key="'command-preview-' + index" class="card-wrapper">
                  <img :src="getCardImage(card)"
                       :alt="card.name"
                       class="card-image small" draggable="true"
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
            </div>
            <div v-if="isZoneExpanded.command" class="expanded-zone command-expanded">
              <div class="expanded-cards">
                <div v-for="(card, index) in commandZone" :key="'command-expanded-' + index" class="card-wrapper">
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
                <div v-if="commandZone.length === 0" class="empty-zone-message">
                   Command zone is empty.
                </div>
              </div>
              <button @click.stop="toggleZoneExpansion('command')" class="collapse-button">Collapse</button>
            </div>
          </div>

          <div class="graveyard" @drop="dropCard($event, 'graveyard')" @dragover.prevent @click="!isZoneExpanded.graveyard && toggleZoneExpansion('graveyard')">
            <h3>Graveyard ({{ graveyard.length }})</h3>
            <div v-if="!isZoneExpanded.graveyard" class="zone-preview">
              <div v-for="(card, index) in graveyard.slice(0, 3)" :key="'graveyard-preview-' + index" class="card-wrapper">
                <img :src="getCardImage(card)"
                     :alt="card.name"
                     class="card-image small" draggable="true"
                     @dragstart="dragStart($event, card, 'graveyard', index)"
                     @contextmenu.prevent="openCardMenu($event, card, 'graveyard', index)">
              </div>
              <div v-if="graveyard.length > 3" class="more-cards-indicator">
                +{{ graveyard.length - 3 }} more
              </div>
              <div v-if="graveyard.length === 0" class="empty-zone-message">
                 Graveyard is empty.
              </div>
            </div>
            <div v-if="isZoneExpanded.graveyard" class="expanded-zone graveyard-expanded">
              <div class="expanded-cards">
                <div v-for="(card, index) in graveyard" :key="'graveyard-expanded-' + index" class="card-wrapper">
                  <img :src="getCardImage(card)"
                       :alt="card.name"
                       class="card-image"
                       draggable="true"
                       @dragstart="dragStart($event, card, 'graveyard', index)"
                       @contextmenu.prevent="openCardMenu($event, card, 'graveyard', index)">
                </div>
                 <div v-if="graveyard.length === 0" class="empty-zone-message">
                   Graveyard is empty.
                </div>
              </div>
              <button @click.stop="toggleZoneExpansion('graveyard')" class="collapse-button">Collapse</button>
            </div>
          </div>

          <div class="exile-zone" @drop="dropCard($event, 'exile')" @dragover.prevent @click="!isZoneExpanded.exile && toggleZoneExpansion('exile')">
             <h3>Exile ({{ exileZone.length }})</h3>
             <div v-if="!isZoneExpanded.exile" class="zone-preview">
               <div v-for="(card, index) in exileZone.slice(0, 3)" :key="'exile-preview-' + index" class="card-wrapper">
                 <img :src="getCardImage(card)"
                      :alt="card.name"
                      class="card-image small" draggable="true"
                      @dragstart="dragStart($event, card, 'exile', index)"
                      @contextmenu.prevent="openCardMenu($event, card, 'exile', index)">
               </div>
               <div v-if="exileZone.length > 3" class="more-cards-indicator">
                 +{{ exileZone.length - 3 }} more
               </div>
               <div v-if="exileZone.length === 0" class="empty-zone-message">
                 Exile is empty.
               </div>
             </div>
             <div v-if="isZoneExpanded.exile" class="expanded-zone exile-expanded">
               <div class="expanded-cards">
                 <div v-for="(card, index) in exileZone" :key="'exile-expanded-' + index" class="card-wrapper">
                   <img :src="getCardImage(card)"
                        :alt="card.name"
                        class="card-image"
                        draggable="true"
                        @dragstart="dragStart($event, card, 'exile', index)"
                        @contextmenu.prevent="openCardMenu($event, card, 'exile', index)">
                 </div>
                  <div v-if="exileZone.length === 0" class="empty-zone-message">
                    Exile is empty.
                  </div>
               </div>
               <button @click.stop="toggleZoneExpansion('exile')" class="collapse-button">Collapse</button>
             </div>
           </div>
        </div>

        <div class="battlefield" @drop="dropCard($event, 'battlefield')" @dragover.prevent>
          <h3>Battlefield</h3>
          <div class="battlefield-cards">
            <div v-for="(card, index) in battlefield" :key="'battlefield-' + (card.gameId || index)" class="battlefield-card"
                 :style="{
                   transform: card.tapped ? 'rotate(90deg)' : 'none', // Rotate if tapped
                   left: card.position?.x + 'px', // Position based on drag/drop
                   top: card.position?.y + 'px',
                   position: 'absolute' // Absolute positioning for dragging
                 }"
                 @mousedown="startDrag($event, card, index)"
                 @mouseup="stopDrag"
                 @mousemove="throttledHandleDrag($event)">
              <img :src="getCardImage(card)"
                   :alt="card.name"
                   class="card-image"
                   draggable="true" @dragstart="dragStart($event, card, 'battlefield', index)"
                   @contextmenu.prevent="openCardMenu($event, card, 'battlefield', index)">
              <div v-if="card.counters > 0" class="counter-badge">
                {{ card.counters }}
              </div>
              <div v-if="card.power !== undefined || card.toughness !== undefined" class="pt-indicator">
                {{ card.power ?? '?' }}/{{ card.toughness ?? '?' }}
              </div>
            </div>
          </div>
          <button @click="addToken" class="token-button">Add Token</button>
        </div>

        <div class="bottom-row">
          <div class="library" @drop="dropCard($event, 'library')" @dragover.prevent>
            <h3>Library ({{ library.length }})</h3>
            <img :src="defaultCardBack"
                 alt="Library"
                 class="library-image"
                 @click="searchLibrary"
                 draggable="false">
            <button @click="drawCard" class="draw-button">Draw</button>
          </div>
          <div class="hand-zone" @drop="dropCard($event, 'hand')" @dragover.prevent>
            <h3>Hand ({{ hand.length }})</h3>
            <div class="hand-cards">
              <div v-for="(cardGroup, index) in groupedHand" :key="'hand-' + (cardGroup.card.gameId || index)" class="card-wrapper">
                <img :src="getCardImage(cardGroup.card)"
                     :alt="cardGroup.card.name"
                     class="card-image"
                     draggable="true"
                     @dragstart="dragStart($event, cardGroup.card, 'hand', findCardIndexInHand(cardGroup.card))" @contextmenu.prevent="openCardMenu($event, cardGroup.card, 'hand', findCardIndexInHand(cardGroup.card))">
                <div v-if="cardGroup.count > 1" class="quantity-badge">
                  {{ cardGroup.count }}
                </div>
              </div>
               <div v-if="hand.length === 0" class="empty-zone-message">
                 Hand is empty.
               </div>
            </div>
          </div>
        </div>

        <div v-if="showContextMenu && contextCard"
             class="context-menu"
             :style="{ top: contextMenuPosition.y + 'px', left: contextMenuPosition.x + 'px' }"
             @click.stop>
          <div v-if="contextZone !== 'battlefield'" class="context-menu-item" @click="moveToZone('battlefield')">Move to Battlefield</div>
          <div v-if="contextZone !== 'exile'" class="context-menu-item" @click="moveToZone('exile')">Move to Exile</div>
          <div v-if="contextZone !== 'graveyard'" class="context-menu-item" @click="moveToZone('graveyard')">Move to Graveyard</div>
          <div v-if="contextZone !== 'command' && !contextCard?.isToken" class="context-menu-item" @click="moveToZone('command')">Move to Command Zone</div>
          <div v-if="contextZone !== 'hand' && !contextCard?.isToken" class="context-menu-item" @click="moveToZone('hand')">Move to Hand</div>
          <div v-if="contextZone !== 'library' && !contextCard?.isToken" class="context-menu-item" @click="moveToTopOfLibrary">Put on Top of Library</div>
          <div v-if="contextZone !== 'library' && !contextCard?.isToken" class="context-menu-item" @click="moveToBottomOfLibrary">Put on Bottom of Library</div>
          <div v-if="contextCard?.isCommander" class="context-menu-item" @click="increaseCommanderTax">Increase Commander Tax (+2)</div>
          <div class="context-menu-divider"></div>
          <div v-if="contextCard?.card_faces?.length > 1" class="context-menu-item" @click="flipCard">Flip Card</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="tapCard">{{ contextCard.tapped ? 'Untap' : 'Tap' }}</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="addCounter">Add Counter</div>
          <div v-if="contextZone === 'battlefield' && contextCard?.counters > 0" class="context-menu-item" @click="removeCounter">Remove Counter</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="setPowerToughness">Set Power/Toughness</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="createTokenCopy">Create Token Copy</div>
        </div>

        <div v-if="showTokenModal" class="modal-overlay" @click="cancelTokenCreation">
          <div class="modal-content token-modal" @click.stop>
            <h3>Create Token</h3>
            <div class="token-form">
              <label> Token Name: <input v-model="tokenName" type="text" placeholder="E.g., Soldier, Goblin"> </label>
              <label> Quantity: <input v-model.number="tokenQuantity" type="number" min="1" max="100"> </label>
              <label> Image URL (optional): <input v-model="tokenImageUrl" type="text" placeholder="Paste image URL"> </label>
              <div class="modal-buttons token-modal-buttons">
                <button @click="createToken" class="confirm-button">Create</button>
                <button @click="cancelTokenCreation" class="cancel-button">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showPTModal" class="modal-overlay" @click="cancelPT">
          <div class="modal-content pt-modal" @click.stop>
            <h3>Set Power/Toughness for {{ contextCard?.name }}</h3>
            <div class="pt-form">
              <label> Power: <input v-model.number="newPower" type="number"> </label>
              <label> Toughness: <input v-model.number="newToughness" type="number"> </label>
              <div class="modal-buttons pt-modal-buttons">
                <button @click="savePT" class="confirm-button">Save</button>
                <button @click="cancelPT" class="cancel-button">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showLibrarySearch" class="modal-overlay" @click="closeLibrarySearch">
          <div class="modal-content library-search-modal" @click.stop>
            <h3>Search Library ({{ library.length }} cards)</h3>
            <input v-model="librarySearchQuery"
                   type="text"
                   placeholder="Search for a card..."
                   @input="searchLibraryCards"
                   class="library-search-input">
            <div class="search-results">
              <div v-for="card in librarySearchResults"
                   :key="'search-' + (card.gameId || card.id)" class="search-result-card"
                   @click="moveSearchedCardToHand(card)">
                 <img :src="getCardImage(card)"
                     :alt="card.name"
                     class="search-card-image">
                 <span>{{ card.name }}</span>
              </div>
               <div v-if="librarySearchResults.length === 0 && librarySearchQuery" class="empty-zone-message">
                 No matching cards found.
               </div>
               <div v-if="librarySearchResults.length === 0 && !librarySearchQuery && library.length > 0" class="empty-zone-message">
                 Library contains {{ library.length }} cards.
               </div>
               <div v-if="library.length === 0" class="empty-zone-message">
                 Library is empty.
               </div>
            </div>
            <div class="modal-buttons library-search-buttons">
              <button @click="shuffleLibrary" class="action-button mulligan">Shuffle Library</button> <button @click="closeLibrarySearch" class="cancel-button">Close</button>
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
// Simple throttle function to limit how often a function can be called
// Useful for events that fire rapidly, like mousemove
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  }
}

export default {
  name: 'PlaytestPopup',
  props: {
    decks: {
      type: Array,
      default: () => [], 
    },
  },
  data() {
    return {
      // --- Core State ---
      selectedDeckId: null, // ID of the deck chosen for playtesting
      phase: 'select', // Current phase: 'select', 'initialDraw', 'playtest', 'loading'
      loading: true, // Indicates if decks are still loading
      isInitialized: false, // Flag to ensure component is ready before rendering main content

      // --- Game State Zones ---
      library: [],
      initialHand: [], // Stores the hand during the initial draw/mulligan phase
      hand: [],
      battlefield: [],
      graveyard: [],
      exileZone: [],
      commandZone: [],

      // --- UI State ---
      selectedCards: [], // Indices of cards selected for mulligan
      isZoneExpanded: {
        command: false,
        exile: false,
        graveyard: false,
      },

      // --- Drag and Drop State ---
      draggedCard: null, 
      draggedFromZone: null, 
      draggedFromIndex: null, 
      isDraggingBattlefieldCard: false, 
      draggedBattlefieldCardIndex: -1, 
      dragStartOffset: { x: 0, y: 0 },
      throttledHandleDrag: null, 

      // --- Context Menu State ---
      showContextMenu: false, 
      contextMenuPosition: { x: 0, y: 0 }, 
      contextCard: null, 
      contextZone: null, 
      contextIndex: null, 
      contextMenuCloseHandler: null,

      // --- Modal States ---
      showTokenModal: false, 
      tokenName: '', 
      tokenQuantity: 1, // Input field for token quantity
      tokenImageUrl: '', // Input field for optional token image URL
      showPTModal: false, // Visibility of the power/toughness setting modal
      newPower: 0, // Input for new power
      newToughness: 0, // Input for new toughness
      showLibrarySearch: false, // Visibility of the library search modal
      librarySearchQuery: '', // Input field for searching the library
      librarySearchResults: [], // Array of cards matching the library search

      // --- Game Logic State ---
      commanderTax: 0, // Tracks additional cost for casting the commander
      mulliganCount: 0, // How many times the player has mulliganed

      // --- Internal State / Assets ---
      // Define default images (using dynamic import URLs for Vite/modern build tools)
      // Note: For older setups (like Webpack 4), you might need `require()`
      defaultCardBack: new URL('@/assets/cards/mtg-card-back.jpg', import.meta.url).href,
      defaultTokenImage: new URL('@/assets/cards/mtg-token-default.jpg', import.meta.url).href,
    };
  },
  computed: {
    // Groups cards in the hand by their ID or name for display
    // Shows a quantity badge instead of duplicate card images
    groupedHand() {
      const groups = [];
      const cardMap = new Map(); // Use a Map for efficient lookup
      this.hand.forEach(card => {
        // Use gameId first, fallback to id or name as the key
        const key = card.gameId || card.id || card.name;
        if (cardMap.has(key)) {
          // If card already seen, increment its count
          cardMap.get(key).count++;
        } else {
          // If it's a new card, create a group for it
          const group = { card: card, count: 1 };
          cardMap.set(key, group);
          groups.push(group);
        }
      });
      return groups;
    },
  },
  created() {
    // Create a throttled version of the handleDrag method on component creation
    // Throttle to roughly 60fps (1000ms / 60 = ~16.6ms)
    this.throttledHandleDrag = throttle(this.handleDrag, 16);
  },
  mounted() {
    // Runs after the component's template has been rendered to the DOM
    console.log('PlaytestPopup mounted');
    // Use $nextTick to ensure the DOM is updated before setting isInitialized
    this.$nextTick(() => {
        this.isInitialized = true;
        this.loading = false; // Assuming decks are passed as props and available now
    });
    // Set up a global click listener to close the context menu if clicked outside
    this.contextMenuCloseHandler = (event) => {
      // Check if the menu is open and the click was not inside the menu itself
      if (this.showContextMenu && !event.target.closest('.context-menu')) {
        this.closeContextMenu();
      }
    };
    document.addEventListener('click', this.contextMenuCloseHandler);
  },
  beforeUnmount() {
    // Runs right before the component is destroyed
    console.log('PlaytestPopup unmounting');
    // Clean up global event listeners to prevent memory leaks
    document.removeEventListener('click', this.contextMenuCloseHandler);
    document.removeEventListener('mousemove', this.throttledHandleDrag);
    document.removeEventListener('mouseup', this.stopDrag);
    // Reset component state
    this.cleanup();
  },
  methods: {
    // --- Component Lifecycle & Setup ---

    // Closes the popup and resets state
    closePopup() {
      this.cleanup(); // Reset internal state
      this.$emit('close'); // Notify parent component
    },

    // Resets all game state and UI flags to initial values
    cleanup() {
      console.log('Cleaning up PlaytestPopup state');
      this.library = [];
      this.initialHand = [];
      this.hand = [];
      this.battlefield = [];
      this.graveyard = [];
      this.exileZone = [];
      this.commandZone = [];
      this.selectedCards = [];
      this.selectedDeckId = null;
      this.phase = 'select';
      this.commanderTax = 0;
      this.mulliganCount = 0;
      this.closeContextMenu();
      this.showTokenModal = false;
      this.showPTModal = false;
      this.showLibrarySearch = false;
      // Reset zone expansion states
      this.isZoneExpanded = { command: false, exile: false, graveyard: false };
      // Reset drag state
      this.isDraggingBattlefieldCard = false;
      this.draggedBattlefieldCardIndex = -1;
      this.draggedCard = null;
      this.draggedFromZone = null;
      this.draggedFromIndex = null;
    },

    // Called when a deck option is clicked
    selectAndLoadDeck(deckId) {
      this.selectedDeckId = deckId;
      this.loadDeck(); // Proceed to load the selected deck
    },

    // Loads the deck data, populates zones, shuffles, and draws initial hand
    loadDeck() {
      try {
        if (!this.selectedDeckId) { console.error('No deck selected'); return; }
        // Find the deck data from the props based on the selected ID
        const deck = this.decks.find(d => d.id === this.selectedDeckId);
        if (!deck) { console.error('Selected deck not found:', this.selectedDeckId); return; }
        console.log('Loading deck:', deck.name);
        this.cleanup(); // Reset state before loading new deck
        this.phase = 'loading'; // Show loading indicator (optional)

        // Deep copy the deck data to avoid modifying the original prop
        const deckData = JSON.parse(JSON.stringify(deck));
        const libraryCards = [];

        // Populate the library, excluding the commander
        if (deckData.cards && Array.isArray(deckData.cards)) {
          deckData.cards.forEach((cardData, cardIndex) => {
            // Skip if this card is the commander
            if (deckData.commander && cardData.id === deckData.commander.id) return;
            const count = cardData.count || cardData.quantity || 1; // Handle different quantity properties
            // Add each copy of the card to the library
            for (let i = 0; i < count; i++) {
              // Add a unique gameId and default properties for playtest state
              libraryCards.push({
                ...cardData,
                gameId: `card-${cardData.id}-${cardIndex}-${i}-${Date.now()}`,
                tapped: false,
                flipped: false,
                counters: 0,
                position: null,
                power: cardData.power, // Keep original P/T if available
                toughness: cardData.toughness,
              });
            }
          });
          this.library = libraryCards;
        } else { console.warn('Deck has no cards or cards is not an array:', deckData); this.library = []; }

        // Set up the command zone
        if (deckData.commander) {
          // Add commander-specific properties
          this.commandZone = [{
            ...deckData.commander,
            isCommander: true,
            gameId: `commander-${deckData.commander.id}-${Date.now()}`,
            tapped: false,
            flipped: false,
            counters: 0,
            position: null,
            power: deckData.commander.power,
            toughness: deckData.commander.toughness,
          }];
        } else { this.commandZone = []; }

        // Prepare for the game start
        this.shuffleDeck();
        this.drawInitialHand();
        this.phase = 'initialDraw'; // Move to the initial hand phase
        console.log('Deck loaded:', { library: this.library.length, hand: this.initialHand.length, commander: this.commandZone.length });
      } catch (error) {
        console.error('Error in loadDeck:', error);
        this.phase = 'select'; // Go back to selection on error
      }
    },

    // --- Initial Draw and Mulligan ---

    // Draws the starting hand (usually 7 cards)
    drawInitialHand() {
      this.initialHand = [];
      this.selectedCards = []; // Clear any mulligan selections
      const handSize = 7;
      for (let i = 0; i < handSize; i++) {
        if (this.library.length > 0) {
          this.initialHand.push(this.library.pop()); // Take card from the top (end) of the library array
        }
        else { console.warn("Library empty during initial draw"); break; }
      }
    },

    // Toggles selection of a card in the initial hand for mulligan
    toggleCardSelect(index) {
      const idx = this.selectedCards.indexOf(index);
      if (idx === -1) {
        // If not selected, add it
        this.selectedCards.push(index);
      } else {
        // If already selected, remove it
        this.selectedCards.splice(idx, 1);
      }
    },

    // Finalizes the hand and starts the playtest phase
    keepHand() {
      this.hand = [...this.initialHand]; // Move cards from initialHand to the actual hand
      this.initialHand = []; // Clear the temporary initial hand
      this.phase = 'playtest'; // Start the game!
    },

    // Handles the mulligan process (simplified)
    mulligan() {
        this.mulliganCount++; // Track mulligans
        const newHandSize = 7; // Draw 7 cards again (standard mulligan)
        // Simplified: Just draw 7, user decides what to keep/bottom later if needed
        // More complex logic could be added for specific mulligan rules (London, Vancouver)

        // Put the current hand back into the library
        this.library.push(...this.initialHand);
        this.initialHand = [];
        this.shuffleDeck(); // Reshuffle

        // Draw a new hand of 7 cards
        for (let i = 0; i < newHandSize; i++) {
            if (this.library.length > 0) {
                this.initialHand.push(this.library.pop());
            }
            else { console.warn("Library empty during mulligan draw"); break; }
        }

        // Inform the user about the mulligan outcome
        alert(`Mulligan ${this.mulliganCount}. Drawn ${this.initialHand.length} cards. You may need to place ${this.mulliganCount} card(s) on the bottom (manual action).`);
        // Stay in the initialDraw phase
        this.phase = 'initialDraw';
        this.selectedCards = []; // Reset selections for the new hand
    },

    // --- Core Gameplay Actions ---

    // Draws a single card from the library to the hand (or initial hand if applicable)
    drawCard() {
      if (this.library.length > 0) {
        const drawnCard = this.library.pop(); // Get top card
        if (this.phase === 'initialDraw') {
           // If still in mulligan phase, add to initial hand
           this.initialHand.push(drawnCard);
        } else if (this.phase === 'playtest') {
           // Otherwise, add to the main hand
           this.hand.push(drawnCard);
        }
      } else {
        console.warn('Cannot draw, library is empty!'); // Prevent drawing from empty library
      }
    },

    // Shuffles the library array using the Fisher-Yates algorithm
    shuffleDeck() {
      // Standard Fisher-Yates shuffle
      for (let i = this.library.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [this.library[i], this.library[j]] = [this.library[j], this.library[i]]; // Swap elements
      }
      console.log('Deck shuffled successfully.');
    },

    // Shuffles the library during playtest (e.g., after searching)
    shuffleLibrary() {
        console.log('Attempting to shuffle library...');
        this.shuffleDeck(); // Reuse the main shuffle logic
        // Refresh the search results if the library search modal is open
        if (this.showLibrarySearch) {
            this.searchLibraryCards();
        }
        // ** Pop-up removed as requested **
    },

    // Increases the commander tax
    increaseCommanderTax() {
      this.commanderTax += 2; // Standard tax increase
      console.log(`Commander tax increased to ${this.commanderTax}`);
      this.closeContextMenu(); // Close menu if called from there
    },

    // --- Zone Management ---

    // Toggles the expanded state of Command, Exile, or Graveyard zones
    toggleZoneExpansion(zone) {
      // Only allow one expanded zone at a time (optional, but common UI pattern)
      Object.keys(this.isZoneExpanded).forEach(key => {
          if (key !== zone) {
              this.isZoneExpanded[key] = false;
          }
      });
      // Toggle the target zone
      this.isZoneExpanded[zone] = !this.isZoneExpanded[zone];
      console.log(`Toggled ${zone} expansion to:`, this.isZoneExpanded[zone]);
    },

    // Removes a card from a specific zone at a given index
    removeCardFromZone(zoneName, index) {
        const zoneArray = this.getZoneArray(zoneName);
        if (!zoneArray || index < 0 || index >= zoneArray.length) {
            console.error(`Cannot remove card from ${zoneName} at invalid index ${index}`);
            return null;
        }
        // Use splice to remove the card and return the removed card object
        return zoneArray.splice(index, 1)[0];
    },

    // --- Drag and Drop ---

    // Initiates dragging a card from any zone (except battlefield cards handled separately by mouse events)
    dragStart(event, card, zone, index) {
        console.log(`Drag Start: ${card.name} from ${zone}[${index}]`);
        // Store card identifier, source zone, and index in dataTransfer
        // Using gameId for uniqueness, falling back to id
        event.dataTransfer.setData('text/plain', JSON.stringify({ cardId: card.gameId || card.id, zone, index }));
        event.dataTransfer.effectAllowed = 'move'; // Indicate the type of operation
        // Keep track of the dragged card details locally
        this.draggedCard = card;
        this.draggedFromZone = zone;
        this.draggedFromIndex = index;
    },

    // Handles dropping a card onto a target zone (from non-battlefield source)
    dropCard(event, targetZone) {
        event.preventDefault(); // Prevent default browser behavior
        console.log(`Drop on: ${targetZone}`);
        try {
            // Retrieve the data stored during dragStart
            const data = JSON.parse(event.dataTransfer.getData('text/plain'));
            const { cardId, zone: sourceZone, index: sourceIndex } = data;
            console.log(`Dropped card ID: ${cardId} from ${sourceZone}[${sourceIndex}] to ${targetZone}`);

            let cardToMove;
            let actualSourceIndex = -1; // The actual index might differ if the array changed

            // Get the array representing the source zone
            const sourceArray = this.getZoneArray(sourceZone);
            if (!sourceArray) { console.error("Invalid source zone:", sourceZone); return; }

            // Find the card in the source array using its unique ID
            actualSourceIndex = sourceArray.findIndex(c => (c.gameId || c.id) === cardId);

            if (actualSourceIndex === -1) {
                console.error(`Card ${cardId} not found in source zone ${sourceZone}.`);
                return; // Can't find the card
            }

            // Remove the card from the source array
            cardToMove = sourceArray.splice(actualSourceIndex, 1)[0];
            if (!cardToMove) { console.error("Failed to extract card from source zone."); return; }

            // Handle tokens ceasing to exist when moved off the battlefield (mostly)
            if (cardToMove.isToken && sourceZone === 'battlefield') {
                if (targetZone === 'hand' || targetZone === 'library' || targetZone === 'graveyard' || targetZone === 'exile') {
                    console.log(`Token ${cardToMove.name} removed (moved to ${targetZone})`);
                    this.draggedCard = null; return; // Don't add the token to the target zone
                }
            }

            // Get the array representing the target zone
            const targetArray = this.getZoneArray(targetZone);
            if (!targetArray) {
                // Invalid target, put the card back in the source zone
                console.error("Invalid target zone:", targetZone); sourceArray.splice(actualSourceIndex, 0, cardToMove); return;
            }

            // Reset card state when moving zones (untap, clear position)
            cardToMove.tapped = false;
            cardToMove.position = null; // Clear absolute position

            // Add the card to the target array
            if (targetZone === 'battlefield') {
                // Calculate position relative to the battlefield drop area
                const battlefieldRect = event.currentTarget.getBoundingClientRect();
                cardToMove.position = {
                    x: event.clientX - battlefieldRect.left,
                    y: event.clientY - battlefieldRect.top,
                };
                targetArray.push(cardToMove);
            } else if (targetZone === 'library') {
                // Add to the top of the library (beginning of the array)
                targetArray.unshift(cardToMove);
            } else {
                // Add to the end for hand, graveyard, exile, command zone
                targetArray.push(cardToMove);
            }

            console.log(`Moved ${cardToMove.name} to ${targetZone}`);
        } catch (e) { console.error("Error processing drop event:", e); }
        finally {
             // Clean up drag state regardless of success or error
             this.draggedCard = null;
             this.draggedFromZone = null;
             this.draggedFromIndex = null;
        }
    },

    // --- Battlefield Card Dragging (Mouse Events) ---

    // Starts dragging a card *within* the battlefield using mouse events
    startDrag(event, card, index) {
        // Only react to left mouse button clicks
        if (event.button !== 0) return;
        // Ensure we are clicking directly on a battlefield card element
        if (!event.target.closest('.battlefield-card')) return;

        console.log(`Battlefield Drag Start: ${card.name}`);
        this.isDraggingBattlefieldCard = true; // Set the specific flag
        this.draggedBattlefieldCardIndex = index; // Store the index

        // Initialize position if it doesn't exist (e.g., first drag)
        if (!card.position) {
            const battlefieldCardsRect = this.$el.querySelector('.battlefield-cards').getBoundingClientRect();
            // Default to somewhere near the top-left of the drop zone
            card.position = { x: 50, y: 50 };
        }

        // Calculate the offset between the mouse click and the top-left corner of the card
        const cardRect = event.target.closest('.battlefield-card').getBoundingClientRect();
        this.dragStartOffset = { x: event.clientX - cardRect.left, y: event.clientY - cardRect.top };

        // Add listeners to the document to track mouse movement and release
        document.addEventListener('mousemove', this.throttledHandleDrag);
        document.addEventListener('mouseup', this.stopDrag);
        event.preventDefault(); // Prevent default text selection or other drag behaviors
    },

    // Handles mouse movement while dragging a battlefield card (throttled)
    handleDrag(event) {
        // Only proceed if we are currently dragging a battlefield card
        if (!this.isDraggingBattlefieldCard || this.draggedBattlefieldCardIndex < 0) return;
        const card = this.battlefield[this.draggedBattlefieldCardIndex]; if (!card) return; // Safety check

        // Get the dimensions of the battlefield container (where cards are placed)
        const battlefieldCardsRect = this.$el.querySelector('.battlefield-cards').getBoundingClientRect();

        // Calculate the new position based on mouse coordinates, container offset, and initial click offset
        const newX = event.clientX - battlefieldCardsRect.left - this.dragStartOffset.x;
        const newY = event.clientY - battlefieldCardsRect.top - this.dragStartOffset.y;

        // Update the card's position state (Vue reactivity handles the visual update)
        // No need to clamp here, but could add if needed
        card.position = { x: newX, y: newY };
    },

    // Stops dragging a battlefield card on mouse release
    stopDrag() {
        if (this.isDraggingBattlefieldCard) {
            console.log(`Battlefield Drag End: ${this.battlefield[this.draggedBattlefieldCardIndex]?.name}`);
            // Reset battlefield drag state
            this.isDraggingBattlefieldCard = false;
            this.draggedBattlefieldCardIndex = -1;
            // Remove the global listeners
            document.removeEventListener('mousemove', this.throttledHandleDrag);
            document.removeEventListener('mouseup', this.stopDrag);
        }
    },

    // --- Context Menu ---

    // Opens the right-click context menu for a card
    openCardMenu(event, card, zone, index) {
      event.preventDefault(); // Prevent the default browser context menu
      event.stopPropagation(); // Prevent the click from closing the menu immediately

      let actualIndex = index; // The provided index might be visual (e.g., graveyard preview)
      const zoneArray = this.getZoneArray(zone);
      if (!zoneArray) { console.error(`Invalid zone ${zone} for context menu`); return; }

      // Special handling for grouped hand - find the actual index in the ungrouped hand array
      if (zone === 'hand') {
        actualIndex = this.findCardIndexInHand(card);
      } else {
          // For other zones, verify the index and card match, or find the correct index
          // Check if the provided index is valid and points to the correct card
          if (index >= zoneArray.length || (zoneArray[index].gameId || zoneArray[index].id) !== (card.gameId || card.id)) {
              // If not, search the zone array for the card's actual index
              actualIndex = zoneArray.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
          }
      }

      // If we couldn't find the card's real index, bail out
      if (actualIndex === -1) {
          console.error(`Context menu card ${card.name} not found in ${zone}`); return;
      }

      // Store context details
      this.contextCard = card;
      this.contextZone = zone;
      this.contextIndex = actualIndex; // Store the *actual* index
      // Position the menu near the click event coordinates
      this.contextMenuPosition = { x: event.clientX + 5, y: event.clientY + 5 };
      this.showContextMenu = true; // Make the menu visible
      console.log(`Context menu opened for ${card.name} in ${zone}[${actualIndex}]`);
    },

    // Closes the context menu and resets its state
    closeContextMenu() {
      this.showContextMenu = false;
      this.contextCard = null;
      this.contextZone = null;
      this.contextIndex = null;
    },

    // --- Context Menu Actions ---

    // The core logic for moving a card via the context menu
    moveCardFromContext(targetZone, libraryPosition = 'top') {
      const card = this.getCardFromContext(); // Get the card details from context state
      if (!card) {
        console.error("Cannot move card, context invalid."); this.closeContextMenu(); return;
      }

      const sourceZone = this.contextZone; // Get source zone from context
      const sourceIndex = this.contextIndex; // Get source index from context

      // Handle tokens moving off the battlefield (same logic as dropCard)
      if (card.isToken && sourceZone === 'battlefield') {
        if (targetZone === 'hand' || targetZone === 'library' || targetZone === 'graveyard' || targetZone === 'exile') {
          console.log(`Token ${card.name} removed (moved from ${sourceZone} to ${targetZone})`);
          this.removeCardFromZone(sourceZone, sourceIndex); // Remove from source
          this.closeContextMenu(); return; // Don't add to target
        }
      }

      // Special handling/logging for commander movement
      if (card.isCommander) {
        // Log if commander moves to a zone where the owner *could* choose the command zone instead
        if (targetZone === 'graveyard' || targetZone === 'exile' || targetZone === 'hand' || targetZone === 'library') {
          console.warn(`Commander ${card.name} moved to ${targetZone}. In a real game, you could choose the Command Zone.`);
        }
        // Increase tax if moving *to* the command zone from elsewhere
        if(targetZone === 'command' && sourceZone !== 'command') {
          this.increaseCommanderTax(); // Call the tax increase method (it will close the menu)
          // Note: increaseCommanderTax closes the menu, so we might return early or let it proceed
        }
      }

      // Remove the card from its original zone
      const removedCard = this.removeCardFromZone(sourceZone, sourceIndex);
      if (!removedCard) {
        console.error(`Failed to remove ${card.name} from ${sourceZone}`); this.closeContextMenu(); return;
      }

      // Get the target zone array
      const targetArray = this.getZoneArray(targetZone);
      if (!targetArray) {
        // Invalid target, put the card back (should not happen with menu items)
        console.error("Invalid target zone for move:", targetZone);
        this.getZoneArray(sourceZone)?.splice(sourceIndex, 0, removedCard); // Put it back
        this.closeContextMenu(); return;
      }

      // Reset card state for the new zone
      removedCard.tapped = false;
      removedCard.position = null; // Clear absolute position

      // Add card to the target zone
      if (targetZone === 'battlefield') {
        // Add with a default position (e.g., top-left corner)
        removedCard.position = { x: 50, y: 50 };
        targetArray.push(removedCard);
      } else if (targetZone === 'library') {
        // Handle top or bottom placement
        if (libraryPosition === 'bottom') {
           targetArray.push(removedCard); // Add to end (bottom)
        } else {
           targetArray.unshift(removedCard); // Add to beginning (top)
        }
      } else {
        // Add to the end for other zones (hand, grave, exile, command)
        targetArray.push(removedCard);
      }

      console.log(`Moved ${removedCard.name} from ${sourceZone} to ${targetZone}`);
      this.closeContextMenu(); // Close menu after action
    },

    // Generic context menu action to move card to a specified zone
    moveToZone(targetZone) {
      this.moveCardFromContext(targetZone); // Call the generic move function
    },

    // Context menu action to move card to the top of the library
    moveToTopOfLibrary() {
      this.moveCardFromContext('library', 'top'); // Call the generic move function
    },

    // Context menu action to move card to the bottom of the library
    moveToBottomOfLibrary() {
      this.moveCardFromContext('library', 'bottom'); // Call the generic move function
    },

    // Flips a double-faced card
    flipCard() {
      const card = this.getCardFromContext();
      // Check if the card exists and has multiple faces
      if (card && card.card_faces?.length > 1) {
         card.flipped = !card.flipped; // Toggle the flipped state
         console.log(`${card.name} flipped to ${card.flipped ? 'back' : 'front'}`);
      }
      this.closeContextMenu();
    },

    // Taps or untaps a card on the battlefield
    tapCard() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') { // Only makes sense on the battlefield
         card.tapped = !card.tapped; // Toggle tapped state
         console.log(`${card.name} ${card.tapped ? 'tapped' : 'untapped'}`);
      }
      this.closeContextMenu();
    },

    // Adds a counter to a battlefield card
    addCounter() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
         if (card.counters === undefined || card.counters === null) card.counters = 0; // Initialize if needed
         card.counters++; // Increment counter
         console.log(`Added counter to ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    // Removes a counter from a battlefield card
    removeCounter() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield' && card.counters > 0) { // Check if counters exist
         card.counters--; // Decrement counter
         console.log(`Removed counter from ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    // Opens the modal to set power/toughness
    setPowerToughness() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        // Pre-fill modal inputs with current P/T or '' if undefined/null
        this.newPower = card.power ?? '';
        this.newToughness = card.toughness ?? '';
        this.showPTModal = true; // Show the modal
      }
      // Don't close context menu immediately, modal needs context
      // this.closeContextMenu();
    },

    // Opens the token modal, pre-filled to copy the context card
    createTokenCopy() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        // Pre-fill token details based on the copied card
        this.tokenName = `${card.name} Token`; // Append "Token" to the name
        this.tokenImageUrl = this.getCardImage(card); // Use the card's image
        this.tokenQuantity = 1; // Default to creating one copy
        this.showTokenModal = true; // Show the modal
      }
      // Don't close context menu immediately, modal needs context
      // this.closeContextMenu();
    },

    // --- Modal Actions ---

    // Opens the token creation modal with default values
    addToken() {
      this.tokenName = ''; // Clear previous inputs
      this.tokenQuantity = 1;
      this.tokenImageUrl = '';
      this.showTokenModal = true;
    },

    // Creates token(s) based on modal inputs and adds them to the battlefield
    createToken() {
      // Ensure quantity is at least 1
      const quantity = Math.max(1, Number(this.tokenQuantity) || 1);
      // Use provided name or default to "Token"
      const name = this.tokenName.trim() || 'Token';
      // Use provided URL or the default token image
      const imageUrl = this.tokenImageUrl.trim() || this.defaultTokenImage;

      // Create the specified number of tokens
      for (let i = 0; i < quantity; i++) {
        // Define the token object structure
        const newToken = {
          name: name,
          isToken: true, // Mark as a token
          // Generate a semi-unique ID
          gameId: `token-${name.replace(/\s+/g, '-')}-${Date.now()}-${i}`,
          // Structure image URIs like Scryfall for consistency
          image_uris: { normal: imageUrl },
          // Default game state properties
          tapped: false,
          flipped: false, // Tokens typically don't flip
          counters: 0,
          // Give tokens slightly offset positions to avoid perfect overlap
          position: { x: 50 + i * 10, y: 50 + i * 10 },
          // Tokens typically don't have inherent P/T unless specified
          power: undefined,
          toughness: undefined,
        };
        this.battlefield.push(newToken); // Add token to the battlefield
      }
      console.log(`Created ${quantity} "${name}" token(s)`);
      this.cancelTokenCreation(); // Close the modal
    },

    // Closes the token creation modal
    cancelTokenCreation() {
      this.showTokenModal = false;
      this.closeContextMenu(); // Close context menu if it was open
    },

    // Saves the new power/toughness from the modal
    savePT() {
      const card = this.getCardFromContext(); // Need to get context again as menu might have closed implicitly
      if (card && this.contextZone === 'battlefield') { // Check context again
          // Convert input to number, allow empty string to mean 'undefined' (reset)
          const power = this.newPower === '' ? undefined : Number(this.newPower);
          const toughness = this.newToughness === '' ? undefined : Number(this.newToughness);
          card.power = power;
          card.toughness = toughness;
          console.log(`Set P/T for ${card.name} to ${power ?? '?'}/${toughness ?? '?'}`);
      } else {
          console.warn("Could not save P/T, context lost or invalid.");
      }
      this.cancelPT(); // Close the modal
    },

    // Closes the power/toughness modal
    cancelPT() {
      this.showPTModal = false;
      this.closeContextMenu(); // Close context menu if it was open
    },

    // --- Library Search ---

    // Opens the library search modal and initializes results
    searchLibrary() {
      this.librarySearchQuery = ''; // Clear previous search
      // Initially show all cards in the library, sorted alphabetically
      this.librarySearchResults = [...this.library].sort((a, b) => a.name.localeCompare(b.name));
      this.showLibrarySearch = true; // Show the modal
    },

    // Filters the library based on the search input query
    searchLibraryCards() {
      const query = this.librarySearchQuery.toLowerCase().trim(); // Normalize query
      if (!query) {
        // If query is empty, show all cards, sorted
        this.librarySearchResults = [...this.library].sort((a, b) => a.name.localeCompare(b.name));
      } else {
        // Filter library based on card name containing the query (case-insensitive)
        this.librarySearchResults = this.library
            .filter(card => card.name.toLowerCase().includes(query))
            .sort((a, b) => a.name.localeCompare(b.name)); // Sort results too
      }
    },

    // Moves a card clicked in the search results to the hand
    moveSearchedCardToHand(card) {
      // Find the index of the selected card in the actual library array
      const index = this.library.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
      if (index !== -1) {
        // Remove the card from the library
        const [movedCard] = this.library.splice(index, 1);
        // Add the card to the hand
        this.hand.push(movedCard);
        console.log(`Moved "${movedCard.name}" from library to hand.`);
        // Standard MtG practice: Shuffle after searching
        console.log('Shuffling library after search...');
        this.shuffleDeck();
        this.closeLibrarySearch(); // Close the modal
      } else {
        console.error(`Card "${card.name}" not found in library during search move.`);
      }
    },

    // Closes the library search modal and resets search state
    closeLibrarySearch() {
      this.showLibrarySearch = false;
      this.librarySearchQuery = '';
      this.librarySearchResults = [];
    },

    // --- Helper Methods ---

    // Determines the correct image URL for a card, handling flipped state and defaults
    getCardImage(card) {
      if (!card) return this.defaultCardBack; // Default if no card data

      try { // Add try-catch for robustness against unexpected card data structures
          // Handle double-faced cards that are flipped
          if (card.flipped && card.card_faces && card.card_faces.length > 1 && card.card_faces[1].image_uris) {
              // Use the 'normal' size if available, fallback to 'large', then default back
              return card.card_faces[1].image_uris.normal || card.card_faces[1].image_uris.large || this.defaultCardBack;
          }
          // Handle regular cards or the front face of double-faced cards
          if (card.image_uris) {
              return card.image_uris.normal || card.image_uris.large || this.defaultCardBack;
          }
          // Fallback for cards where image is nested in the first face object
          if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
              return card.card_faces[0].image_uris.normal || card.card_faces[0].image_uris.large || this.defaultCardBack;
          }
          // Handle tokens specifically (might have image_uris directly or need default)
          if (card.isToken) {
              // Tokens might have image_uris set during creation, otherwise use default
              return card.image_uris?.normal || this.defaultTokenImage;
          }
      } catch (e) {
          console.error("Error getting card image for:", card?.name, e);
      }

      // Final fallback if no image found
      console.warn("Using default card back for card:", card?.name);
      return this.defaultCardBack;
    },

    // Returns the correct state array based on a zone name string
    getZoneArray(zoneName) {
      switch (zoneName) {
        case 'hand': return this.hand;
        case 'library': return this.library;
        case 'graveyard': return this.graveyard;
        case 'exile': return this.exileZone;
        case 'command': return this.commandZone;
        case 'battlefield': return this.battlefield;
        case 'initialDraw': return this.initialHand; // Include initial hand for mulligan phase
        default:
          console.error(`Invalid zone name: ${zoneName}`);
          return null; // Return null for invalid zones
      }
    },

    // Helper to find the actual index of a card in the 'hand' array (needed because of grouping)
    findCardIndexInHand(cardToFind) {
      if (!cardToFind) return -1;
      // Find the first card in the hand array that matches the gameId or id
      return this.hand.findIndex(card => (card.gameId || card.id) === (cardToFind.gameId || cardToFind.id));
    },

    // Retrieves the card object based on the current context menu state
    // Necessary because some actions close the menu before executing (like opening a modal)
    getCardFromContext() {
        if (!this.contextZone || this.contextIndex === null || this.contextIndex < 0) {
            // console.warn("Context is invalid for getting card (likely closed).");
            return null; // Return null gracefully if context is gone
        }
        const zoneArray = this.getZoneArray(this.contextZone);
        if (!zoneArray || this.contextIndex >= zoneArray.length) {
            console.error(`Context index ${this.contextIndex} out of bounds for zone ${this.contextZone}`);
            return null;
        }
        // Return the card at the stored index in the stored zone
        return zoneArray[this.contextIndex];
    },
  },
};
</script>

<style scoped>
/* --- Main Popup --- */
.playtest-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7); /* Darker overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Ensure it's on top */
  color: #ecf0f1; /* Light text for dark background */
  font-family: sans-serif; /* Basic font */
}

.playtest-content {
  background-color: #2c3e50; /* Dark background for the content area */
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
  width: 95vw;
  height: 95vh;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Prevent content overflow */
  border: 1px solid #34495e; /* Subtle border */
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #34495e;
  flex-shrink: 0; /* Prevent header from shrinking */
}

.popup-header h2 {
  margin: 0;
  color: #e74c3c; /* Accent color */
  font-size: 1.8rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #bdc3c7;
  cursor: pointer;
  padding: 0 10px;
  line-height: 1;
  transition: color 0.2s ease;
}
.close-btn:hover {
  color: #e74c3c; /* Match accent on hover */
}

/* --- Deck Selection --- */
.deck-selection {
  text-align: center;
  margin: auto; /* Center the selection box */
  padding: 20px;
  background-color: #34495e; /* Slightly lighter background */
  border-radius: 8px;
  max-width: 500px;
}
.deck-selection h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #ecf0f1;
}
.no-decks-message {
  color: #bdc3c7;
}
.deck-option {
  padding: 12px 20px;
  margin: 8px 0;
  background-color: #4e5d6c;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  color: #ecf0f1;
}
.deck-option:hover {
  background-color: #5c6f82;
  transform: translateY(-2px);
}

/* --- Initial Draw --- */
.initial-draw {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: center; /* Center vertically */
  flex-grow: 1;
}
.initial-draw h2 {
  margin-bottom: 20px;
  flex-shrink: 0;
}
.initial-draw-hand-container {
  display: flex;
  flex-wrap: wrap; /* Allow cards to wrap */
  justify-content: center;
  gap: 15px; /* Spacing between cards */
  margin-bottom: 25px;
  max-width: 90%; /* Limit width */
  padding: 15px;
  background-color: rgba(52, 73, 94, 0.5); /* Semi-transparent dark background */
  border-radius: 8px;
  overflow-y: auto; /* Allow scrolling if many cards */
}
.initial-draw .card-wrapper {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 3px solid transparent; /* Border for selection indicator */
  border-radius: calc(var(--card-border-radius, 8px) + 3px); /* Match image radius */
  flex-shrink: 0; /* Prevent wrapper from shrinking */
}
.initial-draw .card-wrapper:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.initial-draw .card-wrapper.selected {
  border-color: #e74c3c; /* Highlight selected cards */
  box-shadow: 0 0 15px rgba(231, 76, 60, 0.6);
}
.initial-draw .card-image {
  width: 120px; /* Adjust size as needed */
  height: auto;
  display: block;
  border-radius: var(--card-border-radius, 8px);
}
.action-buttons {
  display: flex;
  gap: 15px; /* Space between buttons */
  flex-shrink: 0;
  margin-top: 15px; /* Add some space above buttons */
}
.action-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  color: #fff;
  font-weight: bold;
}
.action-button:hover {
  transform: translateY(-2px);
}
.action-button.keep { background-color: #2ecc71; } /* Green */
.action-button.keep:hover { background-color: #27ae60; }
.action-button.mulligan { background-color: #e74c3c; } /* Red */
.action-button.mulligan:hover { background-color: #c0392b; }
.action-button.draw { background-color: #3498db; } /* Blue */
.action-button.draw:hover { background-color: #2980b9; }

/* --- Playtest Interface Layout --- */
.playtest-interface {
  display: grid;
  grid-template-areas:
    "top top top"
    "battlefield battlefield battlefield"
    "library hand hand";
  grid-template-rows: auto 1fr auto; 
  grid-template-columns: auto 1fr; 
  gap: 15px;
  flex-grow: 1; 
  overflow: hidden; 
  padding: 10px;
  background-color: #34495e;
  border-radius: 8px;
}

/* --- Top Row (Command, Grave, Exile) --- */
.top-row {
  grid-area: top;
  display: flex;
  gap: 15px;
  height: 150px; 
  overflow: hidden; 
}
.command-zone, .graveyard, .exile-zone {
  flex: 1; 
  background-color: #2c3e50; 
  padding: 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden; 
  border: 1px solid #4e5d6c;
  cursor: pointer; 
  transition: background-color 0.2s;
  position: relative; 
}
.top-row h3 {
  margin: 0 0 8px 0;
  text-align: center;
  font-size: 0.9rem;
  color: #bdc3c7;
  border-bottom: 1px solid #4e5d6c;
  padding-bottom: 5px;
  flex-shrink: 0;
}
.zone-preview {
  display: flex;
  gap: 5px;
  align-items: center;
  justify-content: center; 
  flex-grow: 1; 
  position: relative; 
  min-height: 50px; /
}
.zone-preview .card-wrapper {
  position: relative; 
}
.card-image.small {
  width: 50px; 
  height: auto;
  border-radius: 4px;
  display: block;
}
.more-cards-indicator {
  font-size: 0.8rem;
  color: #95a5a6;
  margin-left: 5px;
  align-self: flex-end; 
  padding-bottom: 5px;
}
.empty-zone-message {
  font-size: 0.85rem;
  color: #7f8c8d;
  text-align: center;
  width: 100%; 
  position: absolute; 
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 0 5px;
}
.commander-tax {
  position: absolute;
  bottom: 2px;
  right: 2px;
  background-color: rgba(44, 62, 80, 0.8);
  color: #ecf0f1;
  font-size: 0.7rem;
  padding: 1px 3px;
  border-radius: 3px;
}

/* --- Expanded Zones --- */
.expanded-zone {
  position: fixed; 
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80vw;
  max-width: 900px;
  height: 70vh;
  background-color: rgba(44, 62, 80, 0.98); /* Slightly transparent */
  border: 2px solid #e74c3c;
  border-radius: 10px;
  z-index: 1100; /* Above the main popup */
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}
.expanded-cards {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 10px;
  background-color: #34495e;
  border-radius: 6px;
  justify-content: center; 
  align-content: flex-start; 
}
.expanded-zone .card-wrapper {
  position: relative; 
}
.expanded-zone .card-image {
  width: 130px; 
  height: auto;
  border-radius: 6px;
  display: block;
  cursor: grab;
}
.expanded-zone .card-image:active {
  cursor: grabbing;
}
.collapse-button {
  margin-top: 15px;
  padding: 8px 15px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  align-self: center; 
  transition: background-color 0.2s;
  flex-shrink: 0;
}
.collapse-button:hover {
  background-color: #c0392b;
}
.expanded-zone .empty-zone-message {
  position: static; 
  transform: none;
  font-size: 1rem;
  color: #bdc3c7;
  margin: auto;
  width: 100%; 
}
.expanded-zone .commander-tax { 
    position: absolute;
    bottom: 5px;
    right: 5px;
    background-color: rgba(44, 62, 80, 0.8);
    color: #ecf0f1;
    font-size: 0.8rem;
    padding: 2px 5px;
    border-radius: 3px;
}


/* --- Battlefield --- */
.battlefield {
  grid-area: battlefield;
  background-color: #3d5a80; /* Different background for battlefield */
  border-radius: 8px;
  padding: 15px;
  position: relative; 
  overflow: hidden; 
  border: 1px solid #4e5d6c;
  display: flex; 
  flex-direction: column; 
}
.battlefield h3 {
  margin: 0 0 10px 0;
  text-align: center;
  color: #e0fbfc;
  flex-shrink: 0; 
}
.battlefield-cards {
  position: relative; /* Container for absolute positioned cards */
  width: 100%;
  flex-grow: 1; /* Take remaining space */
  overflow: auto; /* Allow scrolling within this container */
  min-height: 200px; /* Ensure minimum drag area */
  border-radius: 4px; /* Optional: slight rounding */
  background-color: rgba(0, 0, 0, 0.1); /* Subtle inner background */
}
.battlefield-card {
  position: absolute !important; /* Override any other positioning, enable drag */
  cursor: grab;
  transition: transform 0.2s ease-in-out; /* Smooth rotation for tap */
  z-index: 1; /* Base level */
}
.battlefield-card:active {
  cursor: grabbing;
  z-index: 10; /* Bring to front while dragging */
}
.battlefield-card .card-image {
  width: 100px; /* Adjust size */
  height: auto;
  border-radius: 5px;
  display: block;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  user-select: none; /* Prevent image selection during drag */
  -webkit-user-drag: none; /* Prevent browser's default image drag */
  border: 1px solid rgba(0,0,0,0.2); /* Subtle border on cards */
}
.counter-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.8rem;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
  z-index: 2; /* Above card image */
}
.pt-indicator {
    position: absolute;
    bottom: 3px;
    left: 3px;
    background-color: rgba(44, 62, 80, 0.85);
    color: #ecf0f1;
    font-size: 0.8rem;
    padding: 2px 4px;
    border-radius: 3px;
    font-weight: bold;
    z-index: 2; /* Above card image */
}
.token-button {
  position: absolute;
  bottom: 10px;
  right: 10px;
  padding: 6px 12px;
  background-color: #9b59b6; /* Purple */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
  z-index: 20; /* Above cards */
  font-size: 0.9rem;
}
.token-button:hover {
  background-color: #8e44ad;
}


/* --- Bottom Row (Library, Hand) --- */
.bottom-row {
  grid-area: library / library / hand / hand; /* Span across bottom areas */
  display: flex;
  gap: 15px;
  height: 180px; /* Fixed height */
}
.library {
  grid-area: library; /* Explicitly define (though inherited) */
  background-color: #2c3e50;
  padding: 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between; /* Space out elements */
  width: 150px; /* Fixed width for library */
  flex-shrink: 0; /* Prevent shrinking */
  border: 1px solid #4e5d6c;
}
.library h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #bdc3c7;
  width: 100%;
  text-align: center;
  flex-shrink: 0;
}
.library-image {
  width: 80px;
  height: auto;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: transform 0.2s, box-shadow 0.2s;
  flex-shrink: 0; /* Prevent image shrinking weirdly */
}
.library-image:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
}
.draw-button {
  padding: 6px 10px;
  width: 80%; /* Match image width roughly */
  font-size: 0.9rem;
   background-color: #3498db; /* Blue */
   color: white;
   border: none;
   border-radius: 4px;
   cursor: pointer;
   transition: background-color 0.2s;
   flex-shrink: 0;
}
.draw-button:hover {
  background-color: #2980b9;
}

.hand-zone {
  grid-area: hand; /* Explicitly define */
  background-color: #2c3e50;
  padding: 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Take remaining space */
  overflow: hidden; /* Hide overflow, rely on inner scroll */
  border: 1px solid #4e5d6c;
  position: relative; /* For empty message */
}
.hand-zone h3 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: #bdc3c7;
  text-align: center;
  flex-shrink: 0; /* Prevent title from shrinking */
}
.hand-cards {
  display: flex;
  gap: 10px;
  padding-bottom: 10px; /* Space for scrollbar */
  align-items: flex-start; /* Align cards to the top */
  flex-grow: 1;
  overflow-x: auto; /* Allow horizontal scrolling for hand */
  overflow-y: hidden; /* Prevent vertical scrolling */
  min-height: 120px; /* Ensure minimum height */
}
.hand-zone .card-wrapper {
  position: relative; /* For quantity badge */
  flex-shrink: 0; /* Prevent cards from shrinking */
}
.hand-zone .card-image {
  width: 90px; /* Hand card size */
  height: auto;
  border-radius: 5px;
  display: block;
  cursor: grab;
  transition: transform 0.1s ease;
  border: 1px solid rgba(0,0,0,0.2); /* Subtle border */
}
.hand-zone .card-image:active {
  cursor: grabbing;
  transform: scale(0.95);
}
.quantity-badge {
  position: absolute;
  top: -5px;
  left: -5px;
  background-color: #2980b9;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.75rem;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
  z-index: 2; /* Above card */
}
.hand-zone .empty-zone-message {
    position: absolute; /* Center message */
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.9rem;
    color: #7f8c8d;
}

/* --- Context Menu --- */
.context-menu {
  position: fixed; /* Position relative to viewport */
  background-color: #34495e;
  border: 1px solid #4e5d6c;
  border-radius: 5px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 1200; /* Above expanded zones */
  padding: 5px 0;
  min-width: 180px;
}
.context-menu-item {
  padding: 8px 15px;
  color: #ecf0f1;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.15s ease;
  white-space: nowrap; /* Prevent wrapping */
}
.context-menu-item:hover {
  background-color: #4e5d6c;
}
.context-menu-divider {
  height: 1px;
  background-color: #4e5d6c;
  margin: 5px 0;
}

/* --- Modals (Token, P/T, Library Search) --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8); /* Darker overlay for modals */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050; /* Below context menu, above expanded zones */
  padding: 20px; /* Add padding for smaller screens */
}
.modal-content {
  background-color: #34495e;
  padding: 25px 30px;
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5);
  border: 1px solid #4e5d6c;
  color: #ecf0f1;
  max-height: 85vh; /* Limit modal height */
  display: flex;
  flex-direction: column;
  width: 90%; /* Default width */
  max-width: 600px; /* Max width */
}
.modal-content h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #e74c3c;
  border-bottom: 1px solid #4e5d6c;
  padding-bottom: 10px;
  flex-shrink: 0;
}
.token-form, .pt-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto; /* Allow scrolling if form is long */
  padding-right: 5px; /* Space for scrollbar */
}
.modal-content label {
  display: flex;
  flex-direction: column; /* Stack label text above input */
  align-items: flex-start; /* Align text left */
  gap: 5px;
  font-size: 0.95rem;
}
.modal-content input[type="text"], .modal-content input[type="number"] {
  /* flex-grow: 1; */ /* Removed flex-grow */
  width: 100%; /* Make inputs take full width */
  padding: 8px 10px;
  border: 1px solid #4e5d6c;
  background-color: #2c3e50;
  color: #ecf0f1;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box; /* Include padding in width */
}
.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px solid #4e5d6c;
  flex-shrink: 0;
}
.modal-buttons button { /* General modal button style */
  padding: 9px 18px;
  border: none;
  border-radius: 5px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  color: #fff;
  font-weight: bold;
}
.modal-buttons button:hover {
  transform: translateY(-1px);
}
.confirm-button { background-color: #2ecc71; }
.confirm-button:hover { background-color: #27ae60; }
.cancel-button { background-color: #95a5a6; }
.cancel-button:hover { background-color: #7f8c8d; }

/* --- Library Search Specific --- */
.library-search-modal {
  width: 85vw;
  max-width: 1000px;
}
.library-search-input {
  width: 100%; /* Full width */
  margin-bottom: 15px;
  padding: 10px;
  box-sizing: border-box;
  flex-shrink: 0;
}
.search-results {
  flex-grow: 1;
  overflow-y: auto;
  background-color: #2c3e50;
  border: 1px solid #4e5d6c;
  border-radius: 6px;
  padding: 15px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); /* Adjust min card width */
  gap: 1rem;
  margin-bottom: 1rem; /* Use margin-bottom instead of margin */
  max-height: 55vh; /* Limit height */
  min-height: 150px; /* Ensure some space even when empty */
  position: relative; /* For empty message */
}
.search-result-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background-color: #34495e; /* Card background */
  padding: 5px;
  border-radius: 4px;
}
.search-result-card:hover {
  transform: scale(1.04);
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  background-color: #4e5d6c;
}
.search-card-image {
  width: 100%;
  /* max-width: 150px; */ /* Let grid control width */
  height: auto;
  border-radius: 6px;
  display: block;
}
.search-result-card span {
  font-size: 0.8rem; /* Slightly smaller text */
  color: #bdc3c7; /* Slightly lighter than empty message */
  word-break: break-word; /* Wrap long names */
  margin-top: 4px;
}
.library-search-buttons {
  justify-content: space-between; /* Space out shuffle and close */
}
.library-search-modal .empty-zone-message { /* Style message inside results */
    grid-column: 1 / -1; /* Span full width */
    text-align: center;
    font-size: 1rem;
    color: #7f8c8d;
    margin: auto;
    position: absolute; /* Center within results area */
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: calc(100% - 30px); /* Account for padding */
}

/* --- Loading State --- */
.loading {
  margin: auto; /* Center loading text */
  font-size: 1.5rem;
  color: #bdc3c7;
}

/* --- General Card Wrapper --- */
.card-wrapper {
  position: relative; /* Establish positioning context for badges/overlays */
  line-height: 0; /* Prevent extra space below images */
}

/* --- Responsive Adjustments --- */
@media (max-width: 1200px) {
  .playtest-content {
      width: 98vw;
      height: 98vh;
      padding: 15px;
  }
  .expanded-zone {
      width: 90vw;
  }
  .library-search-modal {
      width: 90vw;
  }
  .initial-draw .card-image { width: 100px; }
  .battlefield-card .card-image { width: 90px; }
  .hand-zone .card-image { width: 80px; }
}

@media (max-width: 768px) {
  .top-row { height: 120px; }
  .bottom-row { height: 150px; }
  .library { width: 120px; }
  .library-image { width: 65px; }
  .draw-button { width: 90%; font-size: 0.8rem; padding: 5px 8px; }
  .initial-draw .card-image { width: 80px; }
  .battlefield-card .card-image { width: 75px; }
  .hand-zone .card-image { width: 70px; }
  .hand-cards { gap: 5px; }
  .expanded-zone { width: 95vw; height: 75vh; }
  .expanded-zone .card-image { width: 100px; }
  .library-search-modal { width: 95vw; }
  .search-results { grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 0.8rem; } /* Smaller cards */
  .action-button { padding: 8px 15px; font-size: 0.9rem; }
  .modal-content { padding: 20px; max-width: 90%; }
  .modal-content h3 { font-size: 1.3rem; }
}

@media (max-width: 480px) {
  .playtest-content { padding: 10px; }
  .popup-header h2 { font-size: 1.5rem; }
  .close-btn { font-size: 1.8rem; }
  .top-row { height: 100px; gap: 8px; }
  .top-row h3 { font-size: 0.8rem; }
  .card-image.small { width: 40px; }
  .bottom-row { height: 130px; gap: 8px; }
  .library { width: 100px; padding: 8px; }
  .library-image { width: 55px; }
  .initial-draw .card-image { width: 70px; }
  .battlefield-card .card-image { width: 65px; }
  .hand-zone .card-image { width: 60px; }
  .counter-badge { width: 16px; height: 16px; font-size: 0.7rem; }
  .pt-indicator { font-size: 0.7rem; padding: 1px 3px; }
  .quantity-badge { width: 16px; height: 16px; font-size: 0.7rem; }
  .action-buttons { gap: 10px; }
  .action-button { padding: 6px 12px; font-size: 0.8rem; }
  .modal-buttons { gap: 8px; }
  .modal-buttons button { padding: 7px 14px; font-size: 0.85rem; }
  .search-results { grid-template-columns: repeat(auto-fill, minmax(75px, 1fr)); gap: 0.5rem; } /* Even smaller cards */
  .search-result-card span { font-size: 0.75rem; }
  .modal-content { max-width: 95%; } /* Allow modal to use more width */
}

</style>
