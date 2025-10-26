// saterys/web/src/main.ts

// Import plugin manifest BEFORE bootstrapping the app
import './plugins.manifest';

import App from './App.svelte';

// If you have a global stylesheet, keep the import; otherwise remove this line.
// import './app.css';

const app = new App({
  target: document.getElementById('app')!
});

export default app;
