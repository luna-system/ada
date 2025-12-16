========
Examples
========

Code examples for common API operations. For complete endpoint documentation, see :doc:`api_reference`. For detailed streaming information, see :doc:`streaming`.

curl
----

Non-streaming chat:

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!", "include_thinking": false}'

Streaming chat:

.. code-block:: bash

   curl -N -X POST http://localhost:7000/v1/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!", "include_thinking": true}'

Python
------

.. code-block:: python

   import requests

   # Non-streaming
   data = requests.post(
       'http://localhost:7000/v1/chat',
       json={'prompt': 'Hi there'}
   ).json()
   print(data['response'])

   # Streaming
   resp = requests.post(
       'http://localhost:7000/v1/chat/stream',
       json={'prompt': 'Hi there'},
       stream=True,
   )
   for line in resp.iter_lines():
       if line.startswith(b'data: '):
           print(line[6:].decode())

JavaScript (fetch)
------------------

.. code-block:: javascript

   async function chat(prompt) {
     const res = await fetch('/api/chat', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ prompt })
     });
     const data = await res.json();
     console.log(data.response);
   }

JavaScript (stream)
-------------------

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
         }
       }
     }
   }

Related Documentation
---------------------

- :doc:`api_reference` - Complete endpoint documentation
- :doc:`streaming` - Detailed SSE event structure and best practices
- :doc:`memory` - Memory management operations
- :doc:`getting_started` - Setup and configuration
