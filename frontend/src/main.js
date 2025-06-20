import { createApp } from 'vue';
import App from './App.vue';
import './assets/tailwind.css';
import './index.css';
import router from './router/index'; 

createApp(App)
  .use(router)  
  .mount('#app');