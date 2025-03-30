<template>
    <div v-if="isOpen" class="stats-modal-overlay" @click.self="close">
      <div class="stats-modal-content">
        <button class="close-btn" @click="close">×</button>
        <h2 class="stats-modal-title">Deck Statistics</h2>
        
        <!-- Basic Info Section -->
        <section class="stats-section">
          <h3 class="section-title">🔹 Basic Info</h3>
          <div class="basic-info-grid">
            <div class="info-item">
              <span class="info-label">Deck Name:</span>
              <span class="info-value">{{ deck?.name || 'Untitled Deck' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Format:</span>
              <span class="info-value">Commander</span>
            </div>
            <div class="info-item commander-item" v-if="deck?.commander">
              <span class="info-label">Commander:</span>
              <div class="commander-preview" @click="viewCard(deck.commander)">
                <img :src="commanderImage" :alt="deck.commander.name">
                <span>{{ deck.commander.name }}</span>
              </div>
            </div>
          </div>
        </section>
  
        <!-- Mana Curve Section -->
        <section class="stats-section">
          <h3 class="section-title">🔸 Mana Curve & Speed</h3>
          <div class="curve-grid">
            <div class="curve-metric">
              <div class="metric-value">{{ avgManaValue.toFixed(1) }}</div>
              <div class="metric-label">Avg Mana Value</div>
              <div class="gauge">
                <div class="gauge-fill" :style="{ width: `${Math.min(avgManaValue / 7 * 100, 100)}%` }"></div>
              </div>
            </div>
            <div class="curve-chart">
              <div class="chart-title">Mana Curve</div>
              <div class="chart-bars">
                <div v-for="(count, cmc) in manaCurve" :key="cmc" class="bar-container">
                  <div class="bar" :style="{ height: `${(count / maxCurveValue) * 100}%` }">
                    <span class="bar-count">{{ count }}</span>
                  </div>
                  <div class="bar-label">{{ cmc === '7+' ? '7+' : cmc }}</div>
                </div>
              </div>
            </div>
            <div class="low-cost-metric">
              <div class="metric-value">{{ lowCostCards }}</div>
              <div class="metric-label">Cards ≤ 2 MV</div>
              <div class="metric-subtext">{{ ((lowCostCards / totalCards) * 100).toFixed(1) }}% of deck</div>
            </div>
          </div>
        </section>
  
        <!-- Card Type Composition -->
        <section class="stats-section">
          <h3 class="section-title">🟢 Card Type Composition</h3>
          <div class="type-chart-container">
            <div class="type-chart">
              <div v-for="type in cardTypes" :key="type.name" class="type-bar-container">
                <div class="type-label">{{ type.name }}</div>
                <div class="type-bar">
                  <div class="type-bar-fill" 
                       :style="{ width: `${(type.count / maxTypeCount) * 100}%`, 
                                 backgroundColor: typeColors[type.name] }">
                    <span class="type-count">{{ type.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
  
        <!-- Mana Base Section -->
        <section class="stats-section">
          <h3 class="section-title">🔵 Mana Base</h3>
          <div class="mana-base-grid">
            <div class="land-count">
              <div class="metric-value">{{ landCount }}</div>
              <div class="metric-label">Total Lands</div>
              <div class="land-breakdown">
                <div class="basic-lands">
                  <span class="land-type">Basic:</span>
                  <span class="land-count-value">{{ basicLandCount }}</span>
                </div>
                <div class="nonbasic-lands">
                  <span class="land-type">Nonbasic:</span>
                  <span class="land-count-value">{{ nonbasicLandCount }}</span>
                </div>
              </div>
            </div>
            <div class="color-pips">
              <div class="color-pip" v-for="color in landColors" :key="color.identity">
                <span class="mana" :class="`s${color.identity.toLowerCase()}`"></span>
                <span class="color-count">{{ color.count }}</span>
                <span class="color-name">{{ getColorName(color.identity) }}</span>
              </div>
            </div>
          </div>
        </section>
  
        <!-- Color Identity Section -->
        <section class="stats-section">
          <h3 class="section-title">🟣 Color Identity</h3>
          <div class="color-identity">
            <div class="color-pie-container">
              <div class="color-pie" :style="pieChartStyle"></div>
            </div>
            <div class="color-legend">
              <div v-for="(segment, index) in colorIdentity" :key="index" class="legend-item">
                <span class="legend-color" :style="{ backgroundColor: segment.color }"></span>
                <span class="color-name">{{ segment.label }} ({{ segment.count }})</span>
              </div>
            </div>
          </div>
        </section>
  
        <!-- Cost & Value Section -->
        <section class="stats-section">
          <h3 class="section-title">🟠 Cost & Value</h3>
          <div class="cost-grid">
            <div class="cost-metric">
              <div class="metric-value">${{ totalDeckPrice.toFixed(2) }}</div>
              <div class="metric-label">Total Deck Price</div>
            </div>
            <div class="cost-metric">
              <div class="metric-value">${{ avgCardPrice.toFixed(2) }}</div>
              <div class="metric-label">Avg Card Price</div>
            </div>
            <div class="most-expensive">
              <div class="metric-label">Most Expensive:</div>
              <div class="expensive-card" @click="viewCard(mostExpensiveCard)">
                {{ mostExpensiveCard.name }} <span class="card-price">(${{ mostExpensiveCardPrice.toFixed(2) }})</span>
              </div>
            </div>
            <div class="budget-chart">
              <div class="budget-bar budget-under1" :style="{ width: `${budgetBreakdown.under1}%` }">
                <span class="budget-label">Under $1</span>
              </div>
              <div class="budget-bar budget-1to5" :style="{ width: `${budgetBreakdown.oneToFive}%` }">
                <span class="budget-label">$1-$5</span>
              </div>
              <div class="budget-bar budget-over5" :style="{ width: `${budgetBreakdown.overFive}%` }">
                <span class="budget-label">Over $5</span>
              </div>
            </div>
          </div>
        </section>
  
        <!-- Thematic Content -->
        <section class="stats-section">
          <h3 class="section-title">🟤 Thematic Content</h3>
          <div class="thematic-grid">
            <div class="creature-types">
              <h4 class="subtitle">Creature Types</h4>
              <div class="creature-pie-container">
                <div class="creature-pie" :style="creaturePieStyle"></div>
                <div class="creature-legend">
                  <div v-for="(type, index) in topCreatureTypes" :key="index" class="legend-item">
                    <span class="legend-color" :style="{ backgroundColor: getColorForIndex(index) }"></span>
                    <span class="type-name">{{ type.name }} ({{ type.count }})</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="keywords">
              <h4 class="subtitle">Top Keywords</h4>
              <div class="keyword-chart">
                <div v-for="keyword in topKeywords" :key="keyword.name" class="keyword-item">
                  <div class="keyword-name">{{ keyword.name }}</div>
                  <div class="keyword-bar">
                    <div class="keyword-bar-fill" :style="{ width: `${(keyword.count / maxKeywordCount) * 100}%` }"></div>
                    <span class="keyword-count">{{ keyword.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
</template>
  
<script>
export default {
  name: 'StatsPopup',
  props: {
    isOpen: Boolean,
    deck: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      typeColors: {
        'Creature': '#6EE7B7',
        'Instant': '#93C5FD',
        'Sorcery': '#818CF8',
        'Artifact': '#A5B4FC',
        'Enchantment': '#C4B5FD',
        'Planeswalker': '#F9A8D4',
        'Land': '#FCD34D',
        'Other': '#D1D5DB'
      },
      colorPalette: [
        '#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F',
        '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC'
      ]
    }
  },
  computed: {
    commanderImage() {
      if (!this.deck?.commander) return '';
      return this.deck.commander.image_uris?.small || 
          this.deck.commander.card_faces?.[0]?.image_uris?.small ||
          '';
    },
    totalCards() {
      if (!this.deck?.cards) return 0;
      return this.deck.cards.reduce((total, card) => total + (card.count || 1), 0);
    },
    // Mana Curve Calculations
    manaCurve() {
      const curve = { '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7+': 0 };
      if (!this.deck?.cards) return curve;
      
      this.deck.cards.forEach(card => {
        const cmc = card.cmc || 0;
        const count = card.count || 1;
        
        if (cmc <= 6) {
          curve[cmc.toString()] += count;
        } else {
          curve['7+'] += count;
        }
      });
      
      return curve;
    },
    maxCurveValue() {
      if (!this.manaCurve) return 0;
      const values = Object.values(this.manaCurve);
      return values.length ? Math.max(...values) : 0;
    },
    avgManaValue() {
      if (!this.deck?.cards) return 0;
      
      let totalMV = 0;
      let totalCards = 0;
      
      this.deck.cards.forEach(card => {
        const count = card.count || 1;
        totalMV += (card.cmc || 0) * count;
        totalCards += count;
      });
      
      return totalCards > 0 ? totalMV / totalCards : 0;
    },
    lowCostCards() {
      if (!this.deck?.cards) return 0;
      return this.deck.cards.reduce((total, card) => {
        const cmc = card.cmc || 0;
        const count = card.count || 1;
        return total + (cmc <= 2 ? count : 0);
      }, 0);
    },
    
    // Card Type Calculations
    cardTypes() {
      const types = {
        'Creature': 0,
        'Instant': 0,
        'Sorcery': 0,
        'Artifact': 0,
        'Enchantment': 0,
        'Planeswalker': 0,
        'Land': 0,
        'Other': 0
      };
      
      if (!this.deck?.cards) return Object.entries(types).map(([name, count]) => ({ name, count }));
      
      this.deck.cards.forEach(card => {
        const count = card.count || 1;
        const typeLine = card.type_line || '';
        
        if (typeLine.includes('Creature')) types['Creature'] += count;
        else if (typeLine.includes('Instant')) types['Instant'] += count;
        else if (typeLine.includes('Sorcery')) types['Sorcery'] += count;
        else if (typeLine.includes('Artifact')) types['Artifact'] += count;
        else if (typeLine.includes('Enchantment')) types['Enchantment'] += count;
        else if (typeLine.includes('Planeswalker')) types['Planeswalker'] += count;
        else if (typeLine.includes('Land')) types['Land'] += count;
        else types['Other'] += count;
      });
      
      return Object.entries(types)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
    },
    maxTypeCount() {
      if (!this.cardTypes || !this.cardTypes.length) return 0;
      return Math.max(...this.cardTypes.map(type => type.count));
    },
    
    // Mana Base Calculations
    landCount() {
      if (!this.deck?.cards) return 0;
      return this.deck.cards.reduce((total, card) => {
        const isLand = (card.type_line || '').includes('Land');
        return total + (isLand ? (card.count || 1) : 0);
      }, 0);
    },
    basicLandCount() {
      if (!this.deck?.cards) return 0;
      return this.deck.cards.reduce((total, card) => {
        const isBasicLand = (card.type_line || '').includes('Basic Land');
        return total + (isBasicLand ? (card.count || 1) : 0);
      }, 0);
    },
    nonbasicLandCount() {
      return this.landCount - this.basicLandCount;
    },
    landColors() {
      if (!this.deck?.cards || !this.deck?.colors) return [];
      
      const colors = {};
      
      // Initialize color counts
      this.deck.colors.forEach(color => {
        colors[color] = { identity: color, count: 0 };
      });
      
      // Count lands that produce each color
      this.deck.cards.forEach(card => {
        if ((card.type_line || '').includes('Land')) {
          const count = card.count || 1;
          const produces = this.getLandColors(card);
          
          produces.forEach(color => {
            if (colors[color]) {
              colors[color].count += count;
            }
          });
        }
      });
      
      return Object.values(colors).sort((a, b) => b.count - a.count);
    },
    
    // Color Identity
    colorIdentity() {
      if (!this.deck?.colors || !this.deck.colors.length) return [];
      
      const segments = [];
      const total = this.deck.colors.length;
      
      this.deck.colors.forEach((color, index) => {
        segments.push({
          color: this.getColorHex(color),
          label: this.getColorName(color),
          count: Math.round(100 / total),
          start: (index / total) * 100,
          end: ((index + 1) / total) * 100
        });
      });
      
      return segments;
    },
    pieChartStyle() {
      if (!this.colorIdentity || !this.colorIdentity.length) return {};
      
      const segments = this.colorIdentity.map(segment => 
        `${segment.color} ${segment.start}% ${segment.end}%`
      ).join(', ');
      return {
        background: `conic-gradient(${segments})`
      };
    },
    
    // Cost & Value
    totalDeckPrice() {
      if (!this.deck?.cards) return 0;
      return this.deck.cards.reduce((total, card) => {
        const price = parseFloat(card.prices?.usd || '0') || 0;
        return total + (price * (card.count || 1));
      }, 0);
    },
    avgCardPrice() {
      if (this.totalCards === 0) return 0;
      return this.totalDeckPrice / this.totalCards;
    },
    mostExpensiveCard() {
      if (!this.deck?.cards) return { name: 'N/A' };
      
      let maxPrice = 0;
      let expensiveCard = null;
      
      this.deck.cards.forEach(card => {
        const price = parseFloat(card.prices?.usd || '0') || 0;
        if (price > maxPrice) {
          maxPrice = price;
          expensiveCard = card;
        }
      });
      
      return expensiveCard || { name: 'N/A' };
    },
    mostExpensiveCardPrice() {
      return parseFloat(this.mostExpensiveCard.prices?.usd || '0') || 0;
    },
    budgetBreakdown() {
      if (!this.deck?.cards) return {
        under1: 0,
        oneToFive: 0,
        overFive: 0
      };
      
      let under1 = 0;
      let oneToFive = 0;
      let overFive = 0;
      let total = 0;
      
      this.deck.cards.forEach(card => {
        const price = parseFloat(card.prices?.usd || '0') || 0;
        const count = card.count || 1;
        total += count;
        
        if (price < 1) under1 += count;
        else if (price <= 5) oneToFive += count;
        else overFive += count;
      });
      
      return {
        under1: total > 0 ? (under1 / total) * 100 : 0,
        oneToFive: total > 0 ? (oneToFive / total) * 100 : 0,
        overFive: total > 0 ? (overFive / total) * 100 : 0
      };
    },
    
    // Thematic Content
    topCreatureTypes() {
      if (!this.deck?.cards) return [];
      
      const types = {};
      
      this.deck.cards.forEach(card => {
        if ((card.type_line || '').includes('Creature')) {
          const creatureTypes = card.type_line.split('—')[1]?.trim().split(' ') || [];
          const count = card.count || 1;
          
          creatureTypes.forEach(type => {
            if (type) {
              types[type] = (types[type] || 0) + count;
            }
          });
        }
      });
      
      return Object.entries(types)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8);
    },
    creaturePieStyle() {
      if (!this.topCreatureTypes || !this.topCreatureTypes.length) return {};
      
      const total = this.topCreatureTypes.reduce((sum, type) => sum + type.count, 0);
      if (total === 0) return {};
      
      let currentPercent = 0;
      const segments = this.topCreatureTypes.map((type, index) => {
        const percent = (type.count / total) * 100;
        const start = currentPercent;
        currentPercent += percent;
        return `${this.getColorForIndex(index)} ${start}% ${currentPercent}%`;
      }).join(', ');
      
      return {
        background: `conic-gradient(${segments})`
      };
    },
    topKeywords() {
      if (!this.deck?.cards) return [];
      
      const keywords = {};
      const keywordList = [
        'Flying', 'Trample', 'Haste', 'Vigilance', 'Deathtouch', 'Lifelink',
        'Menace', 'Hexproof', 'Indestructible', 'First strike', 'Double strike',
        'Flash', 'Reach', 'Defender', 'Ward'
      ];
      
      this.deck.cards.forEach(card => {
        const oracleText = (card.oracle_text || '').toLowerCase();
        const count = card.count || 1;
        
        keywordList.forEach(keyword => {
          if (oracleText.includes(keyword.toLowerCase())) {
            keywords[keyword] = (keywords[keyword] || 0) + count;
          }
        });
      });
      
      return Object.entries(keywords)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8);
    },
    maxKeywordCount() {
      if (!this.topKeywords || !this.topKeywords.length) return 1;
      return Math.max(...this.topKeywords.map(k => k.count), 1);
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    viewCard(card) {
      this.$emit('view-card', card);
    },
    getLandColors(card) {
      // Simplified - in reality you'd parse oracle text for color production
      return card.color_identity || [];
    },
    getColorName(color) {
      const names = {
        'W': 'White',
        'U': 'Blue',
        'B': 'Black',
        'R': 'Red',
        'G': 'Green'
      };
      return names[color] || color;
    },
    getColorHex(color) {
      const colors = {
        'W': '#F8F8F7',
        'U': '#0E68AB',
        'B': '#150B00',
        'R': '#D3202A',
        'G': '#00733E'
      };
      return colors[color] || '#CCCCCC';
    },
    getColorForIndex(index) {
      return this.colorPalette[index % this.colorPalette.length];
    }
  }
}
</script>

  <style scoped>
  /* Base Modal Styles */
  .stats-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(3px);
  }
  
  .stats-modal-content {
    background: white;
    border-radius: 12px;
    padding: 30px;
    width: 900px;
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    position: relative;
  }
  
  .close-btn {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #718096;
    transition: color 0.2s;
    padding: 5px 10px;
  }
  
  .close-btn:hover {
    color: #e53e3e;
  }
  
  /* Section Structure */
  .stats-section {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .stats-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  
  .section-title {
    font-size: 1.3rem;
    margin-bottom: 15px;
    color: #2d3748;
  }
  
  .subtitle {
    font-size: 1.1rem;
    margin-bottom: 10px;
    color: #4a5568;
  }
  
  /* Basic Info Section */
  .basic-info-grid {
    display: inline-flex;
    grid-template-columns: repeat(2, 1fr);
    gap: 90px;
  }
  
  .info-item {
    display: flex;
    align-items: center;
  }
  
  .info-label {
    font-weight: 600;
    margin-right: 8px;
    color: #4a5568;
  }
  
  .info-value {
    color: #2d3748;
  }
  
  .commander-item {
    grid-column: span 2;
  }
  
  .commander-preview {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    transition: transform 0.2s;
  }
  
  .commander-preview:hover {
    transform: translateY(-2px);
  }
  
  .commander-preview img {
    width: 50px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  /* Mana Curve Section */
  .curve-grid {
    display: grid;
    grid-template-columns: 150px 1fr 120px;
    gap: 20px;
    align-items: center;
  }
  
  .curve-metric {
    text-align: center;
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  .metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 5px;
  }
  
  .metric-label {
    font-size: 0.9rem;
    color: #4a5568;
    margin-bottom: 10px;
  }
  
  .gauge {
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .gauge-fill {
    height: 100%;
    background: #4299e1;
    transition: width 0.5s ease;
  }
  
  .curve-chart {
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  .chart-bars {
    display: flex;
    height: 150px;
    align-items: flex-end;
    justify-content: space-around;
    padding-top: 20px;
  }
  
  .bar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    max-width: 40px;
  }
  
  .bar {
    width: 25px;
    background: #4299e1;
    border-radius: 4px 4px 0 0;
    transition: height 0.5s ease;
    position: relative;
  }
  
  .bar-count {
    position: absolute;
    top: -25px;
    width: 100%;
    text-align: center;
    font-size: 0.8rem;
    color: #4a5568;
  }
  
  .bar-label {
    margin-top: 5px;
    font-size: 0.8rem;
    color: #718096;
  }
  
  /* Card Type Composition */
  .type-chart-container {
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  .type-chart {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .type-bar-container {
    display: flex;
    align-items: center;
  }
  
  .type-label {
    width: 120px;
    font-weight: 500;
    font-size: 0.9rem;
    color: #4a5568;
  }
  
  .type-bar {
    flex: 1;
    height: 25px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .type-bar-fill {
    height: 100%;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 5px;
  }
  
  .type-count {
    color: white;
    font-size: 0.8rem;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  }
  
  /* Mana Base Section */
  .mana-base-grid {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 20px;
    align-items: center;
  }
  
  .land-count {
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    text-align: center;
  }
  
  .land-breakdown {
    display: flex;
    justify-content: space-around;
    margin-top: 10px;
  }
  
  .land-type {
    font-weight: 500;
    color: #4a5568;
  }
  
  .land-count-value {
    font-weight: 600;
    color: #2d3748;
    margin-left: 5px;
  }
  
  .color-pips {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
    justify-content: center;
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  .color-pip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .color-count {
    font-weight: 600;
    color: #2d3748;
  }
  
  .color-name {
    font-size: 0.9rem;
    color: #4a5568;
  }
  
  /* Color Identity Section */
  .color-identity {
    display: flex;
    gap: 30px;
    align-items: center;
  }
  
  .color-pie-container {
    width: 200px;
    height: 200px;
    position: relative;
  }
  
  .color-pie {
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }
  
  .color-legend {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    display: inline-block;
  }
  
  /* Cost & Value Section */
  .cost-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .cost-metric {
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    text-align: center;
  }
  
  .most-expensive {
    padding: 15px;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    grid-column: span 2;
  }
  
  .expensive-card {
    cursor: pointer;
    color: #4299e1;
    text-decoration: underline;
    margin-top: 5px;
  }
  
  .card-price {
    color: #2d3748;
    font-weight: 600;
  }
  
  .budget-chart {
    height: 30px;
    display: flex;
    border-radius: 4px;
    overflow: hidden;
    grid-column: span 2;
  }
  
  .budget-bar {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.8rem;
    font-weight: 600;
  }
  
  .budget-under1 {
    background: #48BB78;
  }
  
  .budget-1to5 {
    background: #4299E1;
  }
  
  .budget-over5 {
    background: #9F7AEA;
  }
  
  /* Thematic Content Section */
  .thematic-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .creature-pie-container {
    display: flex;
    gap: 20px;
    align-items: center;
  }
  
  .creature-pie {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  
  .creature-legend {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .keyword-chart {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .keyword-item {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .keyword-name {
    width: 120px;
    font-weight: 500;
    color: #4a5568;
  }
  
  .keyword-bar {
    flex: 1;
    height: 20px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
  }
  
  .keyword-bar-fill {
    height: 100%;
    background: #9F7AEA;
    transition: width 0.5s ease;
  }
  
  .keyword-count {
    position: absolute;
    right: 5px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8rem;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  }
  
  /* Responsive Adjustments */
  @media (max-width: 768px) {
    .curve-grid,
    .mana-base-grid,
    .cost-grid,
    .thematic-grid {
      grid-template-columns: 1fr;
    }
    
    .budget-chart,
    .most-expensive {
      grid-column: span 1;
    }
    
    .color-identity {
      flex-direction: column;
    }
    
    .creature-pie-container {
      flex-direction: column;
    }
  }
  
  @media (max-width: 480px) {
    .stats-modal-content {
      padding: 15px;
    }
    
    .commander-preview img {
      width: 40px;
    }
    
    .bar {
      width: 18px;
    }
  }
</style>