<template>
  <div v-if="isOpen" class="popup-overlay" @click.self="closePopup">
    <div class="filter-popup">
      <div class="popup-header">
        <h3>Card Filters</h3>
        <button class="close-btn" @click="closePopup">×</button>
      </div>
      
      <div class="popup-content">
        <!-- Set Filter -->
        <div class="filter-section">
          <h4>Set</h4>
          <div class="set-selector">
            <input 
              type="text" 
              v-model="setSearchQuery" 
              placeholder="Search sets..." 
              @input="filterSets"
              class="search-input"
            />
            <div class="set-list">
              <label v-for="set in filteredSets" :key="set.code" class="set-item">
                <input 
                  type="checkbox" 
                  :value="set.code" 
                  v-model="filters.sets"
                  class="set-checkbox"
                />
                <span class="set-name">{{ set.name }}</span>
                <span class="set-code">{{ set.code.toUpperCase() }}</span>
              </label>
            </div>
          </div>
        </div>

         <!-- Color Filter -->
         <div class="filter-section">
          <h4>Color</h4>
          <div class="color-buttons">
            <button
              v-for="color in colorOptions"
              :key="color.code"
              :class="['color-btn', { selected: filters.colors.includes(color.code) }]"
              :style="{ backgroundColor: color.background }"
              @click="toggleColor(color.code)"
              :title="color.name"
            >
              <span class="mana small" :class="`s${color.code.toLowerCase()}`"></span>
            </button>
          </div>
        </div>
        
        <!-- Rarity Filter -->
        <div class="filter-section">
          <h4>Rarity</h4>
          <div class="rarity-buttons">
            <button 
              v-for="rarity in rarityOptions" 
              :key="rarity.code"
              :class="['rarity-btn', rarity.code, { selected: filters.rarities.includes(rarity.code) }]"
              @click="toggleRarity(rarity.code)"
              :title="rarity.name"
            >
              <img :src="rarity.image" :alt="rarity.name" class="rarity-icon">
            </button>
          </div>
        </div>
        
        <!-- Type Filter -->
        <div class="filter-section">
          <h4>Card Type</h4>
          <div class="type-buttons">
            <button
              v-for="type in typeOptions"
              :key="type"
              :class="['type-btn', { selected: filters.types.includes(type) }]"
              @click="toggleType(type)"
            >
              {{ type }}
            </button>
          </div>
        </div>
        
        <!-- Supertype Filter -->
        <div class="filter-section">
          <h4>Supertype</h4>
          <div class="supertype-buttons">
            <button
              v-for="supertype in supertypeOptions"
              :key="supertype"
              :class="['supertype-btn', { selected: filters.supertypes.includes(supertype) }]"
              @click="toggleSupertype(supertype)"
            >
              {{ supertype }}
            </button>
          </div>
        </div>

        <!-- Subtype Filter
        <div class="filter-section">
          <h4>Subtype</h4>
          <input 
            type="text" 
            v-model="filters.subtype" 
            placeholder="e.g. Elf, Wizard, Dragon"
            class="subtype-input"
          />
        </div> -->
        
        <!-- Mana Value Filter -->
        <div class="filter-section">
    <h4>Mana Cost</h4>
    <div class="mana-cost-filters">
      <div class="mana-cost-filter">
        <label>Minimum:</label>
        <input 
          type="number" 
          v-model.number="filters.manaCost.min" 
          min="0" 
          max="20"
          class="mana-input"
        />
      </div>
      <div class="mana-cost-filter">
        <label>Maximum:</label>
        <input 
          type="number" 
          v-model.number="filters.manaCost.max" 
          min="0" 
          max="20"
          class="mana-input"
        />
      </div>
    </div>
  </div>
        
        <!-- Power/Toughness Filters -->
        <div class="pt-filters">
          <div class="filter-section">
            <h4>Power</h4>
            <div class="value-filter">
              <select v-model="filters.power.operator" class="operator-select">
                <option value="=">=</option>
                <option value=">">≥</option>
                <option value="<">≤</option>
              </select>
              <input 
                type="number" 
                v-model.number="filters.power.value" 
                min="0"
                class="value-input"
                placeholder="0"
              />
            </div>
          </div>
          
          <div class="filter-section">
            <h4>Toughness</h4>
            <div class="value-filter">
              <select v-model="filters.toughness.operator" class="operator-select">
                <option value="=">=</option>
                <option value=">">≥</option>
                <option value="<">≤</option>
              </select>
              <input 
                type="number" 
                v-model.number="filters.toughness.value" 
                min="0"
                class="value-input"
                placeholder="0"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div class="popup-footer">
        <button class="clear-btn" @click="clearFilters">
          <i class="fas fa-trash-alt"></i> Clear All
        </button>
        <button class="apply-btn" @click="applyFilters">
          <i class="fas fa-check"></i> Apply Filters
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "FilterPopup",
  props: {
    allSets: {
      type: Array,
      default: () => []
    },
    isOpen: {
      type: Boolean,
      default: false
    },
    currentFilters: {
      type: Object,
      default: () => ({
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        colors: [],
        // subtype: "",
        manaCost: { min: 0, max: 20 },
        power: { operator: "=", value: null },
        toughness: { operator: "=", value: null }
      })
    }
  },
  data() {
    return {
      filters: JSON.parse(JSON.stringify(this.currentFilters)),
      setSearchQuery: '',
      filteredSets: this.allSets,
      manaCost: this.currentFilters.manaCost || { min: 0, max: 20 },
      rarityOptions: [
        { code: 'common', name: 'Common', image: require('@/assets/icons/common.png') },
        { code: 'uncommon', name: 'Uncommon', image: require('@/assets/icons/uncommon.png') },
        { code: 'rare', name: 'Rare', image: require('@/assets/icons/rare.png') },
        { code: 'mythic', name: 'Mythic Rare', image: require('@/assets/icons/mythic.png') },
        { code: 'special', name: 'Timeshifted', image: require('@/assets/icons/timeshifted.png') },
        { code: 'bonus', name: 'Masterpiece', image: require('@/assets/icons/masterpiece.png') }
      ],
      typeOptions: [
        'Artifact', 'Creature', 'Enchantment', 
        'Instant', 'Land', 'Planeswalker', 
        'Sorcery', 'Tribal'
      ],
      supertypeOptions: [
        'Basic', 'Legendary', 'Snow', 'World'
      ],
      colorOptions: [
        { code: 'W', name: 'White', background: '#f8f5e4' },
        { code: 'U', name: 'Blue', background: '#c0d8e8' },
        { code: 'B', name: 'Black', background: '#cbc2bf' },
        { code: 'R', name: 'Red', background: '#e8b8a0' },
        { code: 'G', name: 'Green', background: '#c8d6c2' },
        { code: 'C', name: 'Colorless', background: '#e8e8e8' }
      ],
    };
  },
  watch: {
    allSets: { 
      handler(newSets) {
        this.filteredSets = newSets;
      },
      immediate: true
    },
    currentFilters: {
      handler(newFilters) {
        this.filters = JSON.parse(JSON.stringify(newFilters));
      },
      deep: true
    }
  },

  methods: {
    filterSets() {
      if (!this.setSearchQuery.trim()) {
        this.filteredSets = this.allSets;
      } else {
        const query = this.setSearchQuery.toLowerCase();
        this.filteredSets = this.allSets.filter(set => 
          set.name.toLowerCase().includes(query) || 
          set.code.toLowerCase().includes(query)
        );
      }
    },
    toggleRarity(rarity) {
      const index = this.filters.rarities.indexOf(rarity);
      if (index === -1) {
        this.filters.rarities.push(rarity);
      } else {
        this.filters.rarities.splice(index, 1);
      }
    },
    toggleColor(color) {
      const index = this.filters.colors.indexOf(color);
      if (index === -1) {
        this.filters.colors.push(color);
      } else {
        this.filters.colors.splice(index, 1);
      }
    },
    toggleType(type) {
      const index = this.filters.types.indexOf(type);
      if (index === -1) {
        this.filters.types.push(type);
      } else {
        this.filters.types.splice(index, 1);
      }
    },
    toggleSupertype(supertype) {
      const index = this.filters.supertypes.indexOf(supertype);
      if (index === -1) {
        this.filters.supertypes.push(supertype);
      } else {
        this.filters.supertypes.splice(index, 1);
      }
    },
    applyFilters() {
      // Emit the current filters
      this.$emit('apply-filters', JSON.parse(JSON.stringify(this.filters)));
      this.closePopup();
    },
     clearFilters() {
      this.filters = {
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        colors: [],
        // subtype: "",
        manaCost: { min: 0, max: 20 },
        power: { operator: "=", value: null },
        toughness: { operator: "=", value: null }
      };
      this.setSearchQuery = '';
      this.filteredSets = this.allSets;
      this.$emit('clear-filters');
    },
    closePopup() {
      this.$emit('close-popup');
    }
  }
};
</script>

