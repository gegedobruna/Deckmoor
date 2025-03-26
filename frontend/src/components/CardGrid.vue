<template>
  <div class="card-grid">
    <div v-for="card in cards" :key="card.id" class="card-container">
      <div class="card-item">
        <img 
          :src="getCardImageUrl(card)" 
          :alt="card.name" 
          class="card-image"
          @click="handleImageClick(card)"
        >
        <div class="card-title">{{ card.name }}</div>
        <button 
          class="add-to-deck-btn"
          @click.stop="handleAddToDeck(card)"
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(195px, 1fr));
  gap: 20px;
  width: 125%;
  padding: 20px 0;
  box-sizing: border-box;
  margin-right: 40px;
  overflow: visible !important;
}

.card-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-width: 0;
  margin-right: 10px;
  overflow: visible; /* Make sure the button can escape the container */

}

.card-item {
  position: relative;
  height: 100%;
  border-radius: 12px;
  overflow: visible; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: white;
  margin-right: 10px;
  isolation: isolate;
  position: relative;
  z-index: 1;
}
.card-item:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}
.card-title {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  font-weight: bold;
  font-size: 16px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

.add-to-deck-btn {
  position: absolute;
  top: 57px;
  right: -15px;
  width: 30px;
  height: 30px;
  border-radius: 20%;
  background-color: #4299e1;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 20; 
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.add-to-deck-btn:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.4);
  background-color: #3a6d99;
}

.plus-icon {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 1px; 
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  }
}


@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    padding: 15px;
  }
  .card-container {
    height: 320px;
  }
}

@media (max-width: 480px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
  .card-container {
    height: 400px;
  }
}
</style>