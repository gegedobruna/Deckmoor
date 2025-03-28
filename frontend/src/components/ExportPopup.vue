<template>
    <div class="modal-overlay" v-if="isOpen" @click.self="close">
      <div class="modal-content export-modal">
        <h2 class="modal-title">Export Deck</h2>
        
        <div class="deck-info">
          <h3>{{ deck?.name || 'Untitled Deck' }}</h3>
          <div class="deck-meta">
            <div class="deck-colors" v-html="formatColors(deck?.colors || [])"></div>
            <span class="card-count">{{ totalCards }}/100 cards</span>
          </div>
        </div>
        
        <div class="export-format">
          <h4>Export Format:</h4>
          <div class="format-preview">
            <pre>{{ formattedDecklist }}</pre>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="cancel-btn" @click="close">Cancel</button>
          <button class="export-btn" @click="exportDecklist" :disabled="!deck?.cards?.length">
            Export Decklist
          </button>
        </div>
      </div>
    </div>
  </template>
  <script>
  export default {
    name: 'ExportPopup',
    props: {
      isOpen: Boolean,
      deck: {
        type: Object,
        default: () => ({
          name: '',
          colors: [],
          cards: [],
          commander: null
        })
      }
    },
    computed: {
      totalCards() {
        if (!this.deck?.cards) return 0;
        return this.deck.cards.reduce((total, card) => total + (card.count || 1), 0);
      },
      formattedDecklist() {
        if (!this.deck?.cards) return '';
        
        const cardGroups = {};
        this.deck.cards.forEach(card => {
          const key = `${card.name} (${card.set?.toUpperCase() || 'Unknown'})`;
          cardGroups[key] = (cardGroups[key] || 0) + (card.count || 1);
        });
        
        const sortedCards = Object.keys(cardGroups)
          .sort((a, b) => a.localeCompare(b))
          .map(name => `${cardGroups[name]}x ${name}`);
        
        let decklist = [];
        if (this.deck.commander) {
          decklist.push(`Commander: 1x ${this.deck.commander.name} (${this.deck.commander.set?.toUpperCase() || 'Unknown'})`);
          decklist.push('');
        }
        
        decklist = decklist.concat(sortedCards);
        return decklist.join('\n');
      }
    },
    methods: {
      close() {
        this.$emit('close');
      },
      formatColors(colors) {
        if (!colors || colors.length === 0) return '';
        return colors
          .map(color => `<span class="mana small s${color.toLowerCase()}"></span>`)
          .join(' ');
      },
      exportDecklist() {
        const blob = new Blob([this.formattedDecklist], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.deck.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_decklist.txt`;
        document.body.appendChild(a);
        a.click();
        
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 100);
        
        this.close();
      }
    }
  };
  </script>
  
  <style scoped>
  .export-modal {
    max-width: 500px;
    background: white; 
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  
  .modal-title {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.5rem;
    color: #4299e1;
    border-bottom: 2px solid #4299e1;
    padding-bottom: 10px;
  }
  
  .deck-info {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .deck-info h3 {
    margin: 0 0 10px 0;
    font-size: 1.3rem;
    color: #2d3748; 
  }
  
  .deck-meta {
    display: grid;
    align-items: center;
    gap: 12px;
    margin: auto;
  }
  
  .card-count {
    font-size: 0.9rem;
    color: #4a5568;
  }
  
  .export-format {
    margin-bottom: 20px;
  }
  
  .export-format h4 {
    margin: 0 0 10px 0;
    font-size: 1rem;
    color: #4a5568;
  }
  
  .format-preview {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 12px;
    max-height: 300px;
    overflow-y: auto;
  }
  
  .format-preview pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.4;
    color: #2d3748;
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
    color: #4a5568;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .cancel-btn:hover {
    border-color: #a0aec0;
    background-color: #edf2f7;
  }
  
  .export-btn {
    padding: 10px 16px;
    background-color: #38a169;
    border: 1px solid #38a169;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .export-btn:hover:not(:disabled) {
    background-color: #2f855a;
    border-color: #2f855a;
  }
  
  .export-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Scrollbar styling */
  .format-preview::-webkit-scrollbar {
    width: 6px;
  }
  
  .format-preview::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
  
  .format-preview::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
  }
  
  .format-preview::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
  }
  </style>
