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
            <div class="chart-container" style="height: 150px">  <!-- Reduced height -->
                <bar-chart 
                :data="manaCurveChartData"
                :options="manaCurveOptions"
                />
            </div>
            <div class="curve-metrics">
                <div class="metric">
                <div class="metric-value">{{ avgManaValue.toFixed(1) }}</div>
                <div class="metric-label">Avg Mana Value</div>
                </div>
                <div class="metric">
                <div class="metric-value">{{ lowCostCards }}</div>
                <div class="metric-label">Cards ≤ 2 MV</div>
                </div>
            </div>
        </section>
  
        <!-- Card Type Composition -->
        <section class="stats-section">
          <h3 class="section-title">🟢 Card Type Composition</h3>
          <div class="chart-container">
            <pie-chart 
              :data="cardTypeChartData"
              :options="pieChartOptions"
              :height="250"
            />
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
          <div class="chart-container">
            <pie-chart 
              :data="colorIdentityChartData"
              :options="pieChartOptions"
              :height="250"
            />
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
            <div class="chart-container">
              <bar-chart 
                :data="budgetChartData"
                :options="budgetChartOptions"
                :height="100"
              />
            </div>
          </div>
        </section>
  
        <!-- Thematic Content -->
        <section class="stats-section">
          <h3 class="section-title">🟤 Thematic Content</h3>
          <div class="thematic-grid">
            <div class="chart-container">
              <pie-chart 
                :data="creatureTypeChartData"
                :options="pieChartOptions"
                :height="250"
              />
            </div>
            <div class="chart-container">
              <bar-chart 
                :data="keywordChartData"
                :options="keywordChartOptions"
                :height="250"
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  </template>
  
  <script>
  import { 
    Chart as ChartJS, 
    Title, 
    Tooltip, 
    Legend, 
    BarElement, 
    CategoryScale, 
    LinearScale, 
    ArcElement 
  } from 'chart.js'
  import { Bar, Pie } from 'vue-chartjs'
  
  ChartJS.register(
    Title, 
    Tooltip, 
    Legend, 
    BarElement, 
    CategoryScale, 
    LinearScale, 
    ArcElement
  )
  
  export default {
    name: 'StatsPopup',
    components: {
      BarChart: Bar,
      PieChart: Pie
    },
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
        ],
        pieChartOptions: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || ''
                  const value = context.raw || 0
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = Math.round((value / total) * 100)
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        },
        manaCurveOptions: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1,
                    precision: 0
                },
                grid: {
                    display: false
                }
                },
                x: {
                grid: {
                    display: false
                }
                }
            },
            plugins: {
                legend: {
                display: false
                }
            },
            barPercentage: 0.6,
            categoryPercentage: 0.7
            },
        keywordChartOptions: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          indexAxis: 'y',
          scales: {
            x: {
              beginAtZero: true,
              ticks: {
                precision: 0,
                stepSize: 1
              }
            }
          }
        },
        budgetChartOptions: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              display: false
            }
          }
        }
      }
    },
    computed: {
      commanderImage() {
        if (!this.deck?.commander) return ''
        return this.deck.commander.image_uris?.small || 
               this.deck.commander.card_faces?.[0]?.image_uris?.small || ''
      },
      totalCards() {
        if (!this.deck?.cards) return 0
        return this.deck.cards.reduce((total, card) => total + (card.count || 1), 0)
      },
      avgManaValue() {
        if (!this.deck?.cards) return 0
        let totalMV = 0
        let totalCards = 0
        
        this.deck.cards.forEach(card => {
            // Skip lands
            if ((card.type_line || '').includes('Land')) return
            
            const count = card.count || 1
            totalMV += (card.cmc || 0) * count
            totalCards += count
        })
        
        return totalCards > 0 ? totalMV / totalCards : 0
      },                

      lowCostCards() {
  if (!this.deck?.cards) return 0
  
    const curve = this.manaCurveChartData.datasets[0].data
    const labels = this.manaCurveChartData.labels
    
    const zeroIndex = labels.indexOf('0')
    const oneIndex = labels.indexOf('1')
    const twoIndex = labels.indexOf('2')
    
    return (zeroIndex >= 0 ? curve[zeroIndex] : 0) + 
            (oneIndex >= 0 ? curve[oneIndex] : 0) + 
            (twoIndex >= 0 ? curve[twoIndex] : 0)
},
    manaCurveChartData() {
  const curve = { '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7+': 0 }
  
  if (this.deck?.cards) {
    this.deck.cards.forEach(card => {
      const cmc = card.cmc || 0
      const count = card.count || 1
      
      // Skip lands
      if ((card.type_line || '').includes('Land')) {
        return
      }
      
      if (cmc <= 6) {
        curve[cmc.toString()] += count
      } else {
        curve['7+'] += count
      }
    })
  }
  
  return {
    labels: Object.keys(curve),
    datasets: [{
      label: 'Cards',
      backgroundColor: '#4299e1',
      data: Object.values(curve)
    }]
  }
},
      cardTypeChartData() {
        const types = {
          'Creature': 0,
          'Instant': 0,
          'Sorcery': 0,
          'Artifact': 0,
          'Enchantment': 0,
          'Planeswalker': 0,
          'Land': 0,
          'Other': 0
        }
        
        if (this.deck?.cards) {
          this.deck.cards.forEach(card => {
            const count = card.count || 1
            const typeLine = card.type_line || ''
            
            if (typeLine.includes('Creature')) types['Creature'] += count
            else if (typeLine.includes('Instant')) types['Instant'] += count
            else if (typeLine.includes('Sorcery')) types['Sorcery'] += count
            else if (typeLine.includes('Artifact')) types['Artifact'] += count
            else if (typeLine.includes('Enchantment')) types['Enchantment'] += count
            else if (typeLine.includes('Planeswalker')) types['Planeswalker'] += count
            else if (typeLine.includes('Land')) types['Land'] += count
            else types['Other'] += count
          })
        }
        
        const filteredTypes = Object.entries(types)
          .filter(([, count]) => count > 0)
          .map(([name, count]) => ({ name, count }))
        
        return {
          labels: filteredTypes.map(t => t.name),
          datasets: [{
            backgroundColor: filteredTypes.map(t => this.typeColors[t.name] || '#D1D5DB'),
            data: filteredTypes.map(t => t.count)
          }]
        }
      },
      landCount() {
        if (!this.deck?.cards) return 0
        return this.deck.cards.reduce((total, card) => {
          const isLand = (card.type_line || '').includes('Land')
          return total + (isLand ? (card.count || 1) : 0)
        }, 0)
      },
      basicLandCount() {
        if (!this.deck?.cards) return 0
        return this.deck.cards.reduce((total, card) => {
          const isBasicLand = (card.type_line || '').includes('Basic Land')
          return total + (isBasicLand ? (card.count || 1) : 0)
        }, 0)
      },
      nonbasicLandCount() {
        return this.landCount - this.basicLandCount
      },
      landColors() {
        if (!this.deck?.cards || !this.deck?.colors) return []
        
        const colors = {}
        
        this.deck.colors.forEach(color => {
          colors[color] = { identity: color, count: 0 }
        })
        
        this.deck.cards.forEach(card => {
          if ((card.type_line || '').includes('Land')) {
            const count = card.count || 1
            const produces = this.getLandColors(card)
            
            produces.forEach(color => {
              if (colors[color]) {
                colors[color].count += count
              }
            })
          }
        })
        
        return Object.values(colors).sort((a, b) => b.count - a.count)
      },
      colorIdentityChartData() {
        if (!this.deck?.colors) return { labels: [], datasets: [] }
        
        const colorCounts = {}
        
        this.deck.colors.forEach(color => {
          colorCounts[color] = 0;
        });
        
        if (this.deck.cards) {
          this.deck.cards.forEach(card => {
            const count = card.count || 1;
            const colors = card.color_identity || [];
            
            colors.forEach(color => {
              if (colorCounts[color] !== undefined) {
                colorCounts[color] += count;
              }
            });
          });
        }
        
        const filteredColors = Object.entries(colorCounts)
          .filter(([, count]) => count > 0)
          .map(([color, count]) => ({
            color,
            count,
            name: this.getColorName(color)
          }));
        
        return {
          labels: filteredColors.map(c => c.name),
          datasets: [{
            backgroundColor: filteredColors.map(c => this.getColorHex(c.color)),
            data: filteredColors.map(c => c.count)
          }]
        };
      },
      creatureTypeChartData() {
        const types = {}
        
        if (this.deck?.cards) {
          this.deck.cards.forEach(card => {
            if ((card.type_line || '').includes('Creature')) {
              const typeParts = (card.type_line || '').split('—')
              const creatureTypesPart = typeParts.length > 1 ? typeParts[1] : ''
              const creatureTypes = creatureTypesPart.trim().split(/[\s/]+/)
                .filter(type => type && type !== '//' && !type.match(/^[^a-zA-Z]/))
              
              const count = card.count || 1
              
              creatureTypes.forEach(type => {
                types[type] = (types[type] || 0) + count
              })
            }
          })
        }
        
        const topTypes = Object.entries(types)
          .map(([name, count]) => ({ name, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 8)
        
        return {
          labels: topTypes.map(t => t.name),
          datasets: [{
            backgroundColor: topTypes.map((_, i) => this.getColorForIndex(i)),
            data: topTypes.map(t => t.count)
          }]
        }
      },
      keywordChartData() {
        const keywords = {}
        const keywordList = [
          'Flying', 'Trample', 'Haste', 'Vigilance', 'Deathtouch', 'Lifelink',
          'Menace', 'Hexproof', 'Indestructible', 'First strike', 'Double strike',
          'Flash', 'Reach', 'Defender', 'Ward'
        ]
        
        if (this.deck?.cards) {
          this.deck.cards.forEach(card => {
            const oracleText = (card.oracle_text || '').toLowerCase()
            const count = card.count || 1
            const typeLine = (card.type_line || '').toLowerCase()
            
            const isCreature = typeLine.includes('creature')
            const isInstant = typeLine.includes('instant')
            const isSorcery = typeLine.includes('sorcery')
            
            keywordList.forEach(keyword => {
              const keywordLower = keyword.toLowerCase()
              if (oracleText.includes(keywordLower)) {
                if (
                  (keywordLower === 'flying' && !isCreature && !oracleText.includes('enchant creature')) ||
                  (['trample', 'haste', 'vigilance', 'deathtouch', 'lifelink', 'menace', 
                    'first strike', 'double strike', 'reach'].includes(keywordLower) && !isCreature) ||
                  (keywordLower === 'flash' && !isInstant && !isSorcery && !isCreature)
                ) {
                  return
                }
                
                keywords[keyword] = (keywords[keyword] || 0) + count
              }
            })
          })
        }
        
        const topKeywords = Object.entries(keywords)
          .map(([name, count]) => ({ name, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 8)
        
        return {
          labels: topKeywords.map(k => k.name),
          datasets: [{
            backgroundColor: '#9F7AEA',
            data: topKeywords.map(k => k.count)
          }]
        }
      },
      totalDeckPrice() {
        if (!this.deck?.cards) return 0
        return this.deck.cards.reduce((total, card) => {
          const price = parseFloat(card.prices?.usd || '0') || 0
          return total + (price * (card.count || 1))
        }, 0)
      },
      avgCardPrice() {
        if (this.totalCards === 0) return 0
        return this.totalDeckPrice / this.totalCards
      },
      mostExpensiveCard() {
        if (!this.deck?.cards) return { name: 'N/A' }
        
        let maxPrice = 0
        let expensiveCard = null
        
        this.deck.cards.forEach(card => {
          const price = parseFloat(card.prices?.usd || '0') || 0
          if (price > maxPrice) {
            maxPrice = price
            expensiveCard = card
          }
        })
        
        return expensiveCard || { name: 'N/A' }
      },
      mostExpensiveCardPrice() {
        return parseFloat(this.mostExpensiveCard.prices?.usd || '0') || 0
      },
      budgetChartData() {
        if (!this.deck?.cards) return {
          labels: [],
          datasets: []
        }
        
        let under1 = 0
        let oneToFive = 0
        let overFive = 0
        
        this.deck.cards.forEach(card => {
          const price = parseFloat(card.prices?.usd || '0') || 0
          const count = card.count || 1
          
          if (price < 1) under1 += count
          else if (price <= 5) oneToFive += count
          else overFive += count
        })
        
        return {
          labels: ['Under $1', '$1-$5', 'Over $5'],
          datasets: [{
            backgroundColor: ['#48BB78', '#4299E1', '#9F7AEA'],
            data: [under1, oneToFive, overFive]
          }]
        }
      }
    },
    methods: {
      close() {
        this.$emit('close')
      },
      viewCard(card) {
        this.$emit('view-card', card)
      },
      getLandColors(card) {
        return card.color_identity || []
      },
      getColorName(color) {
        const names = {
          'W': 'White',
          'U': 'Blue',
          'B': 'Black',
          'R': 'Red',
          'G': 'Green'
        }
        return names[color] || color
      },
      getColorHex(color) {
        const colors = {
          'W': '#F8F8F7',
          'U': '#0E68AB',
          'B': '#150B00',
          'R': '#D3202A',
          'G': '#00733E'
        }
        return colors[color] || '#CCCCCC'
      },
      getColorForIndex(index) {
        return this.colorPalette[index % this.colorPalette.length]
      }
    }
  }
  </script>
<style scoped>

.chart-container {
  margin-bottom: 10px;
}

.cost-grid .chart-container {
    grid-column: span 2;
}

.thematic-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
  gap: 30px;
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
  padding: 5px;
  border-radius: 6px;
}

.commander-preview:hover {
  transform: translateY(-2px);
  background: #f7fafc;
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

.curve-metrics {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
  gap: 10px;
}


.curve-metric:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric {
  text-align: center;
  padding: 8px 12px;
  background: #f7fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  min-width: 100px;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 2px;
}

.metric-label {
  font-size: 0.8rem;
  color: #4a5568;
}

.metric-subtext {
  font-size: 0.8rem;
  color: #718096;
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

.chart-title {
  text-align: center;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 10px;
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
  transition: height 0.5s ease, background-color 0.2s;
  position: relative;
}

.bar:hover {
  background: #3182ce;
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
  transition: width 0.5s ease, transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 5px;
}

.type-bar-fill:hover {
  transform: scaleY(1.1);
  transform-origin: bottom;
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
  transition: transform 0.2s;
}

.land-count:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
  transition: transform 0.2s;
}

.color-pip:hover {
  transform: scale(1.05);
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
  transition: transform 0.2s;
}

.color-pie {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  transition: transform 0.2s;
}

.pie-hover-info {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  pointer-events: none;
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
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.legend-item:hover {
  background-color: #f7fafc;
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
  transition: transform 0.2s;
}

.cost-metric:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
  transition: color 0.2s;
}

.expensive-card:hover {
  color: #3182ce;
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
  transition: transform 0.2s;
}

.budget-bar:hover {
  transform: scaleY(1.1);
  transform-origin: bottom;
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
  transition: transform 0.2s;
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
  transition: width 0.5s ease, transform 0.2s;
}

.keyword-bar-fill:hover {
  transform: scaleY(1.2);
  transform-origin: bottom;
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

/* Tooltip */
.custom-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  pointer-events: none;
  z-index: 1001;
  max-width: 200px;
  text-align: center;
}

/* Mana Symbols */
.mana {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
  vertical-align: middle;
}

.sw { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="white" stroke="black" stroke-width="2"/></svg>'); }
.su { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="blue" stroke="black" stroke-width="2"/></svg>'); }
.sb { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="black" stroke="black" stroke-width="2"/></svg>'); }
.sr { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="red" stroke="black" stroke-width="2"/></svg>'); }
.sg { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="45" fill="green" stroke="black" stroke-width="2"/></svg>'); }

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
  
  .color-pie-container {
    margin-bottom: 20px;
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
  
  .type-label {
    width: 90px;
    font-size: 0.8rem;
  }
  
  .color-pips {
    gap: 8px;
  }
  
  .color-pip {
    padding: 6px 8px;
    font-size: 0.8rem;
  }
}
</style>