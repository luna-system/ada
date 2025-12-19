Architecture
============

This document provides visual representations of Ada's system architecture, data flow, and component interactions.

System Overview
---------------

Ada is composed of several containerized services orchestrated via Docker Compose:

.. graphviz::

   digraph system {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user [label="User\nBrowser", fillcolor=lightgreen];
       matrix_user [label="Matrix\nUsers", fillcolor=lightgreen];
       web [label="Web Service\nNginx + Frontend\n(Port 5000)"];
       matrix_bridge [label="Matrix Bridge\nmatrix-nio Client", fillcolor=lightcyan];
       brain [label="Brain Service\nFastAPI Backend\n(Port 7000)"];
       ollama [label="Ollama Service\nLLM Inference\n(Port 11434)"];
       chroma [label="Chroma Service\nVector Database\n(Port 8000)"];
       consolidation [label="Memory\nConsolidation\n(Nightly Cron)"];
       scripts [label="Scripts Service\nTooling Container\n(On-demand)"];
       
       user -> web [label="HTTP"];
       matrix_user -> matrix_bridge [label="Matrix Protocol"];
       web -> brain [label="API Proxy\n/api/* → /v1/*"];
       matrix_bridge -> brain [label="/v1/chat/stream"];
       brain -> ollama [label="LLM Requests"];
       brain -> chroma [label="RAG Queries"];
       consolidation -> brain [label="Uses"];
       scripts -> chroma [label="Maintenance"];
       scripts -> brain [label="Testing"];
       
       {rank=same; user; matrix_user;}
       {rank=same; web; matrix_bridge;}
       {rank=same; brain;}
       {rank=same; ollama; chroma;}
   }

Request Flow
------------

This diagram shows how a user message flows through the system:

.. graphviz::

   digraph request_flow {
       rankdir=LR;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user [label="User Message", fillcolor=lightgreen];
       frontend [label="Frontend\nSvelte"];
       nginx [label="Nginx\nReverse Proxy"];
       brain [label="Brain API\nFastAPI"];
       prompt [label="Prompt Builder"];
       rag [label="RAG Store\n(Chroma)"];
       llm [label="LLM\n(Ollama)"];
       stream [label="SSE Stream", fillcolor=lightyellow];
       
       user -> frontend -> nginx -> brain;
       brain -> prompt;
       prompt -> rag [label="Retrieve\nContext"];
       rag -> prompt [label="Persona,\nFAQ,\nMemories"];
       prompt -> llm [label="Enriched\nPrompt"];
       llm -> stream [label="Tokens"];
       stream -> nginx -> frontend -> user;
       
       {rank=same; frontend; nginx;}
   }

Specialist System Architecture
-------------------------------

The plugin-based specialist system allows extensible capabilities:

.. graphviz::

   digraph specialists {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user [label="User Request", fillcolor=lightgreen];
       brain [label="Brain API"];
       registry [label="Specialist Registry\n(Auto-discovery)"];
       
       ocr [label="OCR Specialist\n📄 Priority: HIGH"];
       media [label="Media Specialist\n🎧 Priority: MEDIUM"];
       websearch [label="Web Search\n🔍 Priority: HIGH"];
       
       prompt_builder [label="Prompt Builder"];
       llm [label="LLM"];
       
       user -> brain;
       brain -> registry [label="request_context"];
       registry -> ocr [label="should_activate()?"];
       registry -> media [label="should_activate()?"];
       registry -> websearch [label="should_activate()?"];
       
       ocr -> registry [label="context_text"];
       media -> registry [label="context_text"];
       websearch -> registry [label="context_text"];
       
       registry -> prompt_builder [label="Sorted by\nPriority"];
       prompt_builder -> llm [label="Enriched\nPrompt"];
   }

Context Caching System (v2.1)
-----------------------------

Multi-timescale caching reduces redundant RAG queries and token usage:

- **Personas**: 24-hour TTL (identity rarely changes)
- **FAQs**: 24-hour TTL (knowledge base updates infrequently)
- **Memories**: 5-minute TTL (balance freshness vs performance)
- **Conversations**: 1-hour TTL (recent turns cached per session)

**Benefits:**
- Reduces ChromaDB queries by ~70% for repeated context
- Lower latency on cache hits (ms vs seconds)
- LRU eviction prevents unbounded growth
- Per-request cache stats logged for monitoring

**Implementation:** ``brain/context_cache.py`` (MultiTimescaleCache) integrated into ``PromptAssembler``

RAG System Components
---------------------

The Retrieval-Augmented Generation system provides contextual memory:

