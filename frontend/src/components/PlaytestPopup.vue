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
                   transform: card.tapped ? 'rotate(90deg)' : 'none',
                   left: card.position?.x + 'px',
                   top: card.position?.y + 'px',
                   position: 'absolute' // Ensure position is absolute
                 }"
                 @mousedown="startDrag($event, card, index)"
                 @mouseup="stopDrag"
                 @mousemove="throttledHandleDrag($event)"> <img :src="getCardImage(card)"
                   :alt="card.name"
                   class="card-image"
                   draggable="true" @dragstart="dragStart($event, card, 'battlefield', index)"
                   @contextmenu.prevent="openCardMenu($event, card, 'battlefield', index)">
              <div v-if="card.counters > 0" class="counter-badge">
                {{ card.counters }}
              </div>
              <div v-if="card.power !== undefined || card.toughness !== undefined" class="pt-indicator">
                {{ card.power ?? '?' }}/{{ card.toughness ?? '?' }} </div>
            </div>
          </div>
          <button @click="addToken" class="token-button">Add Token</button>
        </div>

        <div class="hand-zone" @drop="dropCard($event, 'hand')" @dragover.prevent>
          <h3>Hand ({{ hand.length }})</h3>
          <div class="hand-cards">
            <div v-for="(cardGroup, index) in groupedHand" :key="'hand-' + (cardGroup.card.gameId || index)" class="card-wrapper"> <img :src="getCardImage(cardGroup.card)"
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
        </div>

        <div v-if="showContextMenu && contextCard"
             class="context-menu"
             :style="{ top: contextMenuPosition.y + 'px', left: contextMenuPosition.x + 'px' }"
             @click.stop> <div v-if="contextZone !== 'battlefield'" class="context-menu-item" @click="moveToZone('battlefield')">
            Move to Battlefield
          </div>
          <div v-if="contextZone !== 'exile'" class="context-menu-item" @click="moveToZone('exile')">
            Move to Exile
          </div>
          <div v-if="contextZone !== 'graveyard'" class="context-menu-item" @click="moveToZone('graveyard')">
            Move to Graveyard
          </div>
          <div v-if="contextZone !== 'command' && !contextCard?.isToken" class="context-menu-item" @click="moveToZone('command')"> Move to Command Zone
          </div>
          <div v-if="contextZone !== 'hand' && !contextCard?.isToken" class="context-menu-item" @click="moveToZone('hand')"> Move to Hand
          </div>
          <div v-if="contextZone !== 'library' && !contextCard?.isToken" class="context-menu-item" @click="moveToTopOfLibrary"> Put on Top of Library
          </div>
          <div v-if="contextZone !== 'library' && !contextCard?.isToken" class="context-menu-item" @click="moveToBottomOfLibrary"> Put on Bottom of Library
          </div>
          <div v-if="contextCard?.isCommander" class="context-menu-item" @click="increaseCommanderTax">
            Increase Commander Tax (+2)
          </div>
          <div class="context-menu-divider"></div>
          <div v-if="contextCard?.card_faces?.length > 1" class="context-menu-item" @click="flipCard">Flip Card</div> <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="tapCard">
            {{ contextCard.tapped ? 'Untap' : 'Tap' }}
          </div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="addCounter">Add Counter</div>
          <div v-if="contextZone === 'battlefield' && contextCard?.counters > 0" class="context-menu-item" @click="removeCounter">Remove Counter</div> <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="setPowerToughness">Set Power/Toughness</div>
          <div v-if="contextZone === 'battlefield'" class="context-menu-item" @click="createTokenCopy">Create Token Copy</div>
        </div>

        <div v-if="showTokenModal" class="modal-overlay" @click="cancelTokenCreation"> <div class="modal-content token-modal" @click.stop> <h3>Create Token</h3>
            <div class="token-form">
              <label>
                Token Name:
                <input v-model="tokenName" type="text" placeholder="E.g., Soldier, Goblin">
              </label>
              <label>
                Quantity:
                <input v-model.number="tokenQuantity" type="number" min="1" max="100"> </label>
              <label>
                Image URL (optional):
                <input v-model="tokenImageUrl" type="text" placeholder="Paste image URL">
              </label>
              <div class="modal-buttons token-modal-buttons">
                <button @click="createToken" class="confirm-button">Create</button>
                <button @click="cancelTokenCreation" class="cancel-button">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showPTModal" class="modal-overlay" @click="cancelPT"> <div class="modal-content pt-modal" @click.stop> <h3>Set Power/Toughness for {{ contextCard?.name }}</h3>
            <div class="pt-form">
              <label>
                Power:
                <input v-model.number="newPower" type="number"> </label>
              <label>
                Toughness:
                <input v-model.number="newToughness" type="number"> </label>
              <div class="modal-buttons pt-modal-buttons">
                <button @click="savePT" class="confirm-button">Save</button>
                <button @click="cancelPT" class="cancel-button">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showLibrarySearch" class="modal-overlay" @click="closeLibrarySearch"> <div class="modal-content library-search-modal" @click.stop> <h3>Search Library ({{ library.length }} cards)</h3>
            <input v-model="librarySearchQuery"
                   type="text"
                   placeholder="Search for a card..."
                   @input="searchLibraryCards"
                   class="library-search-input">
            <div class="search-results">
              <div v-for="card in librarySearchResults"
                   :key="'search-' + (card.gameId || card.id)" class="search-result-card"
                   @click="moveSearchedCardToHand(card)"> <img :src="getCardImage(card)"
                     :alt="card.name"
                     class="search-card-image">
                <span>{{ card.name }}</span>
              </div>
               <div v-if="librarySearchResults.length === 0 && librarySearchQuery" class="empty-zone-message">
                 No matching cards found.
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
// Simple throttle function
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
    // Array of available decks passed as a prop
    decks: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedDeckId: null, // Changed name for clarity
      phase: 'select', // Current phase: 'select', 'initialDraw', 'playtest'
      initialHand: [], // Cards shown during the initial draw phase
      selectedCards: [], // Indices of cards selected for mulligan
      loading: true, // Indicates if decks are being loaded initially

      // --- Game State Zones ---
      hand: [],
      library: [],
      graveyard: [],
      exileZone: [],
      commandZone: [],
      battlefield: [], // Array of cards on the battlefield { cardData, tapped, counters, position: {x, y}, ... }

      // --- UI State ---
      isZoneExpanded: { // Tracks which zones are in expanded view
        command: false,
        exile: false,
        graveyard: false
      },
      isInitialized: false, // Flag to prevent rendering before mount

      // --- Drag and Drop State ---
      draggedCard: null,      // The card object being dragged
      draggedFromZone: null,  // The zone the card came from ('hand', 'battlefield', etc.)
      draggedFromIndex: null, // The index within the source zone array
      // Battlefield specific dragging
      isDraggingBattlefieldCard: false, // Flag for dragging cards *within* the battlefield
      draggedBattlefieldCardIndex: -1, // Index of the card being dragged on the battlefield
      dragStartOffset: { x: 0, y: 0 }, // Offset from mouse click to card top-left

      // --- Context Menu State ---
      showContextMenu: false,
      contextMenuPosition: { x: 0, y: 0 },
      contextCard: null,      // The card the context menu is for
      contextZone: null,      // The zone the context card is in
      contextIndex: null,     // The index of the context card in its zone

      // --- Modal States ---
      showTokenModal: false,
      tokenName: '',
      tokenQuantity: 1,
      tokenImageUrl: '',

      showPTModal: false,
      newPower: 0,
      newToughness: 0,

      showLibrarySearch: false,
      librarySearchQuery: '',
      librarySearchResults: [],

      // --- Game Logic State ---
      commanderTax: 0,
      mulliganCount: 0,

      // --- Internal State ---
      contextMenuCloseHandler: null, // Reference to the click listener for closing the context menu
      defaultCardBack: require('@/assets/cards/mtg-card-back.jpg'), // Cache default card back
      defaultTokenImage: require('@/assets/cards/mtg-token-default.jpg'), // Cache default token image
      dragThrottleTimeout: null, // Timeout reference for throttling drag events

    }
  },
  computed: {
    // Groups cards in hand by name/ID for display purposes
    groupedHand() {
      const groups = [];
      const cardMap = new Map(); // Use Map for better performance

      this.hand.forEach(card => {
        // Use a reliable key, preferring gameId if available
        const key = card.gameId || card.id || card.name;
        if (cardMap.has(key)) {
          cardMap.get(key).count++;
        } else {
          // Store the first instance of the card in the group
          const group = { card: card, count: 1 };
          cardMap.set(key, group);
          groups.push(group);
        }
      });

      return groups;
    }
  },
  created() {
    // Create throttled version of handleDrag for performance
    this.throttledHandleDrag = throttle(this.handleDrag, 16); // Throttle to roughly 60fps
  },
  mounted() {
    console.log('PlaytestPopup mounted');
    // Delay initialization slightly to ensure DOM is ready
    this.$nextTick(() => {
        this.isInitialized = true;
        this.loading = false; // Assume decks are loaded if passed via props
    });
    // Add listener to close context menu on clicks outside
    this.contextMenuCloseHandler = (event) => {
      // Check if the click target is outside the context menu
      if (this.showContextMenu && !event.target.closest('.context-menu')) {
        this.closeContextMenu();
      }
    };
    document.addEventListener('click', this.contextMenuCloseHandler);
  },

  beforeUnmount() {
    console.log('PlaytestPopup unmounting');
    // Clean up event listeners and timers
    document.removeEventListener('click', this.contextMenuCloseHandler);
    document.removeEventListener('mousemove', this.throttledHandleDrag);
    document.removeEventListener('mouseup', this.stopDrag);
    if (this.dragThrottleTimeout) {
        clearTimeout(this.dragThrottleTimeout);
    }
    this.cleanup(); // Perform other cleanup tasks
  },

  methods: {
    // --- Popup Lifecycle ---
    closePopup() {
      this.cleanup(); // Reset state before closing
      this.$emit('close'); // Emit close event to parent
    },

    cleanup() {
      console.log('Cleaning up PlaytestPopup state');
      // Reset all game state variables to initial values
      this.hand = [];
      this.library = [];
      this.graveyard = [];
      this.exileZone = [];
      this.battlefield = [];
      this.commandZone = [];
      this.initialHand = [];
      this.selectedCards = [];
      this.selectedDeckId = null;
      this.phase = 'select';
      this.commanderTax = 0;
      this.mulliganCount = 0;
      this.closeContextMenu(); // Ensure context menu is closed
      // Reset modal states
      this.showTokenModal = false;
      this.showPTModal = false;
      this.showLibrarySearch = false;
      // Reset zone expansion
      this.isZoneExpanded = { command: false, exile: false, graveyard: false };
    },

    // --- Deck Loading and Setup ---
    selectAndLoadDeck(deckId) {
      console.log('Selecting deck:', deckId);
      this.selectedDeckId = deckId;
      this.loadDeck();
    },

    loadDeck() {
      try {
        if (!this.selectedDeckId) {
          console.error('No deck selected');
          return;
        }
        const deck = this.decks.find(d => d.id === this.selectedDeckId);
        if (!deck) {
          console.error('Selected deck not found:', this.selectedDeckId);
          return;
        }
        console.log('Loading deck:', deck.name);

        // Reset game state thoroughly
        this.cleanup(); // Use cleanup to reset most things
        this.phase = 'loading'; // Indicate loading state

        // Deep copy deck data to prevent modifying original prop
        const deckData = JSON.parse(JSON.stringify(deck));

        // Prepare library cards
        const libraryCards = [];
        if (deckData.cards && Array.isArray(deckData.cards)) {
          deckData.cards.forEach((cardData, cardIndex) => {
            // Skip if this card is the commander
            if (deckData.commander && cardData.id === deckData.commander.id) {
              return;
            }
            const count = cardData.count || cardData.quantity || 1;
            for (let i = 0; i < count; i++) {
              // Create unique instance for each copy with a gameId
              libraryCards.push({
                ...cardData,
                gameId: `card-${cardData.id}-${cardIndex}-${i}-${Date.now()}`, // More unique ID
                tapped: false,
                flipped: false,
                counters: 0,
                position: null, // Initialize position as null
                power: cardData.power, // Ensure base P/T is stored
                toughness: cardData.toughness,
              });
            }
          });
          this.library = libraryCards;
        } else {
          console.warn('Deck has no cards or cards is not an array:', deckData);
          this.library = []; // Ensure library is an empty array
        }

        // Set up commander
        if (deckData.commander) {
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
        } else {
            this.commandZone = []; // Ensure command zone is empty
        }

        // Shuffle and draw initial hand
        this.shuffleDeck();
        this.drawInitialHand();
        this.phase = 'initialDraw'; // Move to initial draw phase

        console.log('Deck loaded:', { library: this.library.length, hand: this.initialHand.length, commander: this.commandZone.length });

      } catch (error) {
        console.error('Error in loadDeck:', error);
        this.phase = 'select'; // Revert to selection on error
      }
    },

    shuffleDeck() {
      // Fisher-Yates shuffle algorithm
      for (let i = this.library.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [this.library[i], this.library[j]] = [this.library[j], this.library[i]];
      }
      console.log('Deck shuffled');
    },

    shuffleLibrary() {
        this.shuffleDeck();
        // Optionally close the search modal after shuffling
        // this.closeLibrarySearch();
    },

    // --- Initial Draw and Mulligan ---
    drawInitialHand() {
      this.initialHand = [];
      this.selectedCards = []; // Reset selections
      const handSize = 7;
      for (let i = 0; i < handSize; i++) {
        if (this.library.length > 0) {
          this.initialHand.push(this.library.pop());
        } else {
            console.warn("Library empty during initial draw");
            break; // Stop if library is empty
        }
      }
    },

    toggleCardSelect(index) {
      const idx = this.selectedCards.indexOf(index);
      if (idx === -1) {
        // Select card if not already selected
        this.selectedCards.push(index);
      } else {
        // Deselect card if already selected
        this.selectedCards.splice(idx, 1);
      }
    },

    keepHand() {
      // Move cards from initialHand to the actual hand zone
      this.hand = [...this.initialHand];
      this.initialHand = []; // Clear initial hand display
      this.phase = 'playtest'; // Start the playtest
    },

    mulligan() {
        // Basic Mulligan (London Mulligan): Shuffle hand back, draw N-1 cards.
        this.mulliganCount++;
        const newHandSize = 7; // Always draw 7 initially
        const cardsToKeep = newHandSize - this.mulliganCount;

        if (cardsToKeep < 0) {
            console.log("Cannot mulligan further.");
            // Optionally, force keep or handle differently
            this.keepHand(); // For now, just keep the current hand
            return;
        }

        // Return current hand to library
        this.library.push(...this.initialHand);
        this.initialHand = [];
        this.shuffleDeck();

        // Draw new hand of 7
        for (let i = 0; i < newHandSize; i++) {
            if (this.library.length > 0) {
                this.initialHand.push(this.library.pop());
            } else {
                 console.warn("Library empty during mulligan draw");
                 break;
            }
        }

        // Prompt to put back 'mulliganCount' cards (this part needs UI implementation)
        alert(`Mulligan ${this.mulliganCount}. Drawn ${this.initialHand.length} cards. You must put ${this.mulliganCount} card(s) on the bottom of your library.`);
        // TODO: Implement UI for selecting cards to bottom.
        // For now, just proceed to keep phase, user needs to manually bottom cards later via context menu.
        // This simplification avoids complex UI state for selection during mulligan.
        this.phase = 'initialDraw'; // Stay in initial draw phase to allow keeping/drawing
        this.selectedCards = []; // Reset selections for the new hand
    },

    // --- Core Gameplay Actions ---
    drawCard() {
      if (this.library.length > 0) {
        const drawnCard = this.library.pop();
        // Determine target zone based on phase
        if (this.phase === 'initialDraw') {
            this.initialHand.push(drawnCard);
        } else if (this.phase === 'playtest') {
            this.hand.push(drawnCard);
        }
      } else {
        console.warn('Cannot draw, library is empty!');
        // Optionally add a game loss state or notification
      }
    },

    // --- Zone Expansion ---
    toggleZoneExpansion(zone) {
      // Toggle the specified zone's expansion state
      this.isZoneExpanded[zone] = !this.isZoneExpanded[zone];
      console.log(`Toggled ${zone} expansion to:`, this.isZoneExpanded[zone]);
    },

    // --- Drag and Drop ---
    dragStart(event, card, zone, index) {
        // Standard HTML drag/drop start
        console.log(`Drag Start: ${card.name} from ${zone}[${index}]`);
        event.dataTransfer.setData('text/plain', JSON.stringify({ cardId: card.gameId || card.id, zone, index })); // Pass necessary info
        event.dataTransfer.effectAllowed = 'move';
        this.draggedCard = card; // Keep track locally if needed, but rely on dataTransfer
        this.draggedFromZone = zone;
        this.draggedFromIndex = index; // Store original index
    },

    dropCard(event, targetZone) {
        // Standard HTML drag/drop drop handler
        event.preventDefault();
        console.log(`Drop on: ${targetZone}`);
        try {
            const data = JSON.parse(event.dataTransfer.getData('text/plain'));
            const { cardId, zone: sourceZone, index: sourceIndex } = data;

            console.log(`Dropped card: ${cardId} from ${sourceZone}[${sourceIndex}] to ${targetZone}`);

            // Find the card in the source zone using gameId or id
            let cardToMove;
            let actualSourceIndex = -1; // Recalculate index in case array changed

            const sourceArray = this.getZoneArray(sourceZone);
            if (!sourceArray) {
                console.error("Invalid source zone:", sourceZone);
                return;
            }

            actualSourceIndex = sourceArray.findIndex(c => (c.gameId || c.id) === cardId);

            if (actualSourceIndex === -1) {
                console.error(`Card ${cardId} not found in source zone ${sourceZone}.`);
                // Attempt to use the original index as a fallback, though less reliable
                if (sourceIndex < sourceArray.length && (sourceArray[sourceIndex].gameId || sourceArray[sourceIndex].id) === cardId) {
                    actualSourceIndex = sourceIndex;
                    console.warn("Falling back to original index for card move.");
                } else {
                    return; // Card truly not found
                }
            }

            // Remove card from source zone
            cardToMove = sourceArray.splice(actualSourceIndex, 1)[0];

            if (!cardToMove) {
                console.error("Failed to extract card from source zone.");
                return;
            }

            // --- Handle Token Rules ---
            if (cardToMove.isToken) {
                // Tokens cease to exist if moved to Hand or Library
                if (targetZone === 'hand' || targetZone === 'library') {
                    console.log(`Token ${cardToMove.name} removed (moved to ${targetZone})`);
                    this.draggedCard = null; // Clear drag state
                    return; // Do not add the token to the target zone
                }
                // Tokens moving to Graveyard or Exile also cease to exist *after* triggers resolve.
                // For simplicity in playtesting, we'll remove them immediately unless they go to Battlefield or Command.
                 if (targetZone === 'graveyard' || targetZone === 'exile') {
                    console.log(`Token ${cardToMove.name} removed (moved to ${targetZone})`);
                    this.draggedCard = null; // Clear drag state
                     // TODO: In a real game, triggers would happen first.
                    return;
                 }
            }

            // Add card to target zone
            const targetArray = this.getZoneArray(targetZone);
            if (!targetArray) {
                 console.error("Invalid target zone:", targetZone);
                 // Optionally put the card back in the source zone or handle error
                 sourceArray.splice(actualSourceIndex, 0, cardToMove); // Put back
                 return;
            }

            // Reset card state when moving zones (optional, depends on game rules)
            cardToMove.tapped = false;
            // cardToMove.counters = 0; // Usually counters stay, depends on effect
            cardToMove.position = null; // Reset position unless moving to battlefield

            if (targetZone === 'battlefield') {
                // Place card near the drop point (adjusting for scroll and element position)
                const battlefieldRect = event.currentTarget.getBoundingClientRect();
                cardToMove.position = {
                    x: event.clientX - battlefieldRect.left,
                    y: event.clientY - battlefieldRect.top
                };
                targetArray.push(cardToMove);
            } else if (targetZone === 'library') {
                // Add to top of library by default on drop
                 targetArray.unshift(cardToMove); // Add to top
            } else {
                targetArray.push(cardToMove); // Add to end for hand, graveyard, exile, command
            }

            console.log(`Moved ${cardToMove.name} to ${targetZone}`);

        } catch (e) {
            console.error("Error processing drop event:", e);
        } finally {
            // Clear drag state regardless of success/failure
            this.draggedCard = null;
            this.draggedFromZone = null;
            this.draggedFromIndex = null;
        }
    },

    // --- Battlefield Card Dragging (Internal to Battlefield) ---
    startDrag(event, card, index) {
        // Check if it's a left-click specifically for battlefield dragging
        if (event.button !== 0) return;

        // Prevent interfering with standard HTML drag/drop for moving *between* zones
        // We only activate this internal drag if the target is the battlefield card itself.
        if (event.target.closest('.battlefield-card')) {
            console.log(`Battlefield Drag Start: ${card.name}`);
            this.isDraggingBattlefieldCard = true;
            this.draggedBattlefieldCardIndex = index;

            // Ensure position exists
            if (!card.position) {
                // Estimate initial position if null (e.g., center of battlefield)
                const battlefieldRect = this.$el.querySelector('.battlefield-cards').getBoundingClientRect();
                card.position = { x: battlefieldRect.width / 2, y: battlefieldRect.height / 2 };
            }

            // Calculate offset from mouse click to top-left corner of the card element
            const cardRect = event.target.closest('.battlefield-card').getBoundingClientRect();
            this.dragStartOffset = {
                x: event.clientX - cardRect.left,
                y: event.clientY - cardRect.top
            };

            // Add listeners to the document for move and up events
            document.addEventListener('mousemove', this.throttledHandleDrag);
            document.addEventListener('mouseup', this.stopDrag);

            // Prevent default browser drag behavior ONLY for battlefield internal drag
            event.preventDefault();
        } else {
             // If not clicking directly on a battlefield card, allow standard drag/drop to proceed
             this.dragStart(event, card, 'battlefield', index);
        }
    },

    handleDrag(event) {
        // Handles mouse movement ONLY when dragging a battlefield card internally
        if (!this.isDraggingBattlefieldCard || this.draggedBattlefieldCardIndex < 0) return;

        const card = this.battlefield[this.draggedBattlefieldCardIndex];
        if (!card) return; // Safety check

        // Calculate new position relative to the battlefield container
        const battlefieldRect = this.$el.querySelector('.battlefield-cards').getBoundingClientRect();
        const newX = event.clientX - battlefieldRect.left - this.dragStartOffset.x;
        const newY = event.clientY - battlefieldRect.top - this.dragStartOffset.y;

        // Update card position reactively
        // Use Vue.set or direct assignment if reactivity is handled correctly
        card.position = { x: newX, y: newY };
        // Note: Direct assignment should work in Vue 3. Use this.$set in Vue 2 if needed.
        // this.$set(this.battlefield[this.draggedBattlefieldCardIndex], 'position', { x: newX, y: newY });

    },

    stopDrag() {
        // Handles mouse up event, ending the battlefield drag
        if (this.isDraggingBattlefieldCard) {
            console.log(`Battlefield Drag End: ${this.battlefield[this.draggedBattlefieldCardIndex]?.name}`);
            this.isDraggingBattlefieldCard = false;
            this.draggedBattlefieldCardIndex = -1;

            // Remove document listeners
            document.removeEventListener('mousemove', this.throttledHandleDrag);
            document.removeEventListener('mouseup', this.stopDrag);
        }
        // Also clear standard drag state if any lingered
         this.draggedCard = null;
         this.draggedFromZone = null;
         this.draggedFromIndex = null;
    },


    // --- Context Menu ---
    openCardMenu(event, card, zone, index) {
      event.preventDefault(); // Prevent default right-click menu
      event.stopPropagation(); // Prevent triggering parent clicks (like zone expansion)

      // Find the actual index in the source array, especially for grouped hand
      let actualIndex = index;
      if (zone === 'hand') {
          actualIndex = this.findCardIndexInHand(card);
      } else {
          // For other zones, verify the index points to the correct card
          const zoneArray = this.getZoneArray(zone);
          if (!zoneArray || index >= zoneArray.length || (zoneArray[index].gameId || zoneArray[index].id) !== (card.gameId || card.id)) {
              // If index mismatch, try to find the card again
              actualIndex = zoneArray.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
              if (actualIndex === -1) {
                  console.error(`Context menu card ${card.name} not found in ${zone}`);
                  return; // Don't open menu if card isn't found
              }
          }
      }


      this.contextCard = card;
      this.contextZone = zone;
      this.contextIndex = actualIndex; // Use the potentially corrected index

      // Position the menu near the click event
      // Add small offset to prevent immediate re-click closing it
      this.contextMenuPosition = { x: event.clientX + 5, y: event.clientY + 5 };
      this.showContextMenu = true;

      console.log(`Context menu opened for ${card.name} in ${zone}[${actualIndex}]`);
    },

    closeContextMenu() {
        this.showContextMenu = false;
        this.contextCard = null;
        this.contextZone = null;
        this.contextIndex = null;
    },

    // --- Context Menu Actions ---
    flipCard() {
      const card = this.getCardFromContext();
      if (card && card.card_faces?.length > 1) { // Check if card is flippable
        card.flipped = !card.flipped;
        console.log(`${card.name} flipped to ${card.flipped ? 'back' : 'front'}`);
      }
      this.closeContextMenu();
    },

    tapCard() {
      const card = this.getCardFromContext();
      // Only allow tapping/untapping on the battlefield
      if (card && this.contextZone === 'battlefield') {
        card.tapped = !card.tapped;
        console.log(`${card.name} ${card.tapped ? 'tapped' : 'untapped'}`);
      }
      this.closeContextMenu();
    },

    addCounter() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') { // Counters usually only on battlefield
        if (!card.counters) card.counters = 0; // Initialize if undefined
        card.counters++;
        console.log(`Added counter to ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    removeCounter() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield' && card.counters > 0) {
        card.counters--;
         console.log(`Removed counter from ${card.name} (${card.counters} total)`);
      }
      this.closeContextMenu();
    },

    setPowerToughness() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        // Pre-fill modal with current P/T or defaults
        this.newPower = card.power ?? 0;
        this.newToughness = card.toughness ?? 0;
        this.showPTModal = true; // Context menu closes automatically after this
      }
       this.closeContextMenu(); // Close context menu even if modal doesn't open
    },

    savePT() {
      const card = this.getCardFromContext(); // Get card reference again
      if (card && this.contextZone === 'battlefield') {
         // Ensure values are numbers
         const power = Number(this.newPower) || 0;
         const toughness = Number(this.newToughness) || 0;
         card.power = power;
         card.toughness = toughness;
         console.log(`Set P/T for ${card.name} to ${power}/${toughness}`);
      }
      this.cancelPT(); // Close modal
    },

    cancelPT() {
      this.showPTModal = false;
      // No need to close context menu here, it was closed when modal opened
    },

    createTokenCopy() {
      const card = this.getCardFromContext();
      if (card && this.contextZone === 'battlefield') {
        // Pre-fill modal based on the copied permanent
        this.tokenName = `${card.name} Token`;
        this.tokenImageUrl = this.getCardImage(card); // Use current image
        this.tokenQuantity = 1; // Default to 1 copy
        this.showTokenModal = true;
      }
       this.closeContextMenu();
    },

    moveToTopOfLibrary() {
      this.moveCardFromContext('library', 'top');
    },

    moveToBottomOfLibrary() {
      this.moveCardFromContext('library', 'bottom');
    },

    moveToZone(targetZone) {
        // Generic move function called by context menu items
        this.moveCardFromContext(targetZone);
    },

    moveCardFromContext(targetZone, libraryPosition = 'top') {
        const card = this.getCardFromContext();
        if (!card) {
            console.error("Cannot move card, context invalid.");
            this.closeContextMenu();
            return;
        }

        const sourceZone = this.contextZone;
        const sourceIndex = this.contextIndex;

        // --- Handle Token Rules ---
         if (card.isToken) {
             if (targetZone === 'hand' || targetZone === 'library' || targetZone === 'graveyard' || targetZone === 'exile') {
                 console.log(`Token ${card.name} removed (moved from ${sourceZone} to ${targetZone})`);
                 this.removeCardFromZone(sourceZone, sourceIndex); // Remove from source
                 this.closeContextMenu();
                 return; // Do not add the token to the target zone
             }
         }
         // --- Handle Commander Rules ---
         if (card.isCommander) {
             // Commanders can move to Command Zone instead of Graveyard/Exile/Hand/Library
             if (targetZone === 'graveyard' || targetZone === 'exile' || targetZone === 'hand' || targetZone === 'library') {
                 // TODO: Implement choice to move to Command Zone instead.
                 // For now, allow the move but log a warning.
                 console.warn(`Commander ${card.name} moved to ${targetZone}. In a real game, you could choose the Command Zone.`);
                 // If moving *to* command zone, handle tax increase
                 if(targetZone === 'command' && sourceZone !== 'command') {
                     this.increaseCommanderTax(); // Increase tax when moving *to* command zone from elsewhere
                 }
             }
         }


        // Remove card from the source zone
        const removedCard = this.removeCardFromZone(sourceZone, sourceIndex);
        if (!removedCard) {
             console.error(`Failed to remove ${card.name} from ${sourceZone}`);
             this.closeContextMenu();
             return;
        }

        // Add card to the target zone
        const targetArray = this.getZoneArray(targetZone);
        if (!targetArray) {
            console.error("Invalid target zone for move:", targetZone);
            // Attempt to put card back in source (might be tricky if index changed)
            this.getZoneArray(sourceZone)?.splice(sourceIndex, 0, removedCard);
            this.closeContextMenu();
            return;
        }

        // Reset state as needed
        removedCard.tapped = false;
        removedCard.position = null; // Reset position unless going to battlefield

        if (targetZone === 'battlefield') {
            // Place somewhere default on battlefield (e.g., top-left or center)
             removedCard.position = { x: 50, y: 50 }; // Example position
             targetArray.push(removedCard);
        } else if (targetZone === 'library') {
            if (libraryPosition === 'bottom') {
                targetArray.push(removedCard); // Add to bottom
            } else {
                targetArray.unshift(removedCard); // Add to top
            }
        } else {
            targetArray.push(removedCard); // Add to end for hand, graveyard, exile, command
        }

        console.log(`Moved ${removedCard.name} from ${sourceZone} to ${targetZone}`);
        this.closeContextMenu();
    },

    increaseCommanderTax() {
      // Usually increases by 2 for each time cast from command zone *after the first*
      // This simple implementation just adds 2 each time the menu item is clicked.
      this.commanderTax += 2;
      console.log(`Commander tax increased to ${this.commanderTax}`);
      this.closeContextMenu(); // Close menu after action
    },

    // --- Token Management ---
    addToken() {
      // Reset token modal fields
      this.tokenName = '';
      this.tokenQuantity = 1;
      this.tokenImageUrl = '';
      this.showTokenModal = true;
    },

    createToken() {
      const quantity = Math.max(1, Number(this.tokenQuantity) || 1); // Ensure at least 1
      const name = this.tokenName.trim() || 'Token';
      const imageUrl = this.tokenImageUrl.trim() || this.defaultTokenImage; // Use default if URL is empty

      for (let i = 0; i < quantity; i++) {
        const newToken = {
          name: name,
          isToken: true,
          gameId: `token-${name.replace(/\s+/g, '-')}-${Date.now()}-${i}`, // Unique ID for token
          image_uris: { normal: imageUrl }, // Structure expected by getCardImage
          tapped: false,
          flipped: false,
          counters: 0,
          position: { x: 50 + i * 10, y: 50 + i * 10 }, // Place tokens slightly offset
          power: undefined, // Tokens often don't have inherent P/T until set
          toughness: undefined,
        };
        this.battlefield.push(newToken);
      }
      console.log(`Created ${quantity} "${name}" token(s)`);
      this.cancelTokenCreation(); // Close modal
    },

    cancelTokenCreation() {
      this.showTokenModal = false;
    },

    // --- Library Search ---
    searchLibrary() {
      this.librarySearchQuery = ''; // Clear previous query
      this.librarySearchResults = [...this.library]; // Show all cards initially
      this.showLibrarySearch = true;
    },

    searchLibraryCards() {
      // Filter library based on search query (case-insensitive)
      const query = this.librarySearchQuery.toLowerCase().trim();
      if (!query) {
        this.librarySearchResults = [...this.library]; // Show all if query is empty
      } else {
        this.librarySearchResults = this.library.filter(card =>
          card.name.toLowerCase().includes(query)
        );
      }
    },

    moveSearchedCardToHand(card) {
        // Find the actual card in the library array
        const index = this.library.findIndex(c => (c.gameId || c.id) === (card.gameId || card.id));
        if (index !== -1) {
            // Remove from library and add to hand
            const [movedCard] = this.library.splice(index, 1);
            this.hand.push(movedCard);
            console.log(`Moved "${movedCard.name}" from library to hand.`);
            // Close the search modal after moving a card
            this.closeLibrarySearch();
        } else {
            console.error(`Card "${card.name}" not found in library during search move.`);
        }
    },

    closeLibrarySearch() {
      this.showLibrarySearch = false;
      this.librarySearchQuery = ''; // Clear query on close
      this.librarySearchResults = []; // Clear results
    },

    // --- Helper Methods ---
    getCardImage(card) {
      // Provides the correct image URL based on card state (flipped, default, token)
      if (!card) return this.defaultCardBack;

      try {
           // Handle flipped cards (Modal Double-Faced Cards - MDFCs, Transform)
           if (card.flipped && card.card_faces && card.card_faces.length > 1 && card.card_faces[1].image_uris) {
             return card.card_faces[1].image_uris.normal || card.card_faces[1].image_uris.large || this.defaultCardBack;
           }
           // Handle regular cards or front face of DFCs
           if (card.image_uris) {
             return card.image_uris.normal || card.image_uris.large || this.defaultCardBack;
           }
           // Handle cards with faces but no top-level image_uris (older DFCs?)
           if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
               return card.card_faces[0].image_uris.normal || card.card_faces[0].image_uris.large || this.defaultCardBack;
           }
           // Fallback for tokens or cards missing image data
           if (card.isToken) {
               return this.defaultTokenImage;
           }
      } catch (e) {
          console.error("Error getting card image for:", card?.name, e);
      }

      // Ultimate fallback
      return this.defaultCardBack;
    },

    getZoneArray(zoneName) {
        // Returns the reactive array corresponding to the zone name
        switch (zoneName) {
            case 'hand': return this.hand;
            case 'library': return this.library;
            case 'graveyard': return this.graveyard;
            case 'exile': return this.exileZone;
            case 'command': return this.commandZone;
            case 'battlefield': return this.battlefield;
            case 'initialDraw': return this.initialHand; // Include initial hand if needed
            default:
                console.error("Unknown zone name:", zoneName);
                return null;
        }
    },

    getCardFromContext() {
        // Safely retrieves the card object based on the current context menu state
        if (!this.contextZone || this.contextIndex === null || this.contextIndex < 0) {
            console.error("Invalid context for getCardFromContext", this.contextZone, this.contextIndex);
            return null;
        }
        const zoneArray = this.getZoneArray(this.contextZone);
        if (!zoneArray || this.contextIndex >= zoneArray.length) {
             console.error("Context index out of bounds for zone", this.contextZone, this.contextIndex);
             return null;
        }
        // Additionally verify the card matches the stored contextCard (optional sanity check)
        if (zoneArray[this.contextIndex]?.gameId !== this.contextCard?.gameId) {
             console.warn("Context card mismatch at index", this.contextIndex, "in zone", this.contextZone);
             // Attempt to find the correct card again? Or just return based on index.
        }

        return zoneArray[this.contextIndex];
    },

     removeCardFromZone(zoneName, index) {
         // Removes and returns the card at the specified index from the zone
         const zoneArray = this.getZoneArray(zoneName);
         if (!zoneArray || index < 0 || index >= zoneArray.length) {
             console.error(`Cannot remove card from ${zoneName} at invalid index ${index}`);
             return null;
         }
         // Use splice to remove the card and get it in return
         const [removedCard] = zoneArray.splice(index, 1);
         return removedCard;
     },

     findCardIndexInHand(cardToFind) {
         // Finds the first index of a card in the actual hand array, matching by gameId or id
         if (!cardToFind) return -1;
         return this.hand.findIndex(card => (card.gameId || card.id) === (cardToFind.gameId || cardToFind.id));
     }
  }
}
</script>

<style scoped>
/* --- General Popup Styling --- */
.playtest-popup {
  position: fixed;
  inset: 0; /* Replaces top, left, right, bottom */
  background-color: rgba(0, 0, 0, 0.85); /* Slightly darker overlay */
  display: flex;
  justify-content: center;
  align-items: center; /* Center the content box */
  z-index: 1000;
  color: #e0e0e0; /* Lighter text color */
  padding: 1rem; /* Add padding around the content */
  box-sizing: border-box;
}

/* FIX: Constrain the main content area's height and allow scrolling */
.playtest-content {
  background-color: #2c3e50; /* Dark blue-grey background */
  border-radius: 12px; /* Slightly larger radius */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); /* Softer shadow */
  display: flex;
  flex-direction: column;
  width: 95%; /* Use percentage width */
  height: 95%; /* Use percentage height */
  max-width: 1800px; /* Max width for large screens */
  max-height: 90vh; /* Max height relative to viewport */
  overflow: hidden; /* Hide overflow on this container */
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #34495e; /* Separator line */
}

.popup-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #ecf0f1; /* Light grey title */
}

.close-btn { /* Changed from .close-button for consistency */
  background: #e74c3c; /* Red */
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1.2rem;
  line-height: 30px; /* Center the '×' */
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background-color: #c0392b; /* Darker red on hover */
}

/* --- Deck Selection / Initial Draw --- */
.deck-selection, .initial-draw {
  padding: 2rem;
  text-align: center;
  flex-grow: 1; /* Allow these sections to take space if needed */
  display: flex;
  flex-direction: column;
  justify-content: center; /* Center content vertically */
}

.deck-option {
  background-color: #34495e;
  padding: 0.8rem 1.2rem;
  margin: 0.5rem auto;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  width: 80%;
  max-width: 350px;
}

.deck-option:hover {
  background-color: #4a657e;
  transform: translateY(-2px);
}

.no-decks-message {
  color: #95a5a6; /* Muted text color */
}

/* --- Playtest Interface Layout --- */
.playtest-interface {
  flex-grow: 1; /* Take remaining vertical space */
  padding: 1rem;
  display: grid; /* Use CSS Grid for layout */
  grid-template-rows: auto 1fr auto auto; /* Rows: Top, Battlefield, Hand, Bottom */
  grid-template-columns: 1fr 1fr; /* Two equal columns */
  gap: 1rem; /* Space between grid items */
  overflow: hidden; /* Prevent interface overflow, rely on inner scrolls */
  height: 100%; /* Ensure it tries to fill parent */
}

.top-row {
  grid-column: 1 / -1; /* Span both columns */
  display: grid;
  grid-template-columns: 1fr 1fr; /* Command and Exile */
  gap: 1rem;
  min-height: 150px; /* Minimum height for top zones */
}

.battlefield {
  grid-column: 1 / -1; /* Span both columns */
  grid-row: 2; /* Place in the second row */
  background-color: rgba(0, 0, 0, 0.3);
  padding: 0.75rem;
  border-radius: 8px;
  position: relative; /* Needed for absolute positioning of cards */
  overflow: auto; /* Allow scrolling if battlefield content overflows */
  min-height: 300px; /* Ensure minimum space */
}

.hand-zone {
  grid-column: 1 / -1; /* Span both columns */
  grid-row: 3; /* Place in the third row */
  background-color: rgba(0, 0, 0, 0.2);
  padding: 0.5rem;
  border-radius: 8px;
  overflow-x: auto; /* Allow horizontal scrolling for hand */
  overflow-y: hidden; /* Hide vertical scrollbar */
  white-space: nowrap; /* Prevent cards from wrapping */
  min-height: 180px; /* Minimum height for hand */
}

.bottom-row {
  grid-column: 1 / -1; /* Span both columns */
  grid-row: 4; /* Place in the fourth row */
  display: grid;
  grid-template-columns: 1fr 1fr; /* Library and Graveyard */
  gap: 1rem;
  min-height: 180px; /* Minimum height for bottom zones */
}

/* --- Zone Styling (Command, Exile, Graveyard, Library) --- */
.command-zone, .exile-zone, .graveyard, .library {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Hide overflow, rely on internal scrolling if needed */
  position: relative; /* For absolute positioning of collapse button */
}

.command-zone h3, .exile-zone h3, .graveyard h3, .library h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  text-align: center;
  color: #bdc3c7; /* Light grey */
  font-size: 1rem;
  font-weight: 600;
}

.zone-preview {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping */
  gap: 5px; /* Smaller gap for preview */
  align-items: flex-start; /* Align items to top */
  min-height: 50px; /* Ensure some space even when empty */
  flex-grow: 1; /* Take available space */
}

/* Style for small preview cards */
.card-image.small {
    width: 60px; /* Smaller width for previews */
    height: auto;
    border-radius: 4px; /* Smaller radius */
}


.more-cards-indicator {
  background-color: rgba(0, 0, 0, 0.6);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  align-self: center; /* Center indicator if it appears */
  margin-top: 5px;
}

.empty-zone-message {
  color: #7f8c8d; /* Muted color */
  font-style: italic;
  font-size: 0.9rem;
  text-align: center;
  margin: auto; /* Center message vertically and horizontally */
}

/* --- Expanded Zone View --- */
/* FIX: Make expanded zones appear as overlays */
.expanded-zone {
  position: fixed; /* Position relative to viewport */
  inset: 0; /* Cover the whole screen */
  background-color: rgba(0, 0, 0, 0.9); /* Darker overlay */
  padding: 2rem;
  z-index: 1002; /* Above the main popup content */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.expanded-cards {
  background-color: #2c3e50; /* Match main background */
  padding: 1.5rem;
  border-radius: 10px;
  max-width: 90%;
  max-height: 80vh; /* Limit height */
  overflow-y: auto; /* Enable scrolling */
  display: flex;
  flex-wrap: wrap;
  gap: 15px; /* Larger gap for expanded view */
  justify-content: center; /* Center cards */
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
}

/* Specific overrides for expanded zones if needed */
.command-expanded, .exile-expanded, .graveyard-expanded {
    /* Styles specific to each expanded zone if needed */
}

.collapse-button {
  position: absolute; /* Position relative to the expanded zone overlay */
  top: 2rem;
  right: 2rem;
  padding: 0.6rem 1.2rem;
  background-color: #3498db; /* Blue */
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
  z-index: 1003; /* Above expanded cards */
}

.collapse-button:hover {
  background-color: #2980b9; /* Darker blue */
}


/* --- Card Styling --- */
.card-wrapper {
  position: relative; /* For badges */
  cursor: pointer;
  display: inline-block; /* Important for hand scrolling */
  margin: 0 5px; /* Spacing in hand */
}

.card-image {
  display: block; /* Prevent extra space below image */
  width: 150px; /* Standard card width */
  height: auto; /* Maintain aspect ratio */
  border-radius: 8px; /* Rounded corners */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  user-select: none; /* Prevent image selection */
  -webkit-user-drag: none; /* Prevent native image dragging sometimes */
}

.card-wrapper:hover .card-image {
  transform: scale(1.05) translateY(-5px); /* Lift effect */
  box-shadow: 0 6px 12px rgba(0,0,0,0.4);
}

.card-wrapper.selected .card-image {
  box-shadow: 0 0 12px 4px #f1c40f; /* Gold outline for selected */
}

.quantity-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background-color: rgba(52, 152, 219, 0.9); /* Blue badge */
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.75rem;
  font-weight: bold;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.counter-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: rgba(231, 76, 60, 0.9); /* Red badge */
  color: white;
  border-radius: 50%;
  min-width: 22px;
  height: 22px;
  padding: 0 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.75rem;
  font-weight: bold;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.pt-indicator {
  position: absolute;
  bottom: 5px;
  left: 5px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.commander-tax {
  position: absolute;
  top: 5px;
  left: 5px;
  background-color: rgba(142, 68, 173, 0.9); /* Purple badge */
  color: white;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* --- Battlefield Specific --- */
.battlefield-cards {
  position: relative; /* Container for absolute positioned cards */
  width: 100%;
  height: 100%; /* Take full height of the .battlefield container */
  min-height: 250px; /* Ensure minimum drawing area */
}

.battlefield-card {
  position: absolute; /* Crucial for drag/drop positioning */
  cursor: grab; /* Indicate draggable */
  transition: transform 0.2s ease; /* Smooth rotation for tapping */
  z-index: 1; /* Base stacking */
}

.battlefield-card:active {
    cursor: grabbing; /* Indicate grabbing */
    z-index: 10; /* Bring to front while dragging */
    box-shadow: 0 8px 20px rgba(0,0,0,0.5); /* Enhance shadow while dragging */
}

/* --- Hand Zone --- */
.hand-cards {
  display: flex; /* Align cards horizontally */
  padding: 0.5rem; /* Padding inside the scrollable area */
  height: 100%; /* Ensure it fills the hand-zone height */
  align-items: center; /* Vertically center cards in the hand zone */
}

/* --- Library & Buttons --- */
.library {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* Center content */
}

.library-image {
  width: 120px; /* Slightly smaller library image */
  height: auto;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 0.5rem;
  transition: transform 0.2s ease;
}

.library-image:hover {
    transform: scale(1.03);
}

.action-button, .draw-button, .token-button, .confirm-button, .cancel-button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.2s ease, transform 0.1s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-button:hover, .draw-button:hover, .token-button:hover, .confirm-button:hover, .cancel-button:hover {
    transform: translateY(-1px);
}

.keep { background-color: #2ecc71; color: white; } /* Green */
.keep:hover { background-color: #27ae60; }
.mulligan { background-color: #f39c12; color: white; } /* Orange */
.mulligan:hover { background-color: #e67e22; }
.draw { background-color: #3498db; color: white; } /* Blue */
.draw:hover { background-color: #2980b9; }
.draw-button { background-color: #3498db; color: white; margin-top: 0.5rem; }
.draw-button:hover { background-color: #2980b9; }
.token-button { background-color: #9b59b6; color: white; margin-top: 0.5rem; } /* Purple */
.token-button:hover { background-color: #8e44ad; }
.confirm-button { background-color: #2ecc71; color: white; }
.confirm-button:hover { background-color: #27ae60; }
.cancel-button { background-color: #e74c3c; color: white; }
.cancel-button:hover { background-color: #c0392b; }

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* --- Context Menu --- */
.context-menu {
  position: fixed; /* Position relative to viewport */
  background-color: #34495e; /* Dark blue-grey */
  border-radius: 6px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
  z-index: 1010; /* Highest z-index */
  padding: 0.5rem 0; /* Vertical padding */
  min-width: 180px;
}

.context-menu-item {
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  color: #ecf0f1; /* Light text */
  font-size: 0.9rem;
  white-space: nowrap; /* Prevent wrapping */
  transition: background-color 0.15s ease;
}

.context-menu-item:hover {
  background-color: #4a657e; /* Slightly lighter blue-grey */
}

.context-menu-divider {
  height: 1px;
  background-color: #2c3e50; /* Darker separator */
  margin: 0.5rem 0;
}

/* --- Modals (Token, P/T, Library Search) --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.75); /* Consistent overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1005; /* Above playtest content, below context menu */
  padding: 1rem; /* Padding for smaller screens */
}

.modal-content { /* Base style for all modal content boxes */
  background-color: #34495e; /* Match context menu */
  padding: 1.5rem 2rem;
  border-radius: 10px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
  color: #ecf0f1;
  max-width: 90%;
  max-height: 90vh; /* Limit height */
  overflow-y: auto; /* Allow scrolling within modal */
  display: flex;
  flex-direction: column;
}

.token-modal, .pt-modal {
  min-width: 350px;
  width: auto; /* Adjust width based on content */
}

.library-search-modal {
  width: 80%;
  max-width: 900px; /* Wider for library search */
  min-height: 400px; /* Ensure decent height */
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  color: white;
}

.token-form, .pt-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.token-form label, .pt-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #bdc3c7;
}

.token-form input[type="text"],
.token-form input[type="number"],
.pt-form input[type="number"],
.library-search-input {
  padding: 0.7rem 0.9rem;
  border-radius: 5px;
  border: 1px solid #7f8c8d;
  background-color: #2c3e50; /* Dark input background */
  color: #ecf0f1; /* Light text */
  font-size: 1rem;
}

.token-form input::placeholder,
.library-search-input::placeholder {
    color: #95a5a6;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #4a657e; /* Separator */
}

/* Library Search Specific */
.library-search-input {
    margin-bottom: 1rem;
}

.search-results {
  flex-grow: 1; /* Allow results to take available space */
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); /* Responsive grid */
  gap: 1rem;
  padding: 0.5rem;
  margin: 1rem 0;
  overflow-y: auto; /* Scroll only results */
  max-height: 55vh; /* Limit height of results area */
  background-color: rgba(0, 0, 0, 0.2); /* Slightly different background */
  border-radius: 6px;
}

.search-result-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.search-result-card:hover {
  transform: scale(1.04);
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.search-card-image {
  width: 100%;
  max-width: 150px; /* Limit image size */
  height: auto;
  border-radius: 6px;
}

.search-result-card span {
    font-size: 0.85rem;
    color: #ecf0f1;
    word-break: break-word; /* Break long names */
}

.library-search-buttons {
    justify-content: space-between; /* Space out buttons */
}

/* --- Loading State --- */
.loading {
  margin: auto;
  font-size: 1.5rem;
  color: #bdc3c7;
}

/* --- Responsive Adjustments (Example) --- */
@media (max-width: 768px) {
  .playtest-interface {
    grid-template-rows: auto auto 1fr auto auto; /* Adjust rows for smaller screens */
    grid-template-columns: 1fr; /* Single column */
    gap: 0.75rem;
    padding: 0.5rem;
  }
  .top-row, .bottom-row {
    grid-column: 1; /* Reset column span */
    grid-template-columns: 1fr; /* Stack zones vertically */
  }
  .battlefield { grid-row: 3; } /* Adjust row placement */
  .hand-zone { grid-row: 4; min-height: 150px; }
  .bottom-row { grid-row: 5; }

  .card-image { width: 120px; } /* Smaller cards */
  .card-image.small { width: 50px; }
  .context-menu { min-width: 150px; }
  .modal-content { padding: 1rem 1.5rem; }
  .search-results { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
}

</style>
