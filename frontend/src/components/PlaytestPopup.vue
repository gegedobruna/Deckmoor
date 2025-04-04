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
            <div class="zone-header">
              <h3>Command Zone</h3>
              <div v-if="commandZone.some(c => c.isCommander)" class="commander-tax-display">
                Commander Tax: {{ commanderTax }}
              </div>
            </div>

            <div v-if="!isZoneExpanded.command" class="zone-preview">
              <div v-if="commandZone.length > 0">
                <div v-for="(card, index) in commandZone" :key="'command-preview-' + index" class="card-wrapper">
                  <img :src="getCardImage(card)"
                      :alt="card.name"
                      class="card-image small"
                      draggable="true"
                      @dragstart="dragStart($event, card, 'command', index)"
                      @contextmenu.prevent="openCardMenu($event, card, 'command', index)">
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
                 Library contains {{ library.length }} cards. (Showing in current library order)
               </div>
               <div v-if="library.length === 0" class="empty-zone-message">
                 Library is empty.
               </div>
            </div>
            <div class="modal-buttons library-search-buttons">
              <button @click="shuffleLibrary" class="action-button mulligan">Shuffle Library</button>
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
// Helper function to limit the rate at which a function can fire.
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
    // Array of available decks passed from the parent component.
    decks: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      selectedDeckId: null, // ID of the deck chosen for playtesting
      phase: 'select', // Current phase: 'select', 'initialDraw', 'playtest', 'loading'
      loading: true, // Indicates if decks are still loading
      isInitialized: false, // Flag to ensure component is ready before rendering main content

      // Game state arrays
      library: [],
      initialHand: [], // Stores the hand during the initial draw/mulligan phase
      hand: [],
      battlefield: [],
      graveyard: [],
      exileZone: [],
      commandZone: [],

      selectedCards: [], // Indices of cards selected for mulligan in initialHand
      isZoneExpanded: { // State for expanded zone views
        command: false,
        exile: false,
        graveyard: false,
      },

      // Drag and drop state
      draggedCard: null, // The card object being dragged
      draggedFromZone: null, // The name of the zone the card came from
      draggedFromIndex: null, // The index within the source zone array
      isDraggingBattlefieldCard: false, // Flag for dragging specifically on the battlefield
      draggedBattlefieldCardIndex: -1, // Index of the card being dragged on the battlefield
      dragStartOffset: { x: 0, y: 0 }, // Offset for smooth battlefield dragging
      throttledHandleDrag: null, // Throttled version of the drag handler

      // Context menu state
      showContextMenu: false, // Whether the right-click menu is visible
      contextMenuPosition: { x: 0, y: 0 }, // Position of the context menu
      contextCard: null, // The card the context menu is for
      contextZone: null, // The zone the context card is in
      contextIndex: null, // The index of the context card in its zone
      contextMenuCloseHandler: null, // Handler to close the menu on outside click

      // Modal states
      showTokenModal: false, // Visibility for the create token modal
      tokenName: '', // Name for the new token
      tokenQuantity: 1, // Quantity of tokens to create
      tokenImageUrl: '', // Optional image URL for the token
      showPTModal: false, // Visibility for the set power/toughness modal
      newPower: 0, // New power value
      newToughness: 0, // New toughness value
      showLibrarySearch: false, // Visibility for the library search modal
      librarySearchQuery: '', // Search term for the library
      librarySearchResults: [], // Results for library search (now reversed for display)

      // Game counters/state
      commanderTax: 0, // Additional cost to cast the commander
      mulliganCount: 0, // Number of times the player has mulliganed

      // Asset URLs
      defaultCardBack: new URL('@/assets/cards/mtg-card-back.jpg', import.meta.url).href,
      defaultTokenImage: new URL('@/assets/cards/mtg-token-default.jpg', import.meta.url).href,
    };
  },
  computed: {
    // Groups cards in hand by name/ID for display purposes.
    groupedHand() {
      const groups = [];
      const cardMap = new Map(); // Use a Map for efficient lookup by unique ID or name
      this.hand.forEach(card => {
        // Use gameId if available (unique instance), otherwise fallback to id or name
        const key = card.gameId || card.id || card.name;
        if (cardMap.has(key)) {
          // Increment count if this card is already in a group
          cardMap.get(key).count++;
        } else {
          // Create a new group for this card
          const group = { card: card, count: 1 };
          cardMap.set(key, group);
          groups.push(group);
        }
      });
      return groups;
    },
  },
  created() {
    // Initialize the throttled drag handler on component creation.
    this.throttledHandleDrag = throttle(this.handleDrag, 16); // Throttle to ~60fps
  },
  mounted() {
    console.log('PlaytestPopup mounted');
    // Ensure the DOM is ready before setting initialized flag.
    this.$nextTick(() => {
        this.isInitialized = true;
        this.loading = false; // Assume decks passed as props are loaded
    });

    // Add a global click listener to close the context menu when clicking outside it.
    this.contextMenuCloseHandler = (event) => {
      // Check if the context menu is shown and the click was not inside the menu itself
      if (this.showContextMenu && !event.target.closest('.context-menu')) {
        this.closeContextMenu();
      }
    };
    document.addEventListener('click', this.contextMenuCloseHandler);
  },
  beforeUnmount() {
    console.log('PlaytestPopup unmounting');
    // Clean up event listeners to prevent memory leaks.
    document.removeEventListener('click', this.contextMenuCloseHandler);
    document.removeEventListener('mousemove', this.throttledHandleDrag);
    document.removeEventListener('mouseup', this.stopDrag);
    // Reset all component state.
    this.cleanup();
  },
  methods: {
    // Closes the popup and emits an event to the parent component.
    closePopup() {
      this.cleanup(); // Reset state before closing
      this.$emit('close');
    },

    // Resets all game state variables to their initial values.
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
      this.phase = 'select'; // Go back to deck selection phase
      this.commanderTax = 0;
      this.mulliganCount = 0;
      this.closeContextMenu(); // Ensure context menu is closed
      // Reset modal states
      this.showTokenModal = false;
      this.showPTModal = false;
      this.showLibrarySearch = false;
      // Reset expanded zone states
      this.isZoneExpanded = { command: false, exile: false, graveyard: false };
      // Reset drag states
      this.isDraggingBattlefieldCard = false;
      this.draggedBattlefieldCardIndex = -1;
      this.draggedCard = null;
      this.draggedFromZone = null;
      this.draggedFromIndex = null;
    },

    // Sets the selected deck ID and triggers loading the deck.
    selectAndLoadDeck(deckId) {
      this.selectedDeckId = deckId;
      this.loadDeck();
    },

    // Loads the selected deck, initializes game zones, shuffles, and draws the initial hand.
    loadDeck() {
      try {
        if (!this.selectedDeckId) { console.error('No deck selected'); return; }
        // Find the deck data from the props using the selected ID.
        const deck = this.decks.find(d => d.id === this.selectedDeckId);
        if (!deck) { console.error('Selected deck not found:', this.selectedDeckId); return; }
        console.log('Loading deck:', deck.name);
        this.cleanup(); // Reset previous game state first
        this.phase = 'loading'; // Show loading state

        // Deep copy the deck data to avoid modifying the original prop.
        const deckData = JSON.parse(JSON.stringify(deck));
        const libraryCards = [];

        // Populate the library, excluding the commander.
        if (deckData.cards && Array.isArray(deckData.cards)) {
          deckData.cards.forEach((cardData, cardIndex) => {
            // Skip if this card is the designated commander.
            if (deckData.commander && cardData.id === deckData.commander.id) return;
            // Determine the quantity of this card.
            const count = cardData.count || cardData.quantity || 1;
            // Add each copy to the library with initial game state properties.
            for (let i = 0; i < count; i++) {
              libraryCards.push({
                ...cardData,
                // Generate a unique ID for this specific instance of the card in the game.
                gameId: `card-${cardData.id}-${cardIndex}-${i}-${Date.now()}`,
                tapped: false,
                flipped: false,
                counters: 0,
                position: null, // Position on battlefield (null initially)
                power: cardData.power, // Keep original P/T if available
                toughness: cardData.toughness,
              });
            }
          });
          this.library = libraryCards;
          console.log(`Library initialized with ${this.library.length} cards. First few:`, this.library.slice(0, 5).map(c => c.name));
        } else {
          console.warn('Deck has no cards or cards is not an array:', deckData);
          this.library = [];
        }

        // Set up the command zone if a commander exists.
        if (deckData.commander) {
          this.commandZone = [{
            ...deckData.commander,
            isCommander: true, // Mark this card as the commander
            gameId: `commander-${deckData.commander.id}-${Date.now()}`, // Unique game ID
            tapped: false,
            flipped: false,
            counters: 0,
            position: null,
            power: deckData.commander.power,
            toughness: deckData.commander.toughness,
          }];
        } else {
          this.commandZone = [];
        }

        // Shuffle the newly created library.
        this.shuffleDeck();
        // Draw the starting hand.
        this.drawInitialHand();
        // Move to the initial draw phase.
        this.phase = 'initialDraw';
        console.log('Deck loaded:', { library: this.library.length, hand: this.initialHand.length, commander: this.commandZone.length });

      } catch (error) {
        console.error('Error in loadDeck:', error);
        this.phase = 'select'; // Revert to selection phase on error
      }
    },

    // Draws the initial hand of 7 cards.
    drawInitialHand() {
      this.initialHand = [];
      this.selectedCards = []; // Clear any previous selections
      const handSize = 7;
      for (let i = 0; i < handSize; i++) {
        if (this.library.length > 0) {
          // Draw from the 'top' (end) of the library.
          this.initialHand.push(this.library.pop());
        } else {
          console.warn("Library empty during initial draw");
          break; // Stop drawing if library is empty
        }
      }
    },

    // Toggles the selection state of a card in the initial hand (for mulligan).
    toggleCardSelect(index) {
      const idx = this.selectedCards.indexOf(index);
      if (idx === -1) {
        // Add index to selection if not already selected.
        this.selectedCards.push(index);
      } else {
        // Remove index from selection if already selected.
        this.selectedCards.splice(idx, 1);
      }
    },

    // Finalizes the hand and moves to the main playtest phase.
    keepHand() {
      this.hand = [...this.initialHand]; // Move cards from initialHand to the actual hand
      this.initialHand = []; // Clear the temporary initial hand
      this.phase = 'playtest'; // Start the game!
    },

    // Handles the mulligan process.
    mulligan() {
        this.mulliganCount++; // Track mulligans
        const newHandSize = 7; // Always draw 7 (standard mulligan)

        // Put the current initial hand back into the library.
        this.library.push(...this.initialHand);
        this.initialHand = []; // Clear the hand

        // Reshuffle the library.
        this.shuffleDeck();

        // Draw a new hand of 7 cards.
        for (let i = 0; i < newHandSize; i++) {
            if (this.library.length > 0) {
                this.initialHand.push(this.library.pop()); // Draw from top (end)
            } else {
                console.warn("Library empty during mulligan draw");
                break;
            }
        }

        // Inform the user about the mulligan and the need to put cards back manually.
        alert(`Mulligan ${this.mulliganCount}. Drawn ${this.initialHand.length} cards. You must manually put ${this.mulliganCount} card(s) on the bottom of your library using the context menu after keeping.`);

        this.phase = 'initialDraw'; // Stay in the initial draw phase
        this.selectedCards = []; // Reset selections for the new hand
    },

    // Draws a single card from the library to the hand.
    drawCard() {
      if (this.library.length > 0) {
        const drawnCard = this.library.pop(); // Get card from the end (top)
        if (this.phase === 'initialDraw') {
           // If still in mulligan phase, add to initialHand
           this.initialHand.push(drawnCard);
        } else if (this.phase === 'playtest') {
           // Otherwise, add to the main hand
           this.hand.push(drawnCard);
        }
      } else {
        console.warn('Cannot draw, library is empty!'); // Prevent drawing from empty library
      }
    },

    // Shuffles the library array using the Fisher-Yates (Knuth) algorithm.
    shuffleDeck() {
      console.log('Shuffling deck. Library size:', this.library.length);
      if (this.library.length > 1) {
          // Log the cards at the end of the array (top of the library)
          console.log('Library order BEFORE shuffle (top 5):', this.library.slice(-5).map(c => c.name));
      }

      // Standard Fisher-Yates shuffle algorithm
      for (let i = this.library.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1)); // Random index from 0 to i
        // Swap elements at indices i and j
        [this.library[i], this.library[j]] = [this.library[j], this.library[i]];
      }

      if (this.library.length > 1) {
           // Log the cards at the end of the array (top of the library) again
          console.log('Library order AFTER shuffle (top 5):', this.library.slice(-5).map(c => c.name));
      }
      console.log('Deck shuffle complete.');
    },

    // Shuffles the library, typically called from the library search modal.
    shuffleLibrary() {
        console.log('Attempting to shuffle library via button...');
        this.shuffleDeck(); // Reuse the main shuffle logic
        // If the search modal is open, refresh the displayed results to show new order.
        if (this.showLibrarySearch) {
            this.searchLibraryCards();
        }
    },

    // Increases the commander tax by 2.
    increaseCommanderTax() {
      this.commanderTax += 2; // Standard tax increase
      console.log(`Commander tax increased to ${this.commanderTax}`);
      this.closeContextMenu(); // Close menu if called from there
    },

    // Toggles the expanded view for a specific zone (command, graveyard, exile).
    toggleZoneExpansion(zone) {
      // Collapse other zones when expanding one.
      Object.keys(this.isZoneExpanded).forEach(key => {
          if (key !== zone) {
              this.isZoneExpanded[key] = false;
          }
      });
      // Toggle the state for the clicked zone.
      this.isZoneExpanded[zone] = !this.isZoneExpanded[zone];
      console.log(`Toggled ${zone} expansion to:`, this.isZoneExpanded[zone]);
    },

    // Removes a card from a specified zone at a given index. Returns the removed card or null.
    removeCardFromZone(zoneName, index) {
        const zoneArray = this.getZoneArray(zoneName);
        if (!zoneArray || index < 0 || index >= zoneArray.length) {
            console.error(`Cannot remove card from ${zoneName} at invalid index ${index}`);
            return null; // Invalid index or zone
        }
        // Remove the card using splice and return the removed card (first element of the returned array).
        return zoneArray.splice(index, 1)[0];
    },

    // Handles the start of a drag operation. Stores card data in the dataTransfer object.
    dragStart(event, card, zone, index) {
        console.log(`Drag Start: ${card.name} from ${zone}[${index}]`);
        // Store card identifier, source zone, and index for the drop event.
        event.dataTransfer.setData('text/plain', JSON.stringify({ cardId: card.gameId || card.id, zone, index }));
        event.dataTransfer.effectAllowed = 'move'; // Indicate that the card will be moved.
        // Keep track of the dragged card details locally as well.
        this.draggedCard = card;
        this.draggedFromZone = zone;
        this.draggedFromIndex = index; // Note: This index might become stale if the array changes before drop.
    },

    // Handles the drop event when a card is dropped onto a zone.
    dropCard(event, targetZone) {
        event.preventDefault(); // Prevent default browser drop behavior.
        console.log(`Drop on: ${targetZone}`);
        try {
            // Retrieve the data stored during dragStart.
            const data = JSON.parse(event.dataTransfer.getData('text/plain'));
            const { cardId, zone: sourceZone } = data; // Original index might be unreliable, use cardId.
            console.log(`Dropped card ID: ${cardId} from ${sourceZone} to ${targetZone}`);

            let cardToMove;
            let actualSourceIndex = -1; // We need to find the card's current index.

            const sourceArray = this.getZoneArray(sourceZone);
            if (!sourceArray) { console.error("Invalid source zone:", sourceZone); return; }

            // Find the card in the source array using its unique gameId or fallback ID.
            actualSourceIndex = sourceArray.findIndex(c => (c.gameId || c.id) === cardId);

            if (actualSourceIndex === -1) {
                // This can happen if the card was already moved (e.g., via context menu) or state changed.
                console.error(`Card ${cardId} not found in source zone ${sourceZone}. Drag might be stale.`);
                return;
            }

            // Remove the card from the source zone using the found index.
            cardToMove = sourceArray.splice(actualSourceIndex, 1)[0];
            if (!cardToMove) { console.error("Failed to extract card from source zone."); return; }

            // Handle token behavior: Tokens cease to exist when leaving the battlefield (except to command zone potentially, though usually not).
            if (cardToMove.isToken && sourceZone === 'battlefield') {
                if (targetZone === 'hand' || targetZone === 'library' || targetZone === 'graveyard' || targetZone === 'exile') {
                    console.log(`Token ${cardToMove.name} removed (moved from battlefield to ${targetZone})`);
                    this.draggedCard = null; // Clear drag state
                    return; // Do not add the token to the target zone.
                }
            }

            // Get the target zone array.
            const targetArray = this.getZoneArray(targetZone);
            if (!targetArray) {
                console.error("Invalid target zone:", targetZone);
                // Put the card back in the source zone if the target is invalid.
                sourceArray.splice(actualSourceIndex, 0, cardToMove);
                return;
            }

            // Reset card state when moving zones (untap, clear position).
            cardToMove.tapped = false;
            cardToMove.position = null;

            // Add the card to the target zone.
            if (targetZone === 'battlefield') {
                // Calculate position relative to the battlefield container.
                const battlefieldRect = event.currentTarget.getBoundingClientRect();
                cardToMove.position = {
                    x: event.clientX - battlefieldRect.left,
                    y: event.clientY - battlefieldRect.top,
                };
                targetArray.push(cardToMove); // Add to the end of the battlefield array.
            } else if (targetZone === 'library') {
                 // Drop onto library puts on TOP (end of array)
                 targetArray.push(cardToMove); // Add to end (top, drawn by pop)
                 console.log(`Moved ${cardToMove.name} to TOP of library via drop`);
            } else {
                // For hand, graveyard, exile, command zone, add to the end.
                targetArray.push(cardToMove);
            }

            console.log(`Moved ${cardToMove.name} from ${sourceZone} to ${targetZone}`);
        } catch (e) {
            console.error("Error processing drop event:", e);
        } finally {
             // Clear drag state regardless of success or failure.
             this.draggedCard = null;
             this.draggedFromZone = null;
             this.draggedFromIndex = null;
        }
    },

    // --- Battlefield Dragging (Mouse Down/Move/Up) ---

    // Initiates dragging a card within the battlefield using mouse events.
    startDrag(event, card, index) {
        // Only respond to left mouse button clicks.
        if (event.button !== 0) return;
        // Ensure the click started on the card itself.
        if (!event.target.closest('.battlefield-card')) return;

        console.log(`Battlefield Drag Start: ${card.name}`);
        this.isDraggingBattlefieldCard = true; // Set flag
        this.draggedBattlefieldCardIndex = index; // Store index

        // Initialize position if it doesn't exist (e.g., first drag).
        if (!card.position) {
            card.position = { x: 50, y: 50 };
        }

        // Calculate the offset between the mouse click and the card's top-left corner.
        const cardRect = event.target.closest('.battlefield-card').getBoundingClientRect();
        this.dragStartOffset = {
            x: event.clientX - cardRect.left,
            y: event.clientY - cardRect.top
        };

        // Add listeners to the document to track mouse movement and release.
        document.addEventListener('mousemove', this.throttledHandleDrag);
        document.addEventListener('mouseup', this.stopDrag);
        event.preventDefault(); // Prevent default text selection or other drag behaviors.
    },

    // Handles mouse movement while dragging a battlefield card. Updates card position.
    handleDrag(event) {
        // Only proceed if currently dragging a battlefield card.
        if (!this.isDraggingBattlefieldCard || this.draggedBattlefieldCardIndex < 0) return;
        const card = this.battlefield[this.draggedBattlefieldCardIndex];
        if (!card) return; // Safety check

        // Get the bounding box of the battlefield card container area.
        const battlefieldCardsRect = this.$el.querySelector('.battlefield-cards').getBoundingClientRect();

        // Calculate the new top-left position based on mouse position, container offset, and initial click offset.
        const newX = event.clientX - battlefieldCardsRect.left - this.dragStartOffset.x;
        const newY = event.clientY - battlefieldCardsRect.top - this.dragStartOffset.y;

        // Update the card's position state. Vue reactivity will update the style.
        card.position = { x: newX, y: newY };
    },

    // Handles mouse button release, ending the battlefield drag operation.
    stopDrag() {
        if (this.isDraggingBattlefieldCard) {
            console.log(`Battlefield Drag End: ${this.battlefield[this.draggedBattlefieldCardIndex]?.name}`);
            this.isDraggingBattlefieldCard = false; // Clear flag
            this.draggedBattlefieldCardIndex = -1; // Clear index
            // Remove the document-level listeners.
            document.removeEventListener('mousemove', this.throttledHandleDrag);
            document.removeEventListener('mouseup', this.stopDrag);
        }
    },

    // --- Context Menu Logic ---

    // Opens the right-click context menu for a card.
    openCardMenu(event, card, zone, index) {
      event.preventDefault(); // Prevent default browser context menu.
      event.stopPropagation(); // Prevent triggering other click listeners (like zone expansion).

      let actualIndex = index; // The provided index might be visual (e.g., grouped hand)
      const zoneArray = this.getZoneArray(zone);
      if (!zoneArray) { console.error(`Invalid zone ${zone} for context menu`); return; }

      // For hand, need to find the actual index in the underlying `hand` array.
      if (zone === 'hand') {
        actualIndex = this.findCardIndexInHand(card);
      } else {
          // Verify the index still points to the correct card, find it if necessary.
          // This handles cases where the array might have changed since rendering.
          if (index >= zoneArray.length || (zoneArray[index].gameId || zoneArray[index].id) !== (card.gameId || card.id)) {
              actualIndex = zoneArray.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
          }
      }

      if (actualIndex === -1) {
          console.error(`Context menu card ${card.name} not found in ${zone}`); return;
      }

      // Store context information before calculating position.
      this.contextCard = card;
      this.contextZone = zone;
      this.contextIndex = actualIndex; // Store the verified index.

      // *** MODIFIED: Calculate context menu position dynamically ***
      const clickX = event.clientX;
      const clickY = event.clientY;
      const viewportHeight = window.innerHeight;
      const estimatedMenuHeight = 300; // Estimate menu height (adjust if needed)
      const spaceBelow = viewportHeight - clickY;
      const padding = 5; // Small gap from cursor

      let yPos;

      // If not enough space below, position above the cursor.
      if (spaceBelow < estimatedMenuHeight) {
          yPos = clickY - estimatedMenuHeight - padding;
          // Prevent menu going off the top of the screen
          if (yPos < padding) {
              yPos = padding;
          }
      } else {
          // Otherwise, position below the cursor (default).
          yPos = clickY + padding;
      }

      // Keep horizontal position simple for now (right of cursor)
      const xPos = clickX + padding;

      // Set the calculated position
      this.contextMenuPosition = { x: xPos, y: yPos };
      // *** END MODIFICATION ***

      this.showContextMenu = true; // Make the menu visible *after* setting position.
      console.log(`Context menu opened for ${card.name} in ${zone}[${actualIndex}] at (${xPos}, ${yPos})`);
    },

    // Closes the context menu and resets related state.
    closeContextMenu() {
      this.showContextMenu = false;
      this.contextCard = null;
      this.contextZone = null;
      this.contextIndex = null;
    },

    // Core logic to move the card currently targeted by the context menu.
    moveCardFromContext(targetZone, libraryPosition = 'top') { // Default libraryPosition is 'top'
      const card = this.getCardFromContext(); // Get the card details from context state
      if (!card) {
        console.error("Cannot move card, context invalid or lost.");
        this.closeContextMenu();
        return;
      }

      const sourceZone = this.contextZone; // Get source zone from context
      const sourceIndex = this.contextIndex; // Get source index from context

      // Handle token removal when moving from battlefield to non-battlefield zones.
      if (card.isToken && sourceZone === 'battlefield') {
        if (targetZone === 'hand' || targetZone === 'library' || targetZone === 'graveyard' || targetZone === 'exile') {
          console.log(`Token ${card.name} removed (moved from ${sourceZone} to ${targetZone})`);
          this.removeCardFromZone(sourceZone, sourceIndex); // Remove from source
          this.closeContextMenu();
          return; // Don't add to target
        }
      }

      // Handle commander movement and tax increase.
      if (card.isCommander) {
        // Log potential game rule interactions.
        if (targetZone === 'graveyard' || targetZone === 'exile' || targetZone === 'hand' || targetZone === 'library') {
          console.warn(`Commander ${card.name} moved to ${targetZone}. In a real game, you could choose the Command Zone instead.`);
        }
        // If moving back to the command zone from elsewhere, increase the tax.
        if(targetZone === 'command' && sourceZone !== 'command') {
          this.increaseCommanderTax(); // This also closes the context menu.
        }
      }

      // Remove the card from its original zone.
      const removedCard = this.removeCardFromZone(sourceZone, sourceIndex);
      if (!removedCard) {
        console.error(`Failed to remove ${card.name} from ${sourceZone}`);
        this.closeContextMenu();
        return;
      }

      // Get the array for the target zone.
      const targetArray = this.getZoneArray(targetZone);
      if (!targetArray) {
        console.error("Invalid target zone for move:", targetZone);
        // Put the card back if the target zone is invalid.
        this.getZoneArray(sourceZone)?.splice(sourceIndex, 0, removedCard);
        this.closeContextMenu();
        return;
      }

      // Reset card state for the new zone.
      removedCard.tapped = false;
      removedCard.position = null; // Clear absolute position

      // Add the card to the target zone based on the zone type.
      if (targetZone === 'battlefield') {
        removedCard.position = { x: 50, y: 50 }; // Default position
        targetArray.push(removedCard);
      } else if (targetZone === 'library') {
        // Logic for top/bottom placement (corrected in previous step)
        if (libraryPosition === 'bottom') {
           targetArray.unshift(removedCard); // Add to beginning (bottom)
           console.log(`Moved ${removedCard.name} to BOTTOM of library`);
        } else { // 'top' or default
           targetArray.push(removedCard); // Add to end (top, drawn by pop)
           console.log(`Moved ${removedCard.name} to TOP of library`);
        }
      } else {
        // Add to the end for hand, graveyard, exile, command zone.
        targetArray.push(removedCard);
      }

      console.log(`Moved ${removedCard.name} from ${sourceZone} to ${targetZone}`);
      this.closeContextMenu(); // Close the menu after the action.
    },

    // Context menu action: Move card to the specified zone.
    moveToZone(targetZone) {
      this.moveCardFromContext(targetZone);
    },

    // Context menu action: Move card to the top of the library.
    moveToTopOfLibrary() {
      this.moveCardFromContext('library', 'top'); // Pass 'top' explicitly
    },

    // Context menu action: Move card to the bottom of the library.
    moveToBottomOfLibrary() {
      this.moveCardFromContext('library', 'bottom'); // Pass 'bottom' explicitly
    },

    // Context menu action: Flip a double-faced card.
    flipCard() {
      const card = this.getCardFromContext();
      // Check if the card exists and has multiple faces.
      if (card && card.card_faces?.length > 1) {
         card.flipped = !card.flipped; // Toggle the flipped state
         console.log(`${card.name} flipped to ${card.flipped ? 'back' : 'front'}`);
      }
      this.closeContextMenu();
    },

    // Context menu action: Tap or untap a card on the battlefield.
    tapCard() {
      const card = this.getCardFromContext();
      // Only makes sense on the battlefield.
      if (card && this.contextZone === 'battlefield') {
         card.tapped = !card.tapped; // Toggle tapped state
         console.log(`${card.name} ${card.tapped ? 'tapped' : 'untapped'}`);
      }
      this.closeContextMenu();
    },

    // Context menu action: Add a counter to a card on the battlefield.
    addCounter() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
         // Initialize counters if undefined/null.
         if (card.counters === undefined || card.counters === null) card.counters = 0;
         card.counters++; // Increment counter
         console.log(`Added counter to ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    // Context menu action: Remove a counter from a card on the battlefield.
    removeCounter() {
      const card = this.getCardFromContext();
      // Check if card exists, is on battlefield, and has counters.
      if (card && this.contextZone === 'battlefield' && card.counters > 0) {
         card.counters--; // Decrement counter
         console.log(`Removed counter from ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    // Context menu action: Open the modal to set power/toughness.
    setPowerToughness() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        // Pre-fill the modal inputs with current P/T or empty string.
        this.newPower = card.power ?? '';
        this.newToughness = card.toughness ?? '';
        this.showPTModal = true; // Show the modal
      } else {
         this.closeContextMenu(); // Close if not applicable
      }
    },

    // Context menu action: Open the token modal pre-filled to copy the card.
    createTokenCopy() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        this.tokenName = `${card.name} Token`; // Append "Token" to the name
        this.tokenImageUrl = this.getCardImage(card); // Use the card's image
        this.tokenQuantity = 1; // Default to creating one copy
        this.showTokenModal = true; // Show the token modal
      } else {
          this.closeContextMenu();
      }
    },

    // --- Token Creation Logic ---

    // Opens the modal to create a generic token.
    addToken() {
      // Reset token form fields.
      this.tokenName = '';
      this.tokenQuantity = 1;
      this.tokenImageUrl = '';
      this.showTokenModal = true; // Show the modal
    },

    // Creates token(s) based on the modal form input and adds them to the battlefield.
    createToken() {
      // Sanitize inputs.
      const quantity = Math.max(1, Number(this.tokenQuantity) || 1);
      const name = this.tokenName.trim() || 'Token'; // Default name if empty
      const imageUrl = this.tokenImageUrl.trim() || this.defaultTokenImage; // Default image if empty

      // Create the specified number of tokens.
      for (let i = 0; i < quantity; i++) {
        const newToken = {
          name: name,
          isToken: true, // Mark as a token
          // Generate a unique ID for the token instance.
          gameId: `token-${name.replace(/\s+/g, '-')}-${Date.now()}-${i}`,
          // Use provided image URL or default.
          image_uris: { normal: imageUrl },
          // Initial state for tokens.
          tapped: false,
          flipped: false, // Tokens typically don't flip
          counters: 0,
          position: { x: 50 + i * 10, y: 50 + i * 10 }, // Stagger position slightly
          power: undefined, // Tokens often need P/T set manually unless copied
          toughness: undefined,
        };
        this.battlefield.push(newToken); // Add to battlefield
      }
      console.log(`Created ${quantity} "${name}" token(s)`);
      this.cancelTokenCreation(); // Close the modal
    },

    // Closes the token creation modal.
    cancelTokenCreation() {
      this.showTokenModal = false;
      this.closeContextMenu(); // Ensure context menu is closed if it was open
    },

    // --- Power/Toughness Setting Logic ---

    // Saves the new power/toughness from the modal to the context card.
    savePT() {
      // Re-fetch the card from context state as it might have changed.
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') { // Check context again
          // Convert empty string to undefined, otherwise parse as number.
          const power = this.newPower === '' ? undefined : Number(this.newPower);
          const toughness = this.newToughness === '' ? undefined : Number(this.newToughness);
          // Update the card's properties.
          card.power = power;
          card.toughness = toughness;
          console.log(`Set P/T for ${card.name} to ${power ?? '?'}/${toughness ?? '?'}`);
      } else {
          console.warn("Could not save P/T, context lost or invalid.");
      }
      this.cancelPT(); // Close the modal
    },

    // Closes the power/toughness modal.
    cancelPT() {
      this.showPTModal = false;
      this.closeContextMenu(); // Ensure context menu is closed
    },

    // --- Library Search Logic ---

    // Opens the library search modal and populates initial results (reversed library order).
    searchLibrary() {
      this.librarySearchQuery = ''; // Clear previous search term
      // Populate results with a reversed copy of the current library array.
      // This shows the top card (last element) first in the modal.
      this.librarySearchResults = [...this.library].reverse();
      this.showLibrarySearch = true; // Show the modal
    },

    // Filters the library search results based on user input, preserving library order then reversing for display.
    searchLibraryCards() {
      const query = this.librarySearchQuery.toLowerCase().trim();
      if (!query) {
        // If query is empty, show all library cards, reversed for top-first display.
        this.librarySearchResults = [...this.library].reverse();
      } else {
        // Filter the library based on the query, then reverse the filtered results.
        this.librarySearchResults = this.library
            .filter(card => card.name.toLowerCase().includes(query))
            .reverse(); // Reverse the filtered array
      }
    },

    // Moves a card selected from the search results to the hand and shuffles the library.
    moveSearchedCardToHand(card) {
      // Find the actual index of the card in the main library array.
      // NOTE: We search the original `this.library`, not the reversed `librarySearchResults`.
      const index = this.library.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
      if (index !== -1) {
        // Remove the card from the library.
        const [movedCard] = this.library.splice(index, 1);
        // Add the card to the hand.
        this.hand.push(movedCard);
        console.log(`Moved "${movedCard.name}" from library to hand.`);
        // Per game rules, shuffle the library after searching.
        console.log('Shuffling library after search...');
        this.shuffleDeck();
        this.closeLibrarySearch(); // Close the modal
      } else {
        // This should ideally not happen if the card came from librarySearchResults
        console.error(`Card "${card.name}" not found in library during search move.`);
      }
    },

    // Closes the library search modal and resets search state.
    closeLibrarySearch() {
      this.showLibrarySearch = false;
      this.librarySearchQuery = '';
      this.librarySearchResults = [];
    },

    // --- Utility Methods ---

    // Determines the correct image URL for a card, handling flipped state and defaults.
    getCardImage(card) {
      if (!card) return this.defaultCardBack; // Default if no card data

      try {
          // Check for flipped state and back face image.
          if (card.flipped && card.card_faces && card.card_faces.length > 1 && card.card_faces[1].image_uris) {
              return card.card_faces[1].image_uris.normal || card.card_faces[1].image_uris.large || this.defaultCardBack;
          }
          // Check for standard image URIs.
          if (card.image_uris) {
              return card.image_uris.normal || card.image_uris.large || this.defaultCardBack;
          }
          // Check for front face image if no standard URI (might be first face of MDFC).
          if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
              return card.card_faces[0].image_uris.normal || card.card_faces[0].image_uris.large || this.defaultCardBack;
          }
          // Handle tokens specifically.
          if (card.isToken) {
              return card.image_uris?.normal || this.defaultTokenImage; // Use token image or default token placeholder
          }
      } catch (e) {
          console.error("Error getting card image for:", card?.name, e);
      }

      // Fallback if no suitable image found.
      console.warn("Using default card back for card:", card?.name);
      return this.defaultCardBack;
    },

    // Returns the corresponding state array based on a zone name string.
    getZoneArray(zoneName) {
      switch (zoneName) {
        case 'hand': return this.hand;
        case 'library': return this.library;
        case 'graveyard': return this.graveyard;
        case 'exile': return this.exileZone;
        case 'command': return this.commandZone;
        case 'battlefield': return this.battlefield;
        case 'initialDraw': return this.initialHand; // Include initial hand for mulligan phase actions
        default:
          console.error(`Invalid zone name: ${zoneName}`);
          return null; // Return null for invalid zone names
      }
    },

    // Finds the index of a specific card instance within the `hand` array.
    findCardIndexInHand(cardToFind) {
      if (!cardToFind) return -1;
      // Use the unique gameId if available, otherwise fallback to card ID.
      return this.hand.findIndex(card => (card.gameId || card.id) === (cardToFind.gameId || cardToFind.id));
    },

    // Retrieves the card object currently targeted by the context menu.
    getCardFromContext() {
        // Check if context state is valid.
        if (!this.contextZone || this.contextIndex === null || this.contextIndex < 0) {
            return null; // Invalid context
        }
        const zoneArray = this.getZoneArray(this.contextZone);
        // Check if index is within bounds.
        if (!zoneArray || this.contextIndex >= zoneArray.length) {
            console.error(`Context index ${this.contextIndex} out of bounds for zone ${this.contextZone} (size ${zoneArray?.length})`);
            return null;
        }
        // Return the card at the stored context index.
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
  background-color: rgba(255, 255, 255, 0.9); /* Light semi-transparent overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.playtest-content {
  background-color: #f8f9fa; /* Light gray background */
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1); /* Softer shadow */
  width: 95vw;
  height: 95vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #dee2e6; /* Light gray border */
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #dee2e6; /* Light gray border */
  flex-shrink: 0;
}

