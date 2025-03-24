<template>
    <div class="filter-panel">
      <h3>Filters</h3>
      
      <div class="filter-section">
        <h4>Mana Cost</h4>
        <div class="mana-cost-display">
          <span>Min: {{ filters.manaCost.min }}</span>
          <span>Max: {{ filters.manaCost.max }}</span>
        </div>
        <div class="mana-cost-slider">
          <input 
            type="range" 
            v-model.number="filters.manaCost.min" 
            min="0" 
            max="16" 
            @change="emitFilters"
          />
          <input 
            type="range" 
            v-model.number="filters.manaCost.max" 
            min="0" 
            max="16" 
            @change="emitFilters"
          />
        </div>
      </div>
      
      <div class="filter-section">
        <h4>Colors</h4>
        <p class="color-helper-text">
          {{ colorHelperText }}
        </p>
        <div class="color-buttons">
          <button 
            v-for="color in colorOptions" 
            :key="color.code"
            :class="['color-btn', { selected: filters.colors.includes(color.code) }]"
            :style="{ backgroundColor: color.bgColor, color: color.textColor }"
            @click="toggleColor(color.code)"
          >
            {{ color.name }}
          </button>
        </div>
      </div>
      
      <div class="filter-section">
        <h4>Card Type</h4>
        <select multiple v-model="filters.types" @change="emitFilters" class="multiselect">
          <option v-for="type in typeOptions" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
      
      <div class="filter-section">
        <h4>Rarity</h4>
        <div class="checkbox-group">
          <label v-for="rarity in rarityOptions" :key="rarity">
            <input 
              type="checkbox" 
              :value="rarity" 
              v-model="filters.rarities"
              @change="emitFilters"
            />
            {{ rarity }}
          </label>
        </div>
      </div>
      
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
                @change="emitFilters"
              />
              {{ set.name }} ({{ set.code }})
            </label>
          </div>
        </div>
      </div>
      
      <div class="filter-section">
        <h4>Power/Toughness</h4>
        <div class="pt-filters">
          <div class="pt-filter">
            <label>Power</label>
            <select v-model="filters.power.operator" @change="emitFilters">
              <option value="equal">Equal to</option>
              <option value="greater">Greater than</option>
              <option value="less">Less than</option>
            </select>
            <input 
              type="number" 
              v-model.number="filters.power.value" 
              min="0" 
              @change="emitFilters"
            />
          </div>
          
          <div class="pt-filter">
            <label>Toughness</label>
            <select v-model="filters.toughness.operator" @change="emitFilters">
              <option value="equal">Equal to</option>
              <option value="greater">Greater than</option>
              <option value="less">Less than</option>
            </select>
            <input 
              type="number" 
              v-model.number="filters.toughness.value" 
              min="0" 
              @change="emitFilters"
            />
          </div>
        </div>
      </div>
      
      <button class="clear-filters" @click="clearFilters">Clear All Filters</button>
    </div>
  </template>
  
  <script>
  export default {
    name: "FilterPanel",
    props: {
      allSets: {
        type: Array,
        default: () => []
      }
    },
    data() {
      return {
        filters: {
          manaCost: {
            min: 0,
            max: 16
          },
          colors: [],
          types: [],
          rarities: [],
          sets: [],
          power: {
            operator: "equal",
            value: 0
          },
          toughness: {
            operator: "equal",
            value: 0
          }
        },
        colorOptions: [
          { code: 'W', name: 'White', bgColor: '#F8F6D8', textColor: '#111' },
          { code: 'U', name: 'Blue', bgColor: '#C1D7E9', textColor: '#111' },
          { code: 'B', name: 'Black', bgColor: '#BAB1AB', textColor: '#111' },
          { code: 'R', name: 'Red', bgColor: '#E49977', textColor: '#111' },
          { code: 'G', name: 'Green', bgColor: '#A3C095', textColor: '#111' },
          { code: 'C', name: 'Colorless', bgColor: '#ccc', textColor: '#111' }
        ],
        typeOptions: [
          'Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 
          'Land', 'Planeswalker', 'Legendary', 'Tribal', 'Basic'
        ],
        rarityOptions: ['common', 'uncommon', 'rare', 'mythic'],
        setSearchQuery: '',
        filteredSets: []
      };
    },
    computed: {
      colorHelperText() {
        if (this.filters.colors.length === 0) {
          return "Select colors to filter cards";
        } else if (this.filters.colors.length === 1) {
          return "Showing cards of exactly this color";
        } else {
          return "Showing cards containing any of these colors";
        }
      }
    },
    created() {
      this.filteredSets = this.allSets;
    },
    watch: {
      allSets: {
        handler(newSets) {
          this.filteredSets = newSets;
        },
        immediate: true
      }
    },
    methods: {
      toggleColor(color) {
        const index = this.filters.colors.indexOf(color);
        if (index === -1) {
          this.filters.colors.push(color);
        } else {
          this.filters.colors.splice(index, 1);
        }
        this.emitFilters();
      },
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
      emitFilters() {
        this.$emit('filters-changed', { ...this.filters });
      },
      clearFilters() {
        this.filters = {
          manaCost: {
            min: 0,
            max: 16
          },
          colors: [],
          types: [],
          rarities: [],
          sets: [],
          power: {
            operator: "equal",
            value: 0
          },
          toughness: {
            operator: "equal",
            value: 0
          }
        };
        this.emitFilters();
      }
    }
  };
  </script>
  
  
