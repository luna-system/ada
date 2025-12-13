const fs = require('fs');
const vm = require('vm');
const { JSDOM } = require('jsdom');
const marked = require('marked');
const hljs = require('highlight.js');
const createDOMPurify = require('dompurify');

const html = `<!doctype html><html><head></head><body>
<div id="messages"></div>
<div id="statusBox"></div>
<div id="clientLibs"></div>
<form id="composer"><textarea id="prompt"></textarea><button id="send" type="submit">Send</button></form>
</body></html>`;

const dom = new JSDOM(html, { runScripts: 'dangerously', resources: 'usable', url: 'http://localhost' });
const { window } = dom;
// Polyfill scrollTo used in the app so tests do not fail in jsdom
if (!window.HTMLElement.prototype.scrollTo) {
  window.HTMLElement.prototype.scrollTo = function(){};
}

// Setup minimal globals expected by app.js
window.localStorage = new (class LocalStorageMock {
  constructor(){ this.store = {}; }
  getItem(key){ return this.store[key] || null; }
  setItem(key, value){ this.store[key] = String(value); }
})();
window.crypto = { randomUUID: () => 'fake-uuid' };
window.fetch = async function() { return { ok: true, json: async () => ({ok: true}) }; };

// Expose libraries on window similar to CDN-loaded globals
window.marked = marked;
window.hljs = hljs;
const DOMPurify = createDOMPurify(window);
window.DOMPurify = DOMPurify;

// Read the app.js file and evaluate it in the jsdom context with improved error logging
const appJs = fs.readFileSync('webserver/static/app.js', 'utf8');
try {
  vm.runInContext(appJs, dom.getInternalVMContext());
} catch (e) {
  console.error('Error running app.js:', e && e.stack ? e.stack : e);
  process.exit(1);
}

// Now we should have the functions defined. Test rendering.
const { document } = window;

function testRender(md) {
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  document.body.appendChild(bubble);
  // call the function defined in the app script
  const renderFn = window.renderMarkdownToElement;
  if (typeof renderFn !== 'function') throw new Error('renderMarkdownToElement not found');
  // For this test, simulate that this is a bot message so we exercise allowBlocks: true
  renderFn(bubble, md, { allowBlocks: true });
  return bubble.innerHTML;
}

(async () => {
  const tests = [
    {name: 'inline', md: 'This is **bold** and `inline code` and a [link](https://example.com) '},
    {name: 'fence', md: 'Here is code:\n```js\nconsole.log("hello");\n```'},
    {name: 'heading/list', md: '# Heading\n- item1\n- item2'},
  ];

  for (const t of tests) {
    console.log('---', t.name, '---');
    console.log(testRender(t.md));
    console.log('\n');
  }
})();
