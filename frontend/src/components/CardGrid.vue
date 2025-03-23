<template>
  <div class="card-grid">
    <div v-for="card in cards" :key="card.id" class="card-container">
      <div class="card-item" @click="$emit('select-card', card)">
        <img 
          :src="getCardImageUrl(card)" 
          :alt="card.name" 
          class="card-image"
        >
        <div class="card-title">{{ card.name }}</div>
        
        <!-- Add To Deck Button -->
        <button 
          class="add-to-deck-btn"
          @click.stop="$emit('add-to-deck', card)"
          title="Add to deck"
        >
          <span class="plus-icon">+</span>
        </button>
      </div>
    </div>
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
      // First check if it's a double-faced card
      if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
        // Return the front face image
        return card.card_faces[0].image_uris.normal;
      } 
      // Then check for regular image_uris
      else if (card.image_uris && card.image_uris.normal) {
        return card.image_uris.normal;
      }
      // Then check for image_url from your API
      else if (card.image_url) {
        return card.image_url;
      }
      // Fallback to placeholder
      return 'placeholder-image.jpg';
    }
  }
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