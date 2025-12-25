import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { FrappeUI } from 'frappe-ui'

import App from './App.vue'
import './setupFrappeUIResources'
import router from './router'


const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(FrappeUI)

app.mount('#app')

declare global {
	interface Window {
		is_developer_mode?: boolean;
		builder_version: string;
	}
}

if (window.is_developer_mode && typeof window.is_developer_mode === "string") {
	window.is_developer_mode =
		window.is_developer_mode === "1" ||
		window.is_developer_mode === "True" ||
		(window.is_developer_mode as string).startsWith("{{");
}

if (window.builder_version && window.builder_version.startsWith("{{")) {
	window.builder_version = "develop";
}