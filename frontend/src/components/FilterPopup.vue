<template>
  <div v-if="isOpen" class="popup-overlay" @click.self="closePopup">
    <div class="filter-popup">
      <div class="popup-header">
        <h3>Filters</h3>
        <button class="close-btn" @click="closePopup">×</button>
      </div>
      
      <div class="popup-content">
        <div class="filter-section">
          <h4>Set</h4>
          <div class="set-selector">
            <input 
              type="text" 
              v-model="setSearchQuery" 
              placeholder="Search sets..." 
              @input="filterSets"
            />
            <div class="set-list">
              <label v-for="set in filteredSets" :key="set.code">
                <input 
                  type="checkbox" 
                  :value="set.code" 
                  v-model="filters.sets"
                />
                {{ set.name }} ({{ set.code }})
              </label>
            </div>
          </div>
        </div>
        
        <!-- Other filter sections remain the same -->
      </div>
      
      <div class="popup-footer">
        <button class="clear-btn" @click="clearFilters">Clear Filters</button>
        <button class="apply-btn" @click="applyFilters">Apply Filters</button>
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
    }
  },
  data() {
    return {
      filters: {
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        subtype: "",
        manaValue: {
          operator: "=",
          value: null
        },
        power: {
          operator: "=",
          value: null
        },
        toughness: {
          operator: "=",
          value: null
        }
      },
      setSearchQuery: '',
      filteredSets: []
    };
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
    applyFilters() {
      this.$emit('apply-filters', this.filters);
      this.closePopup();
    },
    clearFilters() {
      this.filters = {
        sets: [],
        rarities: [],
        types: [],
        supertypes: [],
        subtype: "",
        manaValue: { operator: "=", value: null },
        power: { operator: "=", value: null },
        toughness: { operator: "=", value: null }
      };
      this.$emit('clear-filters');
    },
    closePopup() {
      this.$emit('close-popup');
    }
  }
};
</script>

<style scoped>
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
  border-radius: 8px;
  width: 400px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0 8px;
}

.close-btn:hover {
  color: #333;
}

.popup-content {
  padding: 16px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section h4 {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  color: #444;
}

.set-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.set-selector input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.set-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
}

.set-list label {
  display: block;
  margin-bottom: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.rarity-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.rarity-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.rarity-btn.selected {
  border-color: #333;
  transform: scale(1.1);
}

.multiselect {
  width: 100%;
  height: 100px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
}

.subtype-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.value-filter {
  display: flex;
  gap: 8px;
  align-items: center;
}

.value-filter select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.value-filter input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 60px;
}

.popup-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  border-top: 1px solid #eee;
}

.clear-btn, .apply-btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.clear-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  color: #333;
}

.clear-btn:hover {
  background-color: #eee;
}

.apply-btn {
  background-color: #4CAF50;
  border: 1px solid #45a049;
  color: white;
}

.apply-btn:hover {
  background-color: #45a049;
}
</style>