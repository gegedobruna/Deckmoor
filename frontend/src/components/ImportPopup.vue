<template>
    <div v-if="isOpen" class="modal-overlay" @click="$emit('close')">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">Import Deck</h2>
        
        <div class="form-group">
          <label for="deckName">Deck Name:</label>
          <input
            id="deckName"
            v-model="deckName"
            type="text"
            placeholder="Enter deck name"
          />
        </div>
  
        <div class="form-group">
          <label for="deckFile">Deck List (txt file):</label>
          <input
            ref="fileInputRef"
            id="deckFile"
            type="file"
            accept=".txt"
            @change="handleFileUpload"
            :disabled="processing || !deckName.trim()"
          />
        </div>
  
        <div class="import-instructions">
          <h3>Format Instructions:</h3>
          <pre class="format-example">
  Commander
  1x Example Commander Card (set)
  1x Example Card (set)
  13x Example Land (set)</pre>
          <ul>
            <li>First line should be "Commander" (optional)</li>
            <li>Card format: [quantity]x Card Name (Set Code)</li>
            <li>Quantity and set code are optional</li>
            <li>If no commander line, you'll be prompted to choose one</li>
          </ul>
        </div>
  
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="processing" class="processing-message">Processing deck list...</div>
  
     <!-- Commander Selection Modal -->
     <div v-if="showCommanderSelection" class="commander-selection-modal">
          <h3>No commander specified</h3>
          <p>Please select a commander from these valid options:</p>
          <div class="commander-options-container">
            <div class="commander-options">
              <div 
                v-for="(card, index) in potentialCommanders" 
                :key="index"
                class="commander-option"
                :class="{ selected: selectedCommanderIndex === index }"
                @click="selectedCommanderIndex = index"
                @mouseenter="hoveredCommanderIndex = index"
                @mouseleave="hoveredCommanderIndex = null"
              >
                {{ card.name }}
              </div>
            </div>
            <div v-if="hoveredCommanderIndex !== null" class="card-preview">
              <img 
                v-if="potentialCommanders[hoveredCommanderIndex].image_uris?.normal" 
                :src="potentialCommanders[hoveredCommanderIndex].image_uris.normal" 
                alt="Card preview"
              />
              <div v-else class="no-image">
                No image available
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button class="cancel-btn" @click="cancelCommanderSelection">Cancel</button>
            <button 
              class="confirm-btn" 
              @click="confirmCommanderSelection"
              :disabled="selectedCommanderIndex === null"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  name: 'ImportPopup',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  emits: ['close', 'import'],
  setup(props, { emit }) {
    const deckName = ref('');
    const error = ref(null);
    const processing = ref(false);
    const skippedCards = ref([]);
    const fileInputRef = ref(null);
    const showCommanderSelection = ref(false);
    const potentialCommanders = ref([]);
    const selectedCommanderIndex = ref(null);
    const pendingDeckData = ref(null);

    const parseCardLine = (line) => {
      const trimmedLine = line.trim();
      if (!trimmedLine || trimmedLine.toLowerCase() === 'commander') return null;

      // Handle special characters by using a more flexible regex
      const regex = /^(?:(?<quantity>\d+)\s*(?:x\s*)?)?(?<name>.+?)(?:\s*\((?<set>[^)]+)\))?\s*$/;
      const match = trimmedLine.match(regex);

      if (!match || !match.groups.name.trim()) return null;

      return {
        name: match.groups.name.trim(),
        count: match.groups.quantity ? parseInt(match.groups.quantity) : 1,
        setCode: match.groups.set ? match.groups.set.trim() : undefined
      };
    };

    const isPotentialCommander = (cardData) => {
      if (!cardData.type_line) return false;
      const typeLine = cardData.type_line.toLowerCase();
      
      // Check for legendary creatures or planeswalkers
      const isLegendary = typeLine.includes('legendary');
      const isCreature = typeLine.includes('creature') || typeLine.includes('god');
      const isPlaneswalker = typeLine.includes('planeswalker');
      
      // Some planeswalkers can be commanders (like those with "can be your commander")
      const canBeCommander = typeLine.includes('can be your commander');
      
      return (isLegendary && (isCreature || isPlaneswalker)) || canBeCommander;
    };

    const findPotentialCommanders = async (cards) => {
      const commanders = [];
      
      for (const card of cards) {
        try {
          const response = await axios.get(`https://api.scryfall.com/cards/search`, {
            params: {
              q: `!"${card.name.replace(/"/g, '')}"`, // Handle quotes in names
              unique: 'cards'
            }
          });
          
          if (response.data.data.length > 0) {
            const cardData = response.data.data[0];
            if (isPotentialCommander(cardData)) {
              commanders.push({
                ...cardData,
                count: card.count,
                originalName: card.name // Keep original name for matching
              });
            }
          }
        } catch (error) {
          console.error(`Error fetching card: ${card.name}`, error);
        }
      }

      return commanders;
    };

    const verifyImport = (originalText, importedCards) => {
      const originalLines = originalText.split('\n')
        .filter(line => {
          const trimmed = line.trim();
          return trimmed && trimmed.toLowerCase() !== 'commander';
        });
      
      const missingCards = [];
      
      const originalCardNames = [];
      originalLines.forEach(line => {
        const cardData = parseCardLine(line);
        if (cardData) {
          const name = cardData.name.toLowerCase();
          originalCardNames.push(name);
          if (!importedCards.some(c => c.name.toLowerCase() === name)) {
            missingCards.push(line.trim());
          }
        }
      });
      
      return { missingCards };
    };

    const processDeckList = async (text) => {
      const lines = text.split('\n').filter(line => line.trim());
      let commander = null;
      const cards = [];
      const skipped = [];

      // Check for commander header
      const hasCommanderHeader = lines[0]?.trim().toLowerCase() === 'commander';
      if (hasCommanderHeader && lines.length > 1) {
        const commanderLine = lines[1];
        const commanderData = parseCardLine(commanderLine);
        if (commanderData) {
          try {
            const response = await axios.get(`https://api.scryfall.com/cards/search`, {
              params: {
                q: `!"${commanderData.name.replace(/"/g, '')}"`,
                unique: 'cards'
              }
            });
            
            if (response.data.data.length > 0) {
              commander = response.data.data[0];
              commander.count = 1;
              commander.isCommander = true;
            } else {
              throw new Error(`Commander not found: ${commanderData.name}`);
            }
          } catch (error) {
            console.error(`Commander not found: ${commanderData.name}`, error);
          }
        }
        lines.splice(0, 2);
      }

      // Process all cards
      for (const line of lines) {
        const cardData = parseCardLine(line);
        if (cardData) {
          cards.push(cardData);
        }
      }

      // Process cards with duplicate prevention
      const processedCards = [];
      const processedCardNames = new Set();

      // Process non-commander cards first
      for (const card of cards) {
        try {
          // Skip if this is the specified commander
          if (commander && card.name.toLowerCase() === commander.name.toLowerCase()) {
            continue;
          }

          await new Promise(resolve => setTimeout(resolve, 100));
          const response = await axios.get(`https://api.scryfall.com/cards/search`, {
            params: {
              q: `!"${card.name.replace(/"/g, '')}"`,
              unique: 'cards'
            }
          });

          if (response.data.data.length > 0) {
            const cardData = response.data.data[0];
            cardData.count = card.count;
            
            if (!processedCardNames.has(cardData.name)) {
              processedCards.push(cardData);
              processedCardNames.add(cardData.name);
            }
          } else {
            // Try to find the card using a more flexible search
            const fallbackResponse = await axios.get(`https://api.scryfall.com/cards/search`, {
              params: {
                q: card.name,
                unique: 'cards'
              }
            });

            if (fallbackResponse.data.data.length > 0) {
              const cardData = fallbackResponse.data.data[0];
              cardData.count = card.count;
              
              if (!processedCardNames.has(cardData.name)) {
                processedCards.push(cardData);
                processedCardNames.add(cardData.name);
              }
            } else {
              throw new Error(`Card not found: ${card.name}`);
            }
          }
        } catch (error) {
          // Skip error for double-faced cards if they were added anyway
          if (!processedCardNames.has(card.name)) {
            skipped.push(`${card.name}`);
          }
        }
      }

      return {
        commander,
        cards: processedCards,
        skipped
      };
    };

    const handleFileUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      if (!deckName.value.trim()) {
        error.value = 'Please enter a deck name first';
        return;
      }

      processing.value = true;
      error.value = null;
      skippedCards.value = [];

      try {
        const text = await file.text();
        const deckData = await processDeckList(text);
        
        // If no commander was specified, find potential commanders
        if (!deckData.commander) {
          const commanders = await findPotentialCommanders(deckData.cards);
          if (commanders.length > 0) {
            potentialCommanders.value = commanders;
            pendingDeckData.value = deckData;
            showCommanderSelection.value = true;
            processing.value = false;
            return;
          } else {
            throw new Error('No valid commanders found in the deck list');
          }
        }

        completeImport(deckData, text);
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to process deck list';
        console.error('Import error:', err);
      } finally {
        if (!showCommanderSelection.value) {
          processing.value = false;
          if (fileInputRef.value) {
            fileInputRef.value.value = '';
          }
        }
      }
    };

    const completeImport = (deckData, originalText) => {
      const { missingCards } = verifyImport(originalText, deckData.cards);
      
      if (missingCards.length > 0) {
        let message = `Missing cards (${missingCards.length}):\n${missingCards.slice(0, 5).join('\n')}`;
        if (missingCards.length > 5) message += `\n...and ${missingCards.length - 5} more`;
        alert(`Import verification issues:\n${message}`);
      }

      if (deckData.skipped.length > 0) {
        alert(`Note: The following cards were not found and were skipped:\n${deckData.skipped.slice(0, 10).join('\n')}${deckData.skipped.length > 10 ? `\n...and ${deckData.skipped.length - 10} more` : ''}`);
      }

      emit('import', {
        name: deckName.value,
        commander: deckData.commander,
        cards: deckData.cards,
        colors: deckData.commander?.color_identity || [],
        created: new Date().toISOString(),
        missingCards
      });

      emit('close');
    };

    const hoveredCommanderIndex = ref(null);

    const confirmCommanderSelection = () => {
      if (selectedCommanderIndex.value !== null && pendingDeckData.value) {
        const selectedCommander = potentialCommanders.value[selectedCommanderIndex.value];
        selectedCommander.isCommander = true;
        selectedCommander.count = 1;
        
        // Remove the commander from the main cards list if it's there
        const cardsWithoutCommander = pendingDeckData.value.cards.filter(
          card => card.name.toLowerCase() !== selectedCommander.name.toLowerCase()
        );
        
        completeImport({
          commander: selectedCommander,
          cards: [selectedCommander, ...cardsWithoutCommander],
          skipped: pendingDeckData.value.skipped
        }, '');
      }
      
      resetCommanderSelection();
    };

    const cancelCommanderSelection = () => {
      resetCommanderSelection();
      if (fileInputRef.value) {
        fileInputRef.value.value = '';
      }
    };

    const resetCommanderSelection = () => {
      showCommanderSelection.value = false;
      potentialCommanders.value = [];
      selectedCommanderIndex.value = null;
      pendingDeckData.value = null;
      processing.value = false;
    };

    return {
      deckName,
      error,
      processing,
      skippedCards,
      fileInputRef,
      handleFileUpload,
      showCommanderSelection,
      hoveredCommanderIndex,
      potentialCommanders,
      selectedCommanderIndex,
      confirmCommanderSelection,
      cancelCommanderSelection
    };
  }
};
</script>

