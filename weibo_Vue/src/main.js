import Vue from 'vue';
import App from '@/App.vue';
import router from './router.js';
import $ from 'jquery'
import axios from 'axios'
Vue.prototype.$axios = axios
import 'bootstrap'
import mavonEditor from 'mavon-editor';
import 'mavon-editor/dist/css/index.css';
import Message from '@/components/commons/message';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.use(Message);
Vue.use(mavonEditor);
Vue.use(ElementUI);
Vue.config.productionTip = false;
new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
router.beforeEach((to, from, next) => {
  next();
});

