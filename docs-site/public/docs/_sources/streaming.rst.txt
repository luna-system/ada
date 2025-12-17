=========
Streaming
=========

The Brain API supports real-time token delivery via **Server-Sent Events (SSE)** on ``POST /v1/chat/stream``. Use this for low-latency, progressive rendering of LLM responses.

For complete endpoint documentation, see :doc:`api_reference`. For client examples, see :doc:`examples`.

Endpoint
--------

.. code-block:: bash

   POST /v1/chat/stream

Request Body (JSON)
-------------------

Same as ``/v1/chat``:

- ``prompt`` (str, required)
- ``conversation_id`` (str, optional)
- ``include_thinking`` (bool, optional)
- ``entity`` (str, optional)
- ``save_memory`` (bool, optional)
- ``memory_text`` (str, optional)

Response Format (SSE)
---------------------

``Content-Type: text/event-stream``

Events are newline-delimited and prefixed with ``data: ``:

.. code-block:: text

   data: {"type": "thinking", "content": "Reasoning token"}
   data: {"type": "token", "content": "Hello "}
   data: {"type": "token", "content": "world"}
   data: {"type": "done", "conversation_id": "...", "used_context": {...}}

Event Types
-----------

- ``thinking``: Reasoning tokens (only if ``include_thinking`` is true)
- ``token``: Assistant response tokens
- ``done``: Final metadata (conversation_id, used_context, timestamps, request_id)
- ``error``: Error details if the stream fails

curl Example
------------

.. code-block:: bash

   curl -N -X POST http://localhost:7000/v1/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!", "include_thinking": true}'

Python (requests)
-----------------

.. code-block:: python

   import requests, json

   resp = requests.post(
       'http://localhost:7000/v1/chat/stream',
       json={'prompt': 'What is AI?', 'include_thinking': True},
       stream=True,
   )

   for line in resp.iter_lines():
       if line.startswith(b'data: '):
           event = json.loads(line[6:])
           if event['type'] == 'token':
               print(event['content'], end='', flush=True)
           elif event['type'] == 'thinking':
               print('\n🤔', event['content'], end='', flush=True)
           elif event['type'] == 'done':
               print('\n✓ done')

JavaScript (fetch + ReadableStream)
-----------------------------------

.. code-block:: javascript

   async function streamChat(prompt) {
     const res = await fetch('/api/chat/stream', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ prompt, include_thinking: true })
     });

     const reader = res.body.getReader();
     const decoder = new TextDecoder();
     let buffer = '';

     while (true) {
       const { done, value } = await reader.read();
       if (done) break;
       buffer += decoder.decode(value, { stream: true });
       const lines = buffer.split('\n');
       buffer = lines.pop();
       for (const line of lines) {
         if (line.startsWith('data: ')) {
           const event = JSON.parse(line.slice(6));
           if (event.type === 'token') console.log(event.content);
           if (event.type === 'done') console.log('done');
         }
       }
     }
   }

Best Practices
--------------

- Use ``-N`` with curl to disable buffering.
- In UIs, batch DOM updates (e.g., via ``requestAnimationFrame``) for smoother rendering.
- Handle both HTTP errors and stream ``error`` events.
- Use ``AbortController`` (fetch) to cancel long-running streams.
- Memory is persisted after ``done``; partial streams do not save. See :doc:`memory` for memory management.

Related Documentation
---------------------

- :doc:`api_reference` - Complete endpoint documentation
- :doc:`examples` - Code examples in Python, JavaScript, curl
- :doc:`memory` - Memory persistence and retrieval
- :doc:`configuration` - Streaming and timeout configuration
