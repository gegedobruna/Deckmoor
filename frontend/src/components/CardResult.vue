<template>
  <div class="card-details">
    <!-- Card Faces (for double-sided cards) -->
    <template v-if="card.card_faces">
      <CardFlip :card="card" />
      <div v-for="(face, index) in card.card_faces" :key="index" class="card-face">
        <div class="card-info">
          <div><strong>Name:</strong> {{ face.name }}</div>
          <div><strong>Mana Value:</strong> {{ card.cmc || "N/A" }}</div>
          <div><strong>Mana Color:</strong> {{ face.colors?.join(", ") || "Colorless" }}</div>
          <div><strong>Type:</strong> {{ face.type_line }}</div>
          <div><strong>Oracle Text:</strong> {{ face.oracle_text || "N/A" }}</div>
        </div>
      </div>
    </template>

    <!-- Single-Sided Card -->
    <template v-else>
      <CardFlip :card="card" />
      <div class="card-info">
        <div><strong>Name:</strong> {{ card.name }}</div>
        <div><strong>Mana Value:</strong> {{ card.cmc || "N/A" }}</div>
        <div><strong>Mana Color:</strong> {{ card.colors?.join(", ") || "Colorless" }}</div>
        <div><strong>Power/Toughness:</strong> 
          {{ card.power && card.toughness ? `${card.power}/${card.toughness}` : "N/A" }}
        </div>
        <div><strong>Type:</strong> {{ card.type_line }}</div>
        <div><strong>Subtype:</strong> {{ card.type_line.split("—")[1] || "None" }}</div>
        <div><strong>Sets:</strong> {{ card.set_name || "N/A" }}</div>
        <div><strong>Oracle Text:</strong> {{ card.oracle_text || "N/A" }}</div>
      </div>
    </template>
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
};
</script>

<style scoped>
.card-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
}
.card-face {
  margin-bottom: 20px;
  width: 100%;
}
.card-info {
  font-size: 16px;
}
.card-image img {
  max-width: 300px;
  border-radius: 5px;
}
</style>