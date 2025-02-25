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
        </div>
        
        <!-- Right Column: Card Details -->
        <div class="card-info">
          <h2 class="card-title">{{ card.name }}</h2>
          
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Mana Cost:</span>
              <span class="info-value mana-symbols" v-html="formatManaCost(card.mana_cost)"></span>
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
            <p v-html="formatManaCost(card.oracle_text || 'N/A')"></p>
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
    // Debug: Check what's in the mana_cost field
    console.log("Mana Cost:", this.card.mana_cost);
    console.log("Oracle Text:", this.card.oracle_text);
    console.log("Colors:", this.card.colors);
  },
  computed: {
    canBeFlipped() {
      // Card can be flipped if it has card_faces with a second face that has an image
      return Boolean(this.card?.card_faces?.[1]?.image_uris?.normal);
    }
  },
  methods: {
    close() {
      this.$emit("close");
    },
    formatManaCost(text) {
      if (!text) return "N/A";
      
      // Convert mana symbols to lowercase for proper class naming
      return text.replace(/\{([^}]+)\}/g, (match, symbol) => {
        // Handle special cases
        let cssClass = symbol.toLowerCase();
        
        // Handle tap symbol
        if (cssClass === 't' || cssClass === 'tap') {
          cssClass = 'tap';
        }
        
        // Handle untap symbol
        if (cssClass === 'q' || cssClass === 'untap') {
          cssClass = 'untap';
        }
        
        return `<i class="ms ms-${cssClass}">${cssClass}</i>`;
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
/* Move these outside the scoped style to ensure they apply to dynamically created elements */
.ms {
  display: inline-block;
  width: 1.3em;
  height: 1.3em;
  font-size: 1em;
  border-radius: 50%;
  margin: 0 2px;
  text-align: center;
  line-height: 1.3em;
  color: white;
  font-weight: bold;
  box-shadow: -0.05em 0.12em 0 0 rgba(0, 0, 0, 0.3);
}

/* White mana */
.ms-w {
  background-color: #F8F6D8;
  color: #111;
}

/* Blue mana */
.ms-u {
  background-color: #C1D7E9;
  color: #111;
}

/* Black mana */
.ms-b {
  background-color: #BAB1AB;
  color: black;
}

/* Red mana */
.ms-r {
  background-color: #E49977;
  color: black;
}

/* Green mana */
.ms-g {
  background-color: #A3C095;
  color: #111;
}

/* Generic/colorless mana */
.ms-0, .ms-1, .ms-2, .ms-3, .ms-4, .ms-5, 
.ms-6, .ms-7, .ms-8, .ms-9, .ms-10, .ms-x {
  background-color: #ccc;
  color: #111;
}

/* Special symbols */
.ms-tap, .ms-untap {
  background-color: #ccc;
  color: #111;
}

/* Specific font size adjustments for the mana symbols */
.mana-symbols .ms {
  font-size: 18px;
  margin-right: 2px;
}

/* Oracle text mana symbols alignment */
.oracle-text p .ms {
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
  padding: 30px 30px 20px 30px; /* Reduced bottom padding from 30px to 20px */
  position: relative;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.popup-body {
  display: flex;
  gap: 30px;
  overflow-y: auto;
  height: 100%;
  max-height: calc(100% - 50px); /* Adjusted from 60px to 50px to account for reduced padding */
  margin-bottom: 5px; /* Add a small margin to create a bit more space at the bottom */
}

.card-image-container {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  width: 350px; /* Set a fixed width for the container */
  min-width: 350px; /* Ensure the container doesn't shrink */
}

.card-image {
  width: 100%; /* Take full width of container */
  perspective: 1000px;
  position: relative;
}

/* Target the card face images directly */
:deep(.card-flip-container) {
  width: 100%;
  height: auto;
}

:deep(.card-flip) {
  width: 100%;
  height: auto;
}

:deep(.card-face) {
  width: 100%;
  height: auto;
}

:deep(.card-face img) {
  width: 100%;
  height: auto;
  object-fit: contain;
  display: block;
}

.flip-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: bottom;
  font-size: 14px;
  color: #fff;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 5px 0;
  border-radius: 0 0 5px 5px;
  font-weight: 500;
}

.card-info {
  flex: 1;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0; /* Prevent text overflow issues */
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  color: #222;
  margin: 0 0 10px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  align-items: baseline;
}

.info-label {
  flex: 0 0 150px;
  font-weight: 600;
  color: #444;
}

.info-value {
  flex: 1;
  color: #222;
}

.mana-symbols {
  display: flex;
  align-items: center;
  gap: 3px;
}

.oracle-text {
  margin-top: 10px;
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #3182ce;
}

.oracle-text h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: #3182ce;
}

.oracle-text p {
  font-size: 15px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background: #f1f1f1;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #e0e0e0;
}

/* Media queries for responsiveness */
@media (max-width: 768px) {
  .popup-body {
    flex-direction: column;
    align-items: center;
  }
  
  .card-image-container {
    width: 280px;
    min-width: 280px;
    margin-bottom: 20px;
  }
  
  .info-row {
    flex-direction: column;
    gap: 5px;
  }
  
  .info-label {
    flex: none;
  }
}
</style>