<style scoped>
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

.import-instructions {
  margin-top: 20px;
  padding: 16px;
  background-color: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.format-example {
  background-color: #edf2f7;
  padding: 12px;
  border-radius: 6px;
  margin: 12px 0;
  font-family: monospace;
  white-space: pre-wrap;
}

.error-message {
  color: #e53e3e;
  padding: 12px;
  background-color: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  margin-top: 12px;
}

.processing-message {
  color: #4299e1;
  padding: 12px;
  background-color: #ebf8ff;
  border: 1px solid #bee3f8;
  border-radius: 6px;
  margin-top: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 16px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #4a5568;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  border-color: #a0aec0;
  background-color: #edf2f7;
}

.confirm-btn {
  padding: 10px 16px;
  background-color: #4299e1;
  border: 1px solid #3182ce;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-btn:hover {
  background-color: #3182ce;
}

.confirm-btn:disabled {
  background-color: #a0aec0;
  border-color: #a0aec0;
  cursor: not-allowed;
}

.commander-selection-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 10px;
  padding: 24px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 1001;
}
.commander-options-container {
  display: flex;
  gap: 20px;
  margin: 16px 0;
}

.commander-options {
  flex: 1;
  max-height: 60vh;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.commander-option {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #e2e8f0;
  transition: background-color 0.2s;
}

.commander-option:hover {
  background-color: #ebf8ff;
}

.commander-option.selected {
  background-color: #bee3f8;
  font-weight: 500;
}

.commander-option:last-child {
  border-bottom: none;
}

.card-preview {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 300px;
}

.card-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.no-image {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  width: 100%;
  background-color: #f7fafc;
  border-radius: 8px;
  color: #718096;
}


</style>