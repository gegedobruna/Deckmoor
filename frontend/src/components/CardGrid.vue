<template>
    <div class="card-grid">
      <div 
        v-for="card in cards" 
        :key="card.id" 
        class="card-item" 
        @click="$emit('select-card', card)"
      >
        <img  
        :src="card.image_uris?.small || card.card_faces?.[0]?.image_uris?.small || '/placeholder.jpg'" 
        :alt="card.name || card.card_faces?.[0]?.name || 'Unknown Card'" 
        class="card-image" 
        />
        
        <div class="card-name">{{ card.name || card.card_faces?.[0]?.name }}</div>
      </div>
    </div>
  </template>

 <script>
 export default {
   props: {
     cards: Array,
   },
   mounted() {
     console.log("Cards passed to CardGrid:", this.cards);
   },
 };
 </script>
 
  
  <style scoped>
  .card-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin-top: 20px;
  }
  .card-item {
    cursor: pointer;
    text-align: center;
  }
  .card-image {
    max-width: 100%;
    border-radius: 5px;
    border: 1px solid #ddd;
  }
  .card-name {
    margin-top: 10px;
    font-size: 14px;
    color: #333;
  }
  </style>
  