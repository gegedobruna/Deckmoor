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
            <li>If no commander line, one will be chosen from the list</li>
          </ul>
        </div>
  
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="processing" class="processing-message">Processing deck list...</div>
  
        <div class="modal-actions">
          <button class="cancel-btn" @click="$emit('close')">Cancel</button>
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

    const parseCardLine = (line) => {
      const trimmedLine = line.trim();
      if (!trimmedLine || trimmedLine.toLowerCase() === 'commander') return null;

      const regex = /^(?:(?<quantity>\d+)\s*(?:x\s*)?)?(?<name>[^(]+?)(?:\s*\((?<set>[^)]+)\))?$/;
      const match = trimmedLine.match(regex);

      if (!match) return null;

      return {
        name: match.groups.name.trim(),
        count: match.groups.quantity ? parseInt(match.groups.quantity) : 1,
        setCode: match.groups.set ? match.groups.set.trim() : undefined
      };
    };

    const findCommander = async (cards) => {
      const legendaryCreatures = [];
      
      for (const card of cards) {
        try {
          await new Promise(resolve => setTimeout(resolve, 100));
          const response = await axios.get(`https://api.scryfall.com/cards/search`, {
            params: {
              q: `!"${card.name}"`,
              unique: 'cards'
            }
          });
          
          if (response.data.data.length > 0) {
            const cardData = response.data.data[0];
            const typeLine = cardData.type_line?.toLowerCase() || '';
            if (typeLine.includes('legendary') && 
                (typeLine.includes('creature') || typeLine.includes('god'))) {
              legendaryCreatures.push(cardData);
            }
          }
        } catch (error) {
          console.error(`Error fetching card: ${card.name}`, error);
        }
      }

      if (legendaryCreatures.length === 0) {
        throw new Error('No valid commander found in the deck list');
      }

      return legendaryCreatures[0];
    };

    const verifyImport = (originalText, importedCards) => {
      const originalLines = originalText.split('\n')
        .filter(line => {
          const trimmed = line.trim();
          return trimmed && trimmed.toLowerCase() !== 'commander';
        });
      
      const importedNames = importedCards.map(card => card.name.toLowerCase());
      
      const missingCards = [];
      const extraCards = [];
      
      const originalCardNames = [];
      originalLines.forEach(line => {
        const cardData = parseCardLine(line);
        if (cardData) {
          const name = cardData.name.toLowerCase();
          originalCardNames.push(name);
          if (!importedNames.includes(name)) {
            missingCards.push(line.trim());
          }
        }
      });
      
      importedNames.forEach((importedName, index) => {
        if (index === 0 && importedCards[index].isCommander) return;
        if (!originalCardNames.includes(importedName)) {
          extraCards.push(importedCards[index].name);
        }
      });
      
      return { missingCards, extraCards };
    };

    const processDeckList = async (text) => {
      const lines = text.split('\n').filter(line => line.trim());
      let commander = null;
      const cards = [];
      const skipped = [];

      // Check for commander header
      const hasCommanderHeader = lines[0].trim().toLowerCase() === 'commander';
      if (hasCommanderHeader && lines.length > 1) {
        const commanderLine = lines[1];
        const commanderData = parseCardLine(commanderLine);
        if (commanderData) {
          try {
            const response = await axios.get(`https://api.scryfall.com/cards/search`, {
              params: {
                q: `!"${commanderData.name}"`,
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

      // If no commander was specified, find one
      if (!commander) {
        try {
          commander = await findCommander(cards);
          commander.count = 1;
          commander.isCommander = true;
        } catch (error) {
          console.error('No valid commander found', error);
        }
      }

      // Process cards with duplicate prevention
      const processedCards = [];
      const processedCardNames = new Set();

      // Add commander first if exists
      if (commander && !processedCardNames.has(commander.name)) {
        processedCards.push(commander);
        processedCardNames.add(commander.name);
      }

      // Process other cards
      for (const card of cards) {
        try {
          // Skip if this is the commander
          if (commander && card.name.toLowerCase() === commander.name.toLowerCase()) {
            continue;
          }

          await new Promise(resolve => setTimeout(resolve, 100));
          const response = await axios.get(`https://api.scryfall.com/cards/search`, {
            params: {
              q: `!"${card.name}"`,
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
            throw new Error(`Card not found: ${card.name}`);
          }
        } catch (error) {
          skipped.push(`${card.name} (Error: ${error.message})`);
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
        
        const { missingCards, extraCards } = verifyImport(text, deckData.cards);
        
        if (missingCards.length > 0 || extraCards.length > 0) {
          let message = '';
          if (missingCards.length > 0) {
            message += `Missing cards (${missingCards.length}):\n${missingCards.slice(0, 5).join('\n')}`;
            if (missingCards.length > 5) message += `\n...and ${missingCards.length - 5} more`;
            message += '\n\n';
          }
          if (extraCards.length > 0) {
            message += `Unexpected extra cards (${extraCards.length}):\n${extraCards.slice(0, 5).join('\n')}`;
            if (extraCards.length > 5) message += `\n...and ${extraCards.length - 5} more`;
          }
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
          missingCards,
          extraCards
        });

        emit('close');
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to process deck list';
        console.error('Import error:', err);
      } finally {
        processing.value = false;
        if (fileInputRef.value) {
          fileInputRef.value.value = '';
        }
      }
    };

    return {
      deckName,
      error,
      processing,
      skippedCards,
      fileInputRef,
      handleFileUpload
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
  </style>