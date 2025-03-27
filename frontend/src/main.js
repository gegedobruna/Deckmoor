import { createApp } from 'vue'
import App from './App.vue'
import 'mana-font/css/mana.min.css';
import './assets/global.css';
import Notifications from '@kyvg/vue3-notification'

const app = createApp(App)
app.use(Notifications)
createApp(App).mount('#app')
