You're right - the issue might be with how the images themselves are being rendered within the card container. Let's look at a solution that forces the images to scale up properly.

Based on the HTML you shared from the inspect element, we need to modify the CSS for the actual card face images. The container might be larger now, but the images inside it could still be constrained.

```html
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
              <span class="info-label">Mana Value:</span>
              <span class="info-value">{{ card.cmc || "N/A" }}</span>
            </div>
            
            <div class="info-row">
              <span class="info-label">Mana Color:</span>
              <span class="info-value">{{ card.colors?.join(", ") || "Colorless" }}</span>
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
            <p>{{ card.oracle_text || "N/A" }}</p>
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
  },
};
</script>

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