<style>
@import '../assets/mana-master/css/mana-cost.css';

/* Add custom styling for color filter buttons */
.color-btn .mana {
  width: 1.5em;
  height: 1.5em;
  vertical-align: middle;
  filter: drop-shadow(0 1px 1px rgba(0,0,0,0.2));
}

.color-btn.selected .mana {
  filter: drop-shadow(0 1px 1px rgba(0,0,0,0.4));
}

</style>

<style scoped>
/* ==================== */
/* LAYOUT & CONTAINERS  */
/* ==================== */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.filter-popup {
  background-color: white;
  border-radius: 12px;
  width: 500px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.popup-content {
  padding: 20px;
  flex-grow: 1;
  overflow-y: auto;
}

.popup-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  background-color: #f8f9fa;
  border-radius: 0 0 12px 12px;
}

.filter-section {
  margin-bottom: 24px;
}

.pt-filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* ============= */
/* TYPOGRAPHY    */
/* ============= */
.popup-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
}

.filter-section h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #444;
  font-weight: 500;
}

/* ============= */
/* FORM ELEMENTS */
/* ============= */
.search-input,
.subtype-input,
.mana-input,
.value-input,
.operator-select {
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.search-input,
.subtype-input {
  width: 100%;
}

.mana-input {
  width: 60px;
}

.value-input {
  width: 70px;
}

.operator-select {
  background-color: #f8f9fa;
}

.set-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.set-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 8px;
}

