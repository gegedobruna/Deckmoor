<template>
  <div class="card-grid">
    <div v-for="card in cards" :key="card.id" class="card-container">
      <div class="card-item">
        <!-- Clicking image only triggers showing details -->
        <img 
          :src="getCardImageUrl(card)" 
          :alt="card.name" 
          class="card-image"
          @click="handleImageClick(card)"
        >
        <div class="card-title">{{ card.name }}</div>

        <!-- Separate button to add card to the deck -->
        <button 
          class="add-to-deck-btn"
          @click.stop="handleAddToDeck(card)"
          title="Add to deck"
        >
          <span class="plus-icon">+</span>
        </button>
      </div>
    </div>

    <!-- OUTSIDE the loop -->
    <CardResult
      v-for="card in cards"
      :key="card.id"
      :card="card"
      @add-to-deck="addCardToDeck"
    />

    <CardDetailsPopup
      v-if="selectedCard"
      :card="selectedCard"
      @add-to-deck="addCardToDeck"
    />
  </div>
</template>


<script>
export default {
  props: {
    cards: {
      type: Array,
      required: true
    }
  },
  methods: {
    getCardImageUrl(card) {
      // Double-faced card
      if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
        return card.card_faces[0].image_uris.normal;
      }
      // Regular image_uris
      else if (card.image_uris && card.image_uris.normal) {
        return card.image_uris.normal;
      }
      // Fallback
      return 'placeholder-image.jpg';
    },
    handleAddToDeck(card) {
      console.log("Add button clicked for:", card.name);
      this.$emit('add-to-deck', card);
    },
    handleImageClick(card) {
      this.$emit('select-card', card);
    },
    
  },
  
};
</script>

<style scoped>
.card-grid {
  padding-right: 350px; 
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.card-container {
  position: relative;
}

.card-item {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background-color: white;
}

.card-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.card-image {
  width: 100%;
  display: block;
  object-fit: cover;
  aspect-ratio: 63/88; /* MTG card ratio */
}

.card-title {
  padding: 8px;
  font-weight: bold;
  font-size: 14px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Add to Deck Button Styles */
.add-to-deck-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #4682B4;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s, transform 0.2s;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.add-to-deck-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.plus-icon {
  font-size: 18px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>