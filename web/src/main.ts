import './assets/main.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css' // 引入基础样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 引入图标
import { registerGlobalComponents } from './plugins/registerGlobalComponents.ts'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)

registerGlobalComponents(app)

app.mount('#app')