.set-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.set-item:hover {
  background-color: #f5f5f5;
}

.set-checkbox {
  margin-right: 12px;
}

.set-name {
  flex-grow: 1;
  font-size: 0.95rem;
}

.set-code {
  background-color: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #495057;
  margin-left: 10px;
}

.value-filter {
  display: flex;
  gap: 10px;
  align-items: center;
}

.mana-cost-filters {
  display: flex;
  gap: 15px;
}

.mana-cost-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ============= */
/* BUTTONS       */
/* ============= */
/* Base Button Styles */
.btn {
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  font-weight: 500;
  border: 2px solid;
}

/* Type/Supertype Buttons with Thin Blue Border */
.type-btn,
.supertype-btn {
  border: 1px solid #a0c4e0; /* Light blue border */
  color: #203c54;
  background-color: white;
  position: relative;
}

.type-btn:hover,
.supertype-btn:hover {
  background-color: #f0f7ff;
  box-shadow: 0 0 0 1px #4682B4, 0 2px 5px rgba(70, 130, 180, 0.2);
}

.type-btn.selected,
.supertype-btn.selected {
  border: 1px solid #4682B4; /* Darker border when selected */
  background-color: #4682B4;
  color: white;
  box-shadow: none; /* Remove outer border when selected */
}

/* Rarity Buttons */
.rarity-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  padding: 0;
  border: 2px solid;
  background-color: white;
  transition: all 0.2s;
}

.rarity-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.rarity-btn.common {
  border-color: #b5b5b5;
  color: #b5b5b5;
}
.rarity-btn.common.selected {
  background-color: #b5b5b5;
  color: white;
}

.rarity-btn.uncommon {
  border-color: #c0c0c0;
  color: #c0c0c0;
}
.rarity-btn.uncommon.selected {
  background-color: #c0c0c0;
  color: white;
}

.rarity-btn.rare {
  border-color: #e6c200;
  color: #e6c200;
}
.rarity-btn.rare.selected {
  background-color: #e6c200;
  color: white;
}

.rarity-btn.mythic {
  border-color: #e67e00;
  color: #e67e00;
}
.rarity-btn.mythic.selected {
  background-color: #e67e00;
  color: white;
}

.rarity-btn.special {
  border-color: #a335ee;
  color: #a335ee;
}
.rarity-btn.special.selected {
  background-color: #a335ee;
  color: white;
}

.rarity-btn.bonus {
  border-color: #ff5555;
  color: #ff5555;
}
.rarity-btn.bonus.selected {
  background-color: #ff5555;
  color: white;
}

/* Color Filter Styles */
.color-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  padding: 0;
}

.color-btn.selected {
  border-color: rgba(0, 0, 0, 0.5);
  border-width: 2px;
  transform: scale(1.1);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.color-btn i {
  font-size: 1.2rem;
  color: rgba(0, 0, 0, 0.7);
}

.color-btn[style*="background-color: #f8f5e4"].selected { /* White */
  border-color: #d1c9a3;
}
.color-btn[style*="background-color: #c0d8e8"].selected { /* Blue */
  border-color: #7fa8c4;
}
.color-btn[style*="background-color: #cbc2bf"].selected { /* Black */
  border-color: #8a817d;
}
.color-btn[style*="background-color: #e8b8a0"].selected { /* Red */
  border-color: #d1947a;
}
.color-btn[style*="background-color: #c8d6c2"].selected { /* Green */
  border-color: #9cb394;
}
.color-btn[style*="background-color: #e8e8e8"].selected { /* Colorless */
  border-color: #c0c0c0;
}

/* Action Buttons */
.clear-btn,
.apply-btn {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
}

.clear-btn {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  color: #dc3545;
}

.clear-btn:hover {
  background-color: #f1f1f1;
}

.apply-btn {
  background-color: #28a745;
  border: 1px solid #28a745;
  color: white;
}

.apply-btn:hover {
  background-color: #218838;
}

/* Button Groups */
.type-buttons,
.supertype-buttons,
.rarity-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

/* Selected States */
.type-btn.selected,
.supertype-btn.selected,
.rarity-btn.selected {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ============= */
/* UTILITIES     */
/* ============= */
.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #666;
  padding: 0 12px;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

/* ============= */
/* RESPONSIVE    */
/* ============= */
@media (max-width: 600px) {
  .filter-popup {
    width: 90vw;
    max-height: 80vh;
  }
  
  .pt-filters {
    grid-template-columns: 1fr;
  }
  
  .type-btn,
  .supertype-btn {
    padding: 6px 12px;
    font-size: 0.85rem;
  }
  
  .rarity-btn {
    width: 36px;
    height: 36px;
  }
}
</style>