.popup-header h2 {
  margin: 0;
  color: #495057; /* Dark gray text */
  font-size: 1.8rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6c757d; /* Medium gray */
  cursor: pointer;
  padding: 0 10px;
  line-height: 1;
  transition: color 0.2s ease;
}
.close-btn:hover {
  color: #dc3545; /* Red hover */
}

/* --- Deck Selection --- */
.deck-selection {
  text-align: center;
  margin: auto; /* Center vertically and horizontally */
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  max-width: 500px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.deck-selection h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #495057;
}
.no-decks-message {
  color: #adb5bd; /* Light gray */
}
.deck-option {
  padding: 12px 20px;
  margin: 8px 0;
  background-color: white;
  border-radius: 5px;
  border: 1px solid #dee2e6;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #495057;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.deck-option:hover {
  background-color: #f8f9fa;
  border-color: #0d6efd; /* Blue border */
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* --- Initial Draw / Mulligan --- */
.initial-draw {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%; /* Take available height */
  justify-content: center; /* Center content vertically */
  flex-grow: 1; /* Allow it to grow */
}
.initial-draw h2 {
  margin-bottom: 20px;
  flex-shrink: 0; /* Prevent shrinking */
  color: #495057;
}
.initial-draw-hand-container {
  display: flex;
  flex-wrap: wrap; /* Allow cards to wrap */
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
  max-width: 90%; /* Limit width */
  padding: 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow-y: auto; /* Allow vertical scrolling if needed */
  max-height: 60vh; /* Limit height */
}
.initial-draw .card-wrapper {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 3px solid transparent; /* Border for selection indicator */
  /* Ensure border radius includes the border width */
  border-radius: calc(var(--card-border-radius, 8px) + 3px);
  flex-shrink: 0; /* Prevent cards from shrinking */
}
.initial-draw .card-wrapper:hover {
  transform: translateY(-5px) scale(1.03); /* Slight lift and scale effect */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.initial-draw .card-wrapper.selected {
  border-color: #0d6efd; /* Blue selection indicator */
  box-shadow: 0 0 15px rgba(13, 110, 253, 0.3); /* Glow effect */
}
.initial-draw .card-image {
  width: 120px; /* Card size */
  height: auto;
  display: block;
  border-radius: var(--card-border-radius, 8px); /* Use CSS variable or default */
}
.action-buttons {
  display: flex;
  gap: 15px;
  flex-shrink: 0; /* Prevent shrinking */
  margin-top: 15px; /* Space above buttons */
}
.action-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.action-button:hover {
  transform: translateY(-2px); /* Lift effect */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
.action-button.keep { background-color: #198754; } /* Green */
.action-button.keep:hover { background-color: #157347; }
.action-button.mulligan { background-color: #dc3545; } /* Red */
.action-button.mulligan:hover { background-color: #bb2d3b; }
.action-button.draw { background-color: #0d6efd; } /* Blue */
.action-button.draw:hover { background-color: #0b5ed7; }

/* --- Main Playtest Interface Layout --- */
.playtest-interface {
  display: grid;
  grid-template-areas:
    "top top top"
    "battlefield battlefield battlefield"
    "library hand hand"; /* Library takes 1 column, Hand takes 2 */
  grid-template-rows: auto 1fr auto; /* Top/Bottom auto height, Battlefield flexible */
  grid-template-columns: auto 1fr; /* Library auto width, Hand flexible */
  gap: 15px;
  flex-grow: 1; /* Take remaining space */
  overflow: hidden; /* Prevent content overflow */
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* --- Top Row Zones (Command, Graveyard, Exile) --- */
.top-row {
  grid-area: top;
  display: flex;
  gap: 15px;
  height: 150px; /* Fixed height for the top row */
  overflow: hidden; /* Hide overflow within the row */
}
.command-zone, .graveyard, .exile-zone {
  flex: 1; /* Distribute space equally */
  background-color: white;
  padding: 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Hide internal overflow */
  border: 1px solid #dee2e6;
  cursor: pointer; /* Indicate clickable for expansion */
  transition: all 0.2s;
  position: relative; /* For absolute positioning of messages */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.top-row h3 {
  margin: 0 0 8px 0;
  text-align: center;
  font-size: 0.9rem;
  color: #495057;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 5px;
  flex-shrink: 0; /* Prevent title from shrinking */
}

.zone-header { /* Container for title and tax */
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 0 5px; /* Add some padding */
}

.zone-header h3 {
  margin: 0; /* Remove default margins */
  border-bottom: none; /* Remove border from h3 */
  padding-bottom: 0;
  flex-grow: 1; /* Allow title to take space */
  text-align: left; /* Align title left */
}


.commander-tax-display {
  background-color: #e9ecef; /* Light gray background */
  color: #495057; /* Darker text */
  padding: 3px 8px;
  border-radius: 12px; /* Pill shape */
  font-size: 0.8rem;
  font-weight: bold;
  border: 1px solid #ced4da; /* Slightly darker border */
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.05); /* Inner shadow */
  margin-left: 10px; /* Space from title */
  white-space: nowrap; /* Prevent wrapping */
}

.zone-preview {
  display: flex;
  gap: 5px;
  align-items: center; /* Align items vertically */
  justify-content: center; /* Center items horizontally */
  flex-grow: 1; /* Take available space */
  position: relative; /* For empty message positioning */
  min-height: 50px; /* Ensure minimum height */
  padding: 5px; /* Add padding */
  flex-wrap: wrap; /* Allow wrapping if many cards */
}
.zone-preview .card-wrapper {
  position: relative; /* For potential badges */
  line-height: 0; /* Prevent extra space below images */
}
.card-image.small {
  width: 50px; /* Smaller card images for preview */
  height: auto;
  border-radius: 4px;
  display: block;
  border: 1px solid #eee; /* Faint border */
}
.more-cards-indicator {
  font-size: 0.8rem;
  color: #adb5bd; /* Light gray */
  margin-left: 5px;
  align-self: flex-end; /* Align to bottom */
  padding-bottom: 5px;
}
.empty-zone-message {
  font-size: 0.85rem;
  color: #adb5bd; /* Light gray */
  text-align: center;
  width: 100%;
  position: absolute; /* Center absolutely */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 0 5px; /* Prevent text touching edges */
}

/* --- Expanded Zone View (Modal-like) --- */
.expanded-zone {
  position: fixed; /* Overlay on top */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80vw; /* Responsive width */
  max-width: 900px; /* Max width */
  height: 70vh; /* Responsive height */
  background-color: white;
  border: 2px solid #0d6efd; /* Blue border */
  border-radius: 10px;
  z-index: 1100; /* Above other elements */
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
.expanded-zone .zone-header { /* Reuse zone-header style */
  padding: 0 10px 10px; /* Adjust padding */
  border-bottom: 1px solid #dee2e6; /* Add border */
  flex-shrink: 0; /* Prevent shrinking */
}
.expanded-zone .commander-tax-display { /* Style tax display in expanded view */
  font-size: 0.9rem;
  padding: 4px 10px;
}
.expanded-cards {
  flex-grow: 1; /* Take available space */
  overflow-y: auto; /* Enable vertical scrolling */
  display: flex;
  flex-wrap: wrap; /* Allow cards to wrap */
  gap: 15px; /* Space between cards */
  padding: 15px; /* Padding inside the scroll area */
  background-color: #f8f9fa; /* Light background for contrast */
  border-radius: 6px;
  justify-content: center; /* Center cards horizontally */
  align-content: flex-start; /* Align wrapped lines to the top */
}
.expanded-zone .card-wrapper {
  position: relative; /* For potential future elements */
  line-height: 0;
}
.expanded-zone .card-image {
  width: 130px; /* Larger cards in expanded view */
  height: auto;
  border-radius: 6px;
  display: block;
  cursor: grab; /* Indicate draggable */
  border: 1px solid #dee2e6;
}
.expanded-zone .card-image:active {
  cursor: grabbing; /* Indicate dragging */
}
.collapse-button {
  margin-top: 15px; /* Space above button */
  padding: 8px 15px;
  background-color: #0d6efd; /* Blue */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  align-self: center; /* Center button horizontally */
  transition: all 0.2s;
  flex-shrink: 0; /* Prevent shrinking */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.collapse-button:hover {
  background-color: #0b5ed7;
  transform: translateY(-2px);
}
.expanded-zone .empty-zone-message {
  position: static; /* Reset absolute positioning */
  transform: none;
  font-size: 1rem;
  color: #adb5bd;
  margin: auto; /* Center within the flex container */
  width: 100%;
  text-align: center;
}
/* Removed absolute positioned commander tax in expanded view, handled in header */

/* --- Battlefield --- */
.battlefield {
  grid-area: battlefield;
  border-radius: 8px;
  padding: 15px;
  position: relative; /* For absolute positioning of cards and button */
  overflow: hidden; /* Hide overflow */
  border: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  background-color: #e9ecef; /* Slightly different background */
}
.battlefield h3 {
  margin: 0 0 10px 0;
  text-align: center;
  color: #495057;
  flex-shrink: 0; /* Prevent title shrinking */
}
.battlefield-cards {
  position: relative; /* Container for absolutely positioned cards */
  width: 100%;
  flex-grow: 1; /* Take available space */
  overflow: auto; /* Allow scrolling if cards overflow */
  min-height: 200px; /* Ensure minimum height */
  border-radius: 4px;
  background-color: white; /* White background for card area */
  border: 1px solid #ced4da;
}
.battlefield-card {
  /* Use !important cautiously, ensure it's necessary for overriding */
  position: absolute !important;
  cursor: grab; /* Indicate draggable */
  transition: transform 0.2s ease-in-out; /* Smooth rotation for tapping */
  z-index: 1; /* Base z-index */
  width: 100px; /* Set width here */
  height: auto; /* Maintain aspect ratio */
  line-height: 0; /* Prevent extra space */
}
.battlefield-card:active {
  cursor: grabbing; /* Indicate dragging */
  z-index: 10; /* Bring to front when dragging */
}
.battlefield-card .card-image {
  width: 100%; /* Image takes full width of wrapper */
  height: auto;
  border-radius: 5px;
  display: block;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  user-select: none; /* Prevent image selection */
  -webkit-user-drag: none; /* Prevent native image dragging */
  border: 1px solid rgba(0,0,0,0.1); /* Faint border */
}
.counter-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #dc3545; /* Red */
  color: white;
  border-radius: 50%; /* Circle shape */
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.8rem;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  z-index: 2; /* Above card image */
  pointer-events: none; /* Allow clicks through to card */
}
.pt-indicator {
  position: absolute;
  bottom: 3px;
  left: 3px;
  background-color: rgba(248, 249, 250, 0.9); /* Semi-transparent light background */
  color: #495057; /* Dark text */
  font-size: 0.8rem;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
  z-index: 2; /* Above card image */
  border: 1px solid #dee2e6;
  pointer-events: none; /* Allow clicks through */
}
.token-button {
  position: absolute; /* Position relative to battlefield */
  bottom: 10px;
  right: 10px;
  padding: 6px 12px;
  background-color: #6f42c1; /* Purple */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 20; /* Above cards */
  font-size: 0.9rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.token-button:hover {
  background-color: #5a32a3;
  transform: translateY(-2px);
}

/* --- Bottom Row (Library, Hand) --- */
.bottom-row {
  /* Spans the grid areas defined in playtest-interface */
  grid-area: library / library / hand / hand;
  display: flex;
  gap: 15px;
  height: 180px; /* Fixed height for the bottom row */
}
.library {
  grid-area: library; /* Assign to grid area */
  background-color: white;
  padding: 10px; /* Consistent padding */
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between; /* Space out title, image, button */
  width: 150px; /* Fixed width */
  flex-shrink: 0; /* Prevent shrinking */
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.library h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #495057;
  width: 100%;
  text-align: center;
  flex-shrink: 0;
}
.library-image {
  width: 80px; /* Size of the deck image */
  height: auto;
  border-radius: 5px;
  cursor: pointer; /* Indicate clickable for search */
  margin-bottom: 5px;
  transition: all 0.2s;
  flex-shrink: 0;
  border: 1px solid #dee2e6;
}
.library-image:hover {
  transform: scale(1.05); /* Slight scale effect */
  box-shadow: 0 0 10px rgba(13, 110, 253, 0.2); /* Blue glow */
}
.draw-button {
  padding: 6px 10px;
  width: 80%; /* Relative width */
  font-size: 0.9rem;
  background-color: #0d6efd; /* Blue */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.draw-button:hover {
  background-color: #0b5ed7;
  transform: translateY(-2px);
}

.hand-zone {
  grid-area: hand; /* Assign to grid area */
  background-color: white;
  padding: 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Take remaining horizontal space */
  overflow: hidden; /* Hide overflow */
  border: 1px solid #dee2e6;
  position: relative; /* For empty message */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.hand-zone h3 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: #495057;
  text-align: center;
  flex-shrink: 0;
}
.hand-cards {
  display: flex;
  gap: 10px; /* Space between cards/groups */
  padding-bottom: 10px; /* Space at the bottom */
  align-items: flex-start; /* Align cards to the top */
  flex-grow: 1; /* Take available vertical space */
  overflow-x: auto; /* Enable horizontal scrolling */
  overflow-y: hidden; /* Disable vertical scrolling */
  min-height: 120px; /* Minimum height for the card area */
}
.hand-zone .card-wrapper {
  position: relative; /* For quantity badge */
  flex-shrink: 0; /* Prevent cards from shrinking */
  line-height: 0;
}
.hand-zone .card-image {
  width: 90px; /* Card size in hand */
  height: auto;
  border-radius: 5px;
  display: block;
  cursor: grab; /* Indicate draggable */
  transition: all 0.1s ease;
  border: 1px solid rgba(0,0,0,0.1); /* Faint border */
}
.hand-zone .card-image:active {
  cursor: grabbing;
  transform: scale(0.95); /* Slight shrink effect when grabbed */
}
.quantity-badge {
  position: absolute;
  top: -5px;
  left: -5px;
  background-color: #0d6efd; /* Blue */
  color: white;
  border-radius: 50%; /* Circle */
  width: 18px;
  height: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.75rem;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  z-index: 2; /* Above card */
  pointer-events: none; /* Allow clicks through */
}
.hand-zone .empty-zone-message {
  position: absolute; /* Center message */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.9rem;
  color: #adb5bd;
}

/* --- Context Menu --- */
.context-menu {
  position: fixed; /* Position relative to viewport */
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* Soft shadow */
  z-index: 1200; /* Above expanded zones */
  padding: 5px 0; /* Vertical padding */
  min-width: 180px; /* Minimum width */
}
.context-menu-item {
  padding: 8px 15px; /* Padding within items */
  color: #495057; /* Text color */
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.15s ease;
  white-space: nowrap; /* Prevent text wrapping */
}
.context-menu-item:hover {
  background-color: #f8f9fa; /* Light gray hover */
  color: #0d6efd; /* Blue text hover */
}
.context-menu-divider {
  height: 1px;
  background-color: #dee2e6; /* Separator line */
  margin: 5px 0; /* Space around divider */
}

/* --- Modals (Token, P/T, Library Search) --- */
.modal-overlay {
  position: fixed; /* Full screen overlay */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent white */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050; /* Below context menu, above most content */
  padding: 20px; /* Padding for smaller screens */
}
.modal-content {
  background-color: white;
  padding: 25px 30px;
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #dee2e6;
  color: #495057;
  max-height: 85vh; /* Limit height */
  display: flex;
  flex-direction: column;
  width: 90%; /* Responsive width */
  max-width: 600px; /* Max width for general modals */
}
.modal-content h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #0d6efd; /* Blue title */
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
  flex-shrink: 0; /* Prevent shrinking */
}
.token-form, .pt-form {
  display: flex;
  flex-direction: column;
  gap: 15px; /* Space between form elements */
  overflow-y: auto; /* Allow scrolling if form is long */
  padding-right: 5px; /* Space for scrollbar */
}
.modal-content label {
  display: flex;
  flex-direction: column; /* Stack label text above input */
  align-items: flex-start;
  gap: 5px; /* Space between label text and input */
  font-size: 0.95rem;
}
.modal-content input[type="text"],
.modal-content input[type="number"] {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #dee2e6;
  background-color: white;
  color: #495057;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box; /* Include padding/border in width */
}
.modal-buttons {
  display: flex;
  justify-content: flex-end; /* Align buttons to the right */
  gap: 12px; /* Space between buttons */
  margin-top: 25px; /* Space above buttons */
  padding-top: 15px; /* Space below form */
  border-top: 1px solid #dee2e6; /* Separator line */
  flex-shrink: 0; /* Prevent shrinking */
}
.modal-buttons button {
  padding: 9px 18px;
  border: none;
  border-radius: 5px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #fff;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.modal-buttons button:hover {
  transform: translateY(-1px); /* Slight lift */
}
.confirm-button { background-color: #198754; } /* Green */
.confirm-button:hover { background-color: #157347; }
.cancel-button { background-color: #6c757d; } /* Gray */
.cancel-button:hover { background-color: #5c636a; }

/* --- Library Search Modal Specific Styles --- */
.library-search-modal {
  width: 85vw; /* Wider modal for search results */
  max-width: 1000px;
}
.library-search-input {
  width: 100%;
  margin-bottom: 15px;
  padding: 10px;
  box-sizing: border-box;
  flex-shrink: 0;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 1rem;
}
.search-results {
  flex-grow: 1; /* Take available space */
  overflow-y: auto; /* Vertical scroll */
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 15px;
  display: grid; /* Grid layout for results */
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); /* Responsive columns */
  gap: 1rem; /* Space between grid items */
  margin-bottom: 1rem; /* Space below results */
  max-height: 55vh; /* Limit height */
  min-height: 150px; /* Minimum height */
  position: relative; /* For empty message */
}
.search-result-card {
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem; /* Space between image and name */
  background-color: white;
  padding: 5px;
  border-radius: 4px;
}
.search-result-card:hover {
  transform: scale(1.04); /* Scale effect */
  box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* Shadow on hover */
  background-color: #f8f9fa; /* Light background hover */
}
.search-card-image {
  width: 100%; /* Image takes full width of card */
  height: auto;
  border-radius: 6px;
  display: block;
  border: 1px solid #dee2e6;
}
.search-result-card span {
  font-size: 0.8rem; /* Smaller text for card name */
  color: #495057;
  word-break: break-word; /* Allow long names to wrap */
  margin-top: 4px;
}
.library-search-buttons {
  justify-content: space-between; /* Space out Shuffle and Close buttons */
}
.library-search-modal .empty-zone-message {
  grid-column: 1 / -1; /* Span all columns */
  text-align: center;
  font-size: 1rem;
  color: #adb5bd;
  margin: auto; /* Center vertically and horizontally */
  position: absolute; /* Center within the grid */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: calc(100% - 30px); /* Account for padding */
}

/* --- Loading State --- */
.loading {
  margin: auto; /* Center loading text */
  font-size: 1.5rem;
  color: #adb5bd;
}

/* --- General Card Wrapper --- */
.card-wrapper {
  position: relative; /* Base for absolute positioned elements like badges */
  line-height: 0; /* Prevent extra space below images */
}

/* --- Responsive Styles --- */
@media (max-width: 1200px) {
  .playtest-content {
      width: 98vw;
      height: 98vh;
      padding: 15px;
  }
  .expanded-zone { width: 90vw; }
  .library-search-modal { width: 90vw; }
  .initial-draw .card-image { width: 100px; }
  .battlefield-card { width: 90px; } /* Adjust battlefield card width */
  .hand-zone .card-image { width: 80px; }
}

@media (max-width: 768px) {
  .top-row { height: 120px; }
  .bottom-row { height: 150px; }
  .library { width: 120px; }
  .library-image { width: 65px; }
  .draw-button { width: 90%; font-size: 0.8rem; padding: 5px 8px; }
  .initial-draw .card-image { width: 80px; }
  .battlefield-card { width: 75px; } /* Adjust battlefield card width */
  .hand-zone .card-image { width: 70px; }
  .hand-cards { gap: 5px; }
  .expanded-zone { width: 95vw; height: 75vh; }
  .expanded-zone .card-image { width: 100px; }
  .library-search-modal { width: 95vw; }
  .search-results { grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 0.8rem; }
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
  .battlefield-card { width: 65px; } /* Adjust battlefield card width */
  .hand-zone .card-image { width: 60px; }
  .counter-badge { width: 16px; height: 16px; font-size: 0.7rem; }
  .pt-indicator { font-size: 0.7rem; padding: 1px 3px; }
  .quantity-badge { width: 16px; height: 16px; font-size: 0.7rem; }
  .action-buttons { gap: 10px; }
  .action-button { padding: 6px 12px; font-size: 0.8rem; }
  .modal-buttons { gap: 8px; }
  .modal-buttons button { padding: 7px 14px; font-size: 0.85rem; }
  .search-results { grid-template-columns: repeat(auto-fill, minmax(75px, 1fr)); gap: 0.5rem; }
  .search-result-card span { font-size: 0.75rem; }
  .modal-content { max-width: 95%; }
}
</style>