<style scoped>
.filter-panel {
  background-color: white;
  border-radius: 8px;
  padding: var(--spacing-unit);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: var(--spacing-unit);
}

.filter-panel h3 {
  margin-top: 0;
  margin-bottom: var(--spacing-unit);
  font-size: 1.25rem;
  color: var(--text-color);
}

.filter-section {
  margin-bottom: var(--spacing-unit);
}

.filter-section h4 {
  margin-top: 0;
  margin-bottom: calc(var(--spacing-unit) / 2);
  font-size: 1rem;
  color: var(--text-color);
}

.mana-cost-display {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-unit);
  background-color: var(--background-color);
  padding: calc(var(--spacing-unit) / 2);
  border-radius: 4px;
  font-weight: bold;
}

.mana-cost-slider {
  padding: 0 calc(var(--spacing-unit) / 2);
}

input[type="range"] {
  width: 100%;
  margin: calc(var(--spacing-unit) / 2) 0;
}

.color-helper-text {
  margin: 0 0 calc(var(--spacing-unit) / 2) 0;
  font-size: 0.875rem;
  color: var(--secondary-color);
  font-style: italic;
}

.color-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: calc(var(--spacing-unit) / 2);
}

.color-btn {
  border: 2px solid transparent;
  border-radius: 4px;
  padding: calc(var(--spacing-unit) / 2) var(--spacing-unit);
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}

.color-btn.selected {
  border-color: var(--text-color);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}

.multiselect {
  width: 100%;
  height: 120px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: calc(var(--spacing-unit) / 2);
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: calc(var(--spacing-unit) / 2);
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: calc(var(--spacing-unit) / 2);
  cursor: pointer;
}

.set-selector {
  display: flex;
  flex-direction: column;
  gap: calc(var(--spacing-unit) / 2);
}

.set-selector input {
  width: 100%;
  padding: calc(var(--spacing-unit) / 2);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.set-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: var(--spacing-unit);
}

.set-list label {
  display: block;
  margin-bottom: calc(var(--spacing-unit) / 2);
  cursor: pointer;
}

.pt-filters {
  display: flex;
  flex-direction: column;
  gap: calc(var(--spacing-unit) / 2);
}

.pt-filter {
  display: flex;
  align-items: center;
  gap: calc(var(--spacing-unit) / 2);
}

.pt-filter label {
  width: 80px;
}

.pt-filter select {
  flex: 1;
  padding: calc(var(--spacing-unit) / 2);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.pt-filter input {
  width: 60px;
  padding: calc(var(--spacing-unit) / 2);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.clear-filters {
  width: 100%;
  padding: var(--spacing-unit);
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-filters:hover {
  background-color: var(--border-color);
}
</style>