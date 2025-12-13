const { JSDOM } = require('jsdom');
const marked = require('marked');
const hljs = require('highlight.js');
const createDOMPurify = require('dompurify');

const { window } = new JSDOM(`<!doctype html><html><body><div id="messages"></div></body></html>`);
const DOMPurify = createDOMPurify(window);

function renderMarkdown(md) {
  const fencedRegex = /(^|\n)```(\w+)?\n([\s\S]*?)\n```/m;
  const hasFenced = fencedRegex.test(md);
  const otherBlockRegex = /(^|\n)( {4,}|^#{1,6}\s+|^>\s+|^(\s*[-*+]\s+)|^(\s*\d+\.\s+))/m;
  const hasOtherBlocks = otherBlockRegex.test(md);

  let rawHtml;
  if (hasFenced && !hasOtherBlocks) {
    // configure marked highlight
    marked.setOptions({
      highlight: function(code, lang) {
        try {
          if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
          }
          return hljs.highlightAuto(code).value;
        } catch (e) {
          return code;
        }
      }
    });
    rawHtml = marked.parse(md);
  } else if (!hasOtherBlocks) {
    rawHtml = marked.parseInline(md);
  } else {
    rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
  }

  const sanitizeConfig = {
    ALLOWED_TAGS: ['a','b','i','strong','em','code','pre','p','br','ul','ol','li','span'],
    ALLOWED_ATTR: ['href','title','class']
  };
  return DOMPurify.sanitize(rawHtml, sanitizeConfig);
}

const tests = [
  {name: 'inline', md: 'This is **bold** and `inline code` and a [link](https://example.com) '},
  {name: 'fence', md: 'Here is code:\n```js\nconsole.log("hello");\n```'},
  {name: 'heading/list', md: '# Heading\n- item1\n- item2'},
  {name: 'mixed', md: 'Intro\n```py\nprint(\"hi\")\n```\nMore text'},
];

for (const t of tests) {
  console.log('---', t.name, '---');
  console.log(renderMarkdown(t.md));
  console.log('\n');
}