.. graphviz::

   digraph rag {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       prompt [label="User Query"];
       embed [label="Embedding\nGenerator\n(nomic-embed-text)"];
       chroma [label="ChromaDB\nVector Store"];
       
       persona [label="Persona\n(Identity)", fillcolor=lightyellow];
       faq [label="FAQ Entries\n(Knowledge)", fillcolor=lightyellow];
       memory [label="Memories\n(Long-term)", fillcolor=lightyellow];
       turns [label="Conversation\nTurns (History)", fillcolor=lightyellow];
       specialist_docs [label="Specialist\nDocs (Dynamic)", fillcolor=lightyellow];
       
       prompt -> embed;
       embed -> chroma [label="768-dim\nVector"];
       
       chroma -> persona [label="Query"];
       chroma -> faq [label="Query"];
       chroma -> memory [label="Query"];
       chroma -> turns [label="Query"];
       chroma -> specialist_docs [label="Query"];
       
       persona -> prompt [label="Context"];
       faq -> prompt [label="Context"];
       memory -> prompt [label="Context"];
       turns -> prompt [label="Context"];
       specialist_docs -> prompt [label="Context"];
   }

Bidirectional Specialist Flow
------------------------------

How the LLM can request specialist execution mid-response:

.. graphviz::

   digraph bidirectional {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       start [label="LLM Generation\nStarts", fillcolor=lightgreen];
       token [label="Stream Tokens"];
       detect [label="Detect Request\nPattern", shape=diamond, fillcolor=lightyellow];
       pause [label="Pause\nGeneration", fillcolor=orange];
       execute [label="Execute\nSpecialist"];
       inject [label="Inject Result\ninto Context"];
       resume [label="Resume\nGeneration", fillcolor=lightgreen];
       done [label="Complete", fillcolor=lightgreen];
       
       start -> token;
       token -> detect;
       detect -> token [label="No Request"];
       detect -> pause [label="SPECIALIST_REQUEST[...]"];
       pause -> execute;
       execute -> inject;
       inject -> resume;
       resume -> token;
       token -> done [label="Stream\nComplete"];
   }

Testing Infrastructure
----------------------

The scripts container provides isolated testing environment:

.. graphviz::

   digraph testing {
       rankdir=LR;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       dev [label="Developer", fillcolor=lightgreen];
       scripts [label="Scripts Container\nPython 3.13 + uv"];
       pytest [label="Pytest\nTest Suite"];
       health [label="Health Check\nScript"];
       
       tests_rag [label="tests/test_rag.py\n(6 tests)", fillcolor=lightyellow];
       tests_prompt [label="tests/test_prompt_builder.py\n(2 tests)", fillcolor=lightyellow];
       tests_specialists [label="tests/test_specialists.py\n(1 test)", fillcolor=lightyellow];
       
       brain [label="Brain Service"];
       chroma [label="Chroma Service"];
       ollama [label="Ollama Service"];
       
       dev -> scripts [label="./scripts/run.sh test"];
       scripts -> pytest;
       scripts -> health;
       
       pytest -> tests_rag;
       pytest -> tests_prompt;
       pytest -> tests_specialists;
       
       tests_rag -> chroma;
       tests_rag -> brain;
       tests_prompt -> chroma;
       tests_specialists -> chroma;
       
       health -> chroma;
       health -> brain;
   }

Contextual Router Architecture (v2.7+)
--------------------------------------

Intelligent query routing based on 22 patterns across 5 categories:

.. graphviz::

   digraph contextual_router {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user_msg [label="User Message", fillcolor=lightgreen];
       router [label="Contextual Router\n22 Patterns", fillcolor=orange];
       
       trivial [label="TRIVIAL\n(greetings, thanks)"];
       fact [label="FACT RECALL\n(recent memories)"];
       analytical [label="ANALYTICAL\n(requires reasoning)"];
       creative [label="CREATIVE\n(needs inspiration)"];
       code [label="CODE\n(development tasks)"];
       
       lightweight [label="Lightweight RAG\n(persona only)", fillcolor=lightyellow];
       focused [label="Focused RAG\n(recent memories)", fillcolor=lightyellow];
       full [label="Full RAG\n(all context)", fillcolor=lightyellow];
       
       user_msg -> router;
       router -> trivial [label="Pattern:\nhello|thanks"];
       router -> fact [label="Pattern:\nwhat did I"];
       router -> analytical [label="Pattern:\nwhy|how|explain"];
       router -> creative [label="Pattern:\nwrite|imagine"];
       router -> code [label="Pattern:\nfunction|class"];
       
       trivial -> lightweight;
       fact -> focused;
       analytical -> full;
       creative -> full;
       code -> full;
   }

Multi-Timescale Cache Architecture (v2.1+)
-------------------------------------------

Three-tier caching for performance optimization:

.. graphviz::

   digraph caching {
       rankdir=LR;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       request [label="Chat Request", fillcolor=lightgreen];
       cache_check [label="Check Caches", fillcolor=orange];
       
       persona_cache [label="Persona Cache\nTTL: 24hr", fillcolor=lightyellow];
       faq_cache [label="FAQ Cache\nTTL: 24hr", fillcolor=lightyellow];
       memory_cache [label="Memory Cache\nTTL: 5min", fillcolor=lightyellow];
       response_cache [label="Response Cache\nTTL: 1hr\n(v2.8+)", fillcolor=lightyellow];
       
       chroma [label="ChromaDB\n(Miss)"];
       
       request -> cache_check;
       cache_check -> persona_cache [label="HIT"];
       cache_check -> faq_cache [label="HIT"];
       cache_check -> memory_cache [label="HIT"];
       cache_check -> response_cache [label="HIT\n(full response)"];
       cache_check -> chroma [label="MISS"];
       
       {rank=same; persona_cache; faq_cache; memory_cache; response_cache;}
   }

Parallel Optimization Architecture (v2.9+)
-------------------------------------------

2.5x speedup through parallel RAG retrieval and specialist execution:

.. graphviz::

   digraph parallel {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       request [label="Chat Request", fillcolor=lightgreen];
       parallel [label="ThreadPoolExecutor\n4 Workers", fillcolor=orange];
       
       subgraph cluster_rag {
           label="Parallel RAG (3.96x speedup)";
           style=filled;
           fillcolor=lightgray;
           
           persona [label="Get Persona\n20ms"];
           memories [label="Get Memories\n80ms"];
           faqs [label="Get FAQs\n40ms"];
           turns [label="Get Turns\n60ms"];
       }
       
       subgraph cluster_specialists {
           label="Parallel Specialists (2.98x speedup)";
           style=filled;
           fillcolor=lightgray;
           
           ocr [label="OCR\n(HIGH priority)"];
           web [label="Web Search\n(HIGH priority)"];
           media [label="Media\n(MEDIUM priority)"];
       }
       
       gather [label="Gather Results\n80ms total\n(was 200ms)", fillcolor=lightgreen];
       llm [label="LLM Inference"];
       
       request -> parallel;
       parallel -> persona;
       parallel -> memories;
       parallel -> faqs;
       parallel -> turns;
       parallel -> ocr;
       parallel -> web;
       
       persona -> gather;
       memories -> gather;
       faqs -> gather;
       turns -> gather;
       ocr -> gather;
       web -> gather;
       media -> gather [style=dashed, label="Sequential"];
       
       gather -> llm;
   }

Data Flow: Conversation Turn (Optimized v2.9)
----------------------------------------------

Complete flow with router, caching, and parallel optimizations:

.. graphviz::

   digraph conversation_turn_v29 {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user_msg [label="User Message", fillcolor=lightgreen];
       api [label="POST /v1/chat/stream"];
       router [label="Contextual Router\n~10ms", fillcolor=orange];
       response_cache [label="Response Cache\nCheck", fillcolor=lightyellow];
       parallel [label="Parallel Context\n~80ms", fillcolor=orange];
       specialists [label="Execute\nSpecialists"];
       prompt [label="Build Final\nPrompt"];
       llm [label="Stream LLM\nResponse"];
       store_turn [label="Store Turn\nin Chroma"];
       cache_response [label="Cache Response", fillcolor=lightyellow];
       user_response [label="User Sees\nResponse", fillcolor=lightgreen];
       
       user_msg -> api;
       api -> router;
       router -> response_cache;
       response_cache -> user_response [label="HIT (~40%)", style=dashed, color=green];
       response_cache -> parallel [label="MISS"];
       parallel -> specialists;
       specialists -> prompt;
       prompt -> llm;
       llm -> store_turn;
       llm -> cache_response;
       llm -> user_response;
       store_turn -> parallel [label="Available for\nNext Query", style=dashed];
   }

Deployment Architecture
-----------------------

Production deployment structure:

.. graphviz::

   digraph deployment {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       internet [label="Internet", fillcolor=lightgreen, shape=cloud];
       nginx_proxy [label="Nginx Reverse Proxy\nSSL Termination"];
       
       subgraph cluster_ada {
           label="Ada Docker Stack";
           style=filled;
           fillcolor=lightgray;
           
           web [label="Web Container"];
           brain [label="Brain Container"];
           ollama [label="Ollama Container"];
           chroma [label="Chroma Container"];
           consolidation [label="Consolidation\nContainer"];
       }
       
       data_volume [label="./data/\nPersistent Volume", shape=cylinder, fillcolor=lightyellow];
       
       internet -> nginx_proxy [label="HTTPS"];
       nginx_proxy -> web [label="HTTP"];
       web -> brain;
       brain -> ollama;
       brain -> chroma;
       consolidation -> brain;
       
       chroma -> data_volume [label="Store"];
       ollama -> data_volume [label="Store\nModels"];
   }

Resources
---------

- See :doc:`specialists` for detailed specialist system documentation
- See :doc:`testing` for testing infrastructure details
- See :doc:`development` for scripts container usage
- See :doc:`api_usage` for API endpoint documentation
