<template>
    <div class="popup-overlay" @click.self="close">
      <div class="popup-content">
        <button class="close-button" @click="close">&times;</button>
        <div class="popup-body">
          <!-- Card Image -->
          <div class="card-image">
            <img 
              :src="card.image_uris?.normal || card.card_faces?.[0]?.image_uris?.normal || '/placeholder.jpg'" 
              :alt="card.name" 
            />
          </div>
          <!-- Card Details -->
          <div class="card-info">
            <h2>{{ card.name }}</h2>
            <p><strong>Mana Value:</strong> {{ card.cmc || "N/A" }}</p>
            <p><strong>Mana Color:</strong> {{ card.colors?.join(", ") || "Colorless" }}</p>
            <p><strong>Power/Toughness:</strong> 
              {{ card.power && card.toughness ? `${card.power}/${card.toughness}` : "N/A" }}
            </p>
            <p><strong>Type:</strong> {{ card.type_line }}</p>
            <p><strong>Oracle Text:</strong> {{ card.oracle_text || "N/A" }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      card: Object,
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
    border-radius: 10px;
    width: 600px;
    max-width: 90%;
    padding: 20px;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }
  .popup-body {
    display: flex;
    gap: 20px;
  }
  .card-image img {
    max-width: 200px;
    border-radius: 5px;
    border: 1px solid #ddd;
  }
  .card-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .card-info h2 {
    margin-bottom: 10px;
  }
  </style>
  