<template>
  <div class="popup-overlay" @click.self="close">
    <div class="popup-content">
      <button class="close-button" @click="close" aria-label="Close popup">&times;</button>
      <div class="popup-body">
        <!-- Left Column: Card Image with Flip Component -->
        <div class="card-image-container">
          <div class="card-image">
            <CardFlip :card="card" />
            <div v-if="canBeFlipped" class="flip-hint">Click to flip</div>
          </div>
          
          <!-- Add to Deck Button -->
          <button class="add-to-deck-btn" @click="addToDeckAndClose">
            Add to Deck
          </button>
        </div>
        
        <!-- Right Column: Card Details -->
        <div class="card-info">
          <h2 class="card-title">{{ card.name }}</h2>
          
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Mana Cost:</span>
              <span class="info-value mana-symbols" v-html="formatManaCost(displayManaCost)"></span>
            </div>
            
            <div class="info-row">
              <span class="info-label">Color Identity:</span>
              <span class="info-value">{{ formatColorIdentity(card.colors) }}</span>
            </div>
            
            <div class="info-row" v-if="card.power || card.toughness">
              <span class="info-label">Power/Toughness:</span>
              <span class="info-value">{{ card.power && card.toughness ? `${card.power}/${card.toughness}` : "N/A" }}</span>
            </div>
            
            <div class="info-row">
              <span class="info-label">Type:</span>
              <span class="info-value">{{ card.type_line }}</span>
            </div>
            
            <div class="info-row" v-if="card.set_name">
              <span class="info-label">Set:</span>
              <span class="info-value">{{ card.set_name }}</span>
            </div>
          </div>
          
          <div class="oracle-text">
            <h3>Oracle Text</h3>
            <p v-html="formatManaCost(displayOracleText)"></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CardFlip from './CardFlip.vue';
export default {
  props: {
    card: Object,
  },
  components: {
    CardFlip,
  },
  mounted() {
  },
  computed: {
    canBeFlipped() {
      // Card can be flipped if it has card_faces with a second face that has an image
      return Boolean(this.card?.card_faces?.[1]?.image_uris?.normal);
    },
    displayManaCost() {
    if (this.card.card_faces?.length) {
      const [face1, face2] = this.card.card_faces;
      const cost1 = face1.mana_cost || '';
      const cost2 = face2?.mana_cost || '';
      return cost1 && cost2 ? `${cost1} // ${cost2}` : cost1 || cost2 || 'N/A';
    }
    return this.card.mana_cost || 'N/A';
  },
  displayOracleText() {
    if (this.card.card_faces?.length) {
      return this.card.card_faces
        .map(face => face.oracle_text || '')
        .filter(Boolean)
        .join('<hr style="margin: 10px 0;">'); // simple visual divider
    }
    return this.card.oracle_text || 'N/A';
  }
  },
  methods: {
    close() {
      this.$emit("close");
    },
    addToDeckAndClose() {
      console.log("Emitting add-to-deck for:", this.card.name); // Debug
      this.$emit('add-to-deck', this.card);
      this.close();
    },
    formatManaCost(text) {
      if (!text) return "N/A";
      
      // Convert mana symbols to mana-master classes
      return text.replace(/\{([^}]+)\}/g, (match, symbol) => {
        // Handle special cases
        let cssClass = symbol.toLowerCase();
        
        // Handle tap symbol
        if (cssClass === 't' || cssClass === 'tap') {
          cssClass = 't';
        }
        // Handle untap symbol
        else if (cssClass === 'q' || cssClass === 'untap') {
          cssClass = 'q';
        }
        // Handle hybrid symbols
        else if (cssClass.includes('/')) {
          cssClass = cssClass.replace('/', '');
        }
        // Handle numbers - don't modify them
        else if (/^\d+$/.test(cssClass)) {
          cssClass = symbol; // Use the original symbol without padding
        }
        
        return `<span class="mana medium s${cssClass}"></span>`;
      }); 
    },
    formatColorIdentity(colors) {
      if (!colors || colors.length === 0) return "Colorless";
      
      const colorMap = {
        'W': 'White',
        'U': 'Blue',
        'B': 'Black',
        'R': 'Red',
        'G': 'Green'
      };
      
      return colors.map(color => colorMap[color] || color).join(", ");
    }
  }
};
</script>

<style>
/* Import the mana symbols CSS */
@import '../assets/mana-master/css/mana-cost.css';

.mana-symbols .mana {
  margin-right: 2px;
  vertical-align: middle;
}

.oracle-text p .mana {
  vertical-align: middle;
  position: relative;
  top: -1px;
}
</style>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: white;
  border-radius: 12px;
  width: 1000px;
  max-width: 90%;
  height: 570px;
  max-height: 90%;
  padding: 30px 30px 20px 30px;
  position: relative;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.popup-body {
  display: flex;
  gap: 30px;
  overflow-y: auto;
  height: 100%;
  max-height: calc(100% - 50px);
  margin-bottom: 5px;
}

.card-image-container {
  display: flex;
  flex-direction: column;
  width: 350px;
  min-width: 350px;
  height: 100%; /* Take full height of parent */
}

.card-image-wrapper {
  flex: 1;
  min-height: 0; /* Crucial for flex children */
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.card-image {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative; /* Needed for flip container */
}

.add-to-deck-btn {
  padding: 12px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  width: 100%;
  flex-shrink: 0; /* Prevent button from shrinking */
  margin-top: 10px; /* Push to bottom */
}

.add-to-deck-btn:hover {
  background-color: var(--hover-color);
}

.card-info {
  flex: 1;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 10px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-lable {
  margin-right: 10px;
}

.oracle-text {
  margin-top: 10px;
  background-color: var(--background-color);
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.oracle-text h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: var(--primary-color);
}

.oracle-text p {
  font-size: 15px;
  line-height: 1.5;
  white-space: pre-wrap;
}
.card-flip {
  position: relative !important;
}

.close-button {
  position: absolute;
  background: none;
  color: #666;
  top: 15px;
  right: 15px;
  border: none;
  font-size: 1.8rem;
}

.close-button:hover {
  color: #e53e3e;
}

</style>