=======================
Web Search Specialist
=======================

Overview
========

The web search specialist provides Ada with real-time access to current information via your self-hosted SearxNG instance at https://hunt.airsi.de.

Features
========

- **Bidirectional only**: LLM must explicitly request search (not auto-activated)
- **SearxNG integration**: Privacy-respecting metasearch aggregating multiple sources
- **Context injection**: Search results formatted and injected into prompt
- **Rate limit aware**: Handles 429 errors gracefully

Configuration
=============

Set in ``.env``:

.. code-block:: bash

   SEARXNG_URL=https://hunt.airsi.de

The specialist auto-discovers when ``SEARXNG_URL`` is set.

Usage Pattern
=============

LLM Detection
-------------

When Ada realizes she needs current information:

.. code-block:: text

   User: What's the weather in Portland today?
   Ada: I don't have access to real-time weather data in my training. 
        Let me search for current information.
        SPECIALIST_REQUEST[web_search:{"query":"Portland weather today"}]

Specialist Execution (Pause/Resume)
------------------------------------

1. Generation **pauses** when request detected
2. Web search executes via SearxNG
3. Results formatted and injected into context
4. Generation **resumes** with enriched prompt

Result Format
-------------

.. code-block:: text

   🔍 Web Search Results for 'Portland weather today':

   1. Portland Weather - National Weather Service
      URL: https://weather.gov/portland
      Partly cloudy with high of 55°F. Rain expected this evening...

   2. Weather.com - Portland, OR
      URL: https://weather.com/weather/today/l/Portland+OR
      Current conditions: 52°F, mostly cloudy. Chance of rain 60%...

Specialist Metadata
===================

Auto-generated FAQ entries:

- **Capability**: "Search the web for current information, news, facts, and real-time data"
- **Priority**: HIGH (injected early in prompt)
- **Icon**: 🔍
- **Tags**: web, search, current-events, real-time

Request Schema
==============

.. code-block:: python

   {
       "query": str,           # Search terms (required)
       "num_results": int      # Number of results (default: 5)
   }

Example Interactions
====================

News Query
----------

.. code-block:: text

   User: What happened in AI today?
   Ada: SPECIALIST_REQUEST[web_search:{"query":"AI news today"}]

   [Results injected]

   Based on the search results, here's what's happening in AI today:
   - OpenAI released...
   - Google announced...

Fact Checking
-------------

.. code-block:: text

   User: Is Python 3.13 released yet?
   Ada: Let me check the latest information.
        SPECIALIST_REQUEST[web_search:{"query":"Python 3.13 release"}]

   [Results show release date]

   Yes! Python 3.13 was released on October 7, 2024...

Current Events
--------------

.. code-block:: text

   User: Who won the game last night?
   Ada: SPECIALIST_REQUEST[web_search:{"query":"game results yesterday"}]

   [Results with sports scores]

   Based on the search results...

Rate Limiting
=============

Your SearxNG instance has rate limiting enabled (429 Too Many Requests). This is handled gracefully:

.. code-block:: python

   except httpx.HTTPError as e:
       logger.error(f"[WEB_SEARCH] HTTP error: {e}")
       return self.error_result(
           f"Search service error: {str(e)}",
           request_context
       )

The error is returned to the LLM, which can inform the user:

.. code-block:: text

   Ada: I'm unable to search right now due to rate limiting. 
        Based on my knowledge up to [training date]...

Testing
=======

Manual Test via Bidirectional Handler
--------------------------------------

The web search specialist will be invoked when the LLM emits the request syntax during generation.

Direct API Test (Future)
-------------------------

Once we add a manual specialist invocation endpoint:

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/specialists/web_search \
     -H "Content-Type: application/json" \
     -d '{"query": "test search"}'

Architecture Integration
========================

Discovery
---------

.. code-block:: text

   [BRAIN] Discovered 3 specialists: 🎧 media, 📄 ocr, 🔍 web_search
   [BRAIN] Synced 10 specialist FAQ entries to RAG

Dynamic Documentation
---------------------

When user asks search-related questions, RAG retrieves:

.. code-block:: text

   Q: How do I invoke the web_search specialist?
   A: Use the syntax SPECIALIST_REQUEST[web_search:{"query":"search terms"}]...

Pause/Resume Flow
-----------------

::

   User query → Prompt building → LLM generation → 
     Detection: SPECIALIST_REQUEST[web_search:...] →
     PAUSE → Execute search → Build enriched prompt →
     RESUME → Continue generation with results

Privacy & Security
==================

- **Self-hosted**: All searches go through your SearxNG instance
- **No tracking**: SearxNG doesn't track user queries
- **Aggregated results**: Multiple search engines provide diverse sources
- **Rate limiting**: Prevents abuse

Future Enhancements
===================

Caching
-------

Cache recent searches to reduce API calls:

.. code-block:: python

   search_cache = {}  # TTL: 5 minutes
   if query in search_cache and not expired:
       return cached_result

Result Filtering
----------------

Filter by domain, date, content type:

.. code-block:: python

   SPECIALIST_REQUEST[web_search:{
       "query": "Python news",
       "num_results": 10,
       "time_range": "day",
       "engines": ["google", "bing"]
   }]

Image Search
------------

Add image search capability:

.. code-block:: python

   SPECIALIST_REQUEST[image_search:{"query": "Mars rover"}]

Troubleshooting
===============

Specialist Not Discovered
--------------------------

Check logs:

.. code-block:: bash

   docker logs ada-v1-brain-1 | grep "Discovered"
   # Should show: Discovered 3 specialists: 🎧 media, 📄 ocr, 🔍 web_search

Verify environment:

.. code-block:: bash

   docker exec ada-v1-brain-1 env | grep SEARXNG
   # Should show: SEARXNG_URL=https://hunt.airsi.de

Search Fails
------------

Check SearxNG accessibility:

.. code-block:: bash

   curl "https://hunt.airsi.de/search?q=test&format=json"

Check logs for errors:

.. code-block:: bash

   docker logs ada-v1-brain-1 | grep WEB_SEARCH

Rate Limited
------------

Your instance has rate limiting. Options:

1. Wait for rate limit reset
2. Implement request caching
3. Add authentication to SearxNG (if available)
4. Increase rate limits in SearxNG config

Related Documentation
=====================

- :doc:`bidirectional` - How bidirectional communication works
- :doc:`specialists` - Creating new specialists
- :doc:`specialist_rag` - Dynamic documentation system
