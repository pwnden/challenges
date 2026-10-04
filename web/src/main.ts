import { createApp, h, nextTick, ref } from 'vue';
import Scenario from '@scenario';
import { navigatePages } from './page';

const revision = ref(0);
createApp({ render: () => h(Scenario, { key: revision.value }) }).mount('#app');
navigatePages(async () => { revision.value++; await nextTick(); });
