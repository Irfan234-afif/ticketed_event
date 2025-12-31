
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import TicketView from '../views/TicketView.vue'
import ScannerView from '@/views/ScannerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/:event',
      name: 'event',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/ticket/:id',
      name: 'TicketRequest',
      component: TicketView,
    },
    {
      path: '/scanner',
      name: 'Scanner',
      component: ScannerView,
    },
  ],
})

export default router
