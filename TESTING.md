# Manual Testing for Markdown Rendering

1. Start the webserver (inside the repo venv):

```bash
cd /home/luna/Code/ada-v1
FLASK_APP=webserver/app.py /home/luna/Code/ada-v1/.venv/bin/flask run --host 0.0.0.0 --port 5002
```

2. Open the UI in your browser at `http://127.0.0.1:5002/`.

3. Try these messages in the chat composer and submit (note: inline markdown is rendered; block-level markdown/code fences are intentionally not rendered yet):
- Hello **bold** text
- _italic_ and **bold** together
- A link: [OpenAI](https://openai.com)
- Inline code: `const a = 1;`
- Code block:

```js
function test() {
  return 42;
}
```

4. Verify:
- Messages render with bold/italic/links/inline code formatting
- Links open in a new tab and have `rel="noopener noreferrer"` set
- Code fences (```...```) or indented blocks are shown as-escaped/plain text (no <pre> block rendering yet)
 - Code fences (```...```) should now render with a monospace, sanitized <pre><code> block and basic syntax highlighting.
- The 'Thinking' bubble (if enabled) renders inline markdown similarly
 - If markdown does not render, check the small header status next to the brand for `marked:✓ DOMPurify:✓ hljs:✓` — these indicate the client-side libraries loaded successfully.
 - If any are missing (✕), open DevTools console to see errors and clear browser cache (or refresh with Ctrl/Cmd+Shift+R).

5. Optional: Check that the chat input and memory list still work as before.
