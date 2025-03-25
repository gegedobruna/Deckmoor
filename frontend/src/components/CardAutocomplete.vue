<template>
  <div class="autocomplete-dropdown" v-if="results?.length > 0" @click.stop>
    <ul>
      <li v-for="card in results" :key="card.id" @click="$emit('select-card', card)">
        <div class="card-result">
          <span class="card-name">{{ card.name }}</span>
          <span class="card-mana-cost" v-if="card.mana_cost" v-html="formatManaCost(card.mana_cost)"></span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "CardAutocomplete", 
  props: {
    results: Array,
  },
  methods: {
    closeDropdown() {
      this.$emit("select-card", null);
    },
    formatManaCost(manaCost) {
      if (!manaCost) return '';
      return manaCost.replace(/\{([^}]+)\}/g, (match, symbol) => {
        // Convert symbol to lowercase and handle special cases
        let cssClass = symbol.toLowerCase();
        
        if (cssClass === 't' || cssClass === 'tap') cssClass = 'tap';
        if (cssClass === 'q' || cssClass === 'untap') cssClass = 'untap';
        if (cssClass.includes('/')) cssClass = cssClass.replace('/', '');
        
        return `<span class="mana s${cssClass}"></span>`;
      });
    }
  },
  mounted() {
    document.addEventListener("click", this.closeDropdown);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeDropdown);
  }
};
</script>

<style scoped>
/* Dropdown container styles */
.autocomplete-dropdown {
  position: absolute;
  width: calc(100% - 48px);
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 8px 8px;
  background: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 1000;
  top: 100%;
  left: 0;
}

.autocomplete-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.autocomplete-dropdown li {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-dropdown li:last-child {
  border-bottom: none;
}

.autocomplete-dropdown li:hover {
  background-color: #f5f5f5;
}

.card-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-name {
  font-weight: 500;
}

.card-mana-cost {
  display: flex;
  gap: 2px;
}
</style>

<style>
/* Mana symbol styles - using mana-master classes */
.mana {
  display: inline-block;
  width: 1em;
  height: 1em;
  background-image: url('../assets/mana-master/images/mana.svg');
  background-repeat: no-repeat;
  background-size: auto 700%;
  vertical-align: middle;
}

/* White */
.mana.sw { background-position: 44.4% 33.3%; }
/* Blue */
.mana.su { background-position: 55.5% 33.3%; }
/* Black */
.mana.sb { background-position: 66.6% 33.3%; }
/* Red */
.mana.sr { background-position: 77.7% 33.3%; }
/* Green */
.mana.sg { background-position: 88.8% 33.3%; }
/* Colorless */
.mana.sc { background-position: 77.7% 83.3%; }

/* Generic mana (0-9) */
.mana.s0 { background-position: 0 0; }
.mana.s1 { background-position: 11.1% 0; }
.mana.s2 { background-position: 22.2% 0; }
.mana.s3 { background-position: 33.3% 0; }
.mana.s4 { background-position: 44.4% 0; }
.mana.s5 { background-position: 55.5% 0; }
.mana.s6 { background-position: 66.6% 0; }
.mana.s7 { background-position: 77.7% 0; }
.mana.s8 { background-position: 88.8% 0; }
.mana.s9 { background-position: 99.9% 0; }

/* Hybrid mana */
.mana.swu { background-position: 0 50%; }
.mana.swb { background-position: 11.1% 50%; }
.mana.sub { background-position: 22.2% 50%; }
.mana.sur { background-position: 33.3% 50%; }
.mana.sbr { background-position: 44.4% 50%; }
.mana.sbg { background-position: 55.5% 50%; }
.mana.srw { background-position: 66.6% 50%; }
.mana.srg { background-position: 77.7% 50%; }
.mana.sgw { background-position: 88.8% 50%; }
.mana.sgu { background-position: 99.9% 50%; }

/* Special symbols */
.mana.stap { background-position: 0% 83.3%; }
.mana.suntap { background-position: 11.1% 83.3%; }
</style>