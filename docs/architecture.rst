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
       web [label="Web Service\nNginx + Frontend\n(Port 5000)"];
       brain [label="Brain Service\nFastAPI Backend\n(Port 7000)"];
       ollama [label="Ollama Service\nLLM Inference\n(Port 11434)"];
       chroma [label="Chroma Service\nVector Database\n(Port 8000)"];
       consolidation [label="Memory\nConsolidation\n(Nightly Cron)"];
       scripts [label="Scripts Service\nTooling Container\n(On-demand)"];
       
       user -> web [label="HTTP"];
       web -> brain [label="API Proxy\n/api/* → /v1/*"];
       brain -> ollama [label="LLM Requests"];
       brain -> chroma [label="RAG Queries"];
       consolidation -> brain [label="Uses"];
       scripts -> chroma [label="Maintenance"];
       scripts -> brain [label="Testing"];
       
       {rank=same; web; brain;}
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

Data Flow: Conversation Turn
----------------------------

Complete flow for processing and storing a conversation turn:

.. graphviz::

   digraph conversation_turn {
       rankdir=TB;
       node [shape=box, style=filled, fillcolor=lightblue];
       
       user_msg [label="User Message", fillcolor=lightgreen];
       api [label="POST /v1/chat/stream"];
       context [label="Build Request\nContext"];
       specialists [label="Execute\nSpecialists"];
       rag_query [label="RAG Query\n(Persona, FAQ,\nMemory, Turns)"];
       prompt [label="Build Final\nPrompt"];
       llm [label="Stream LLM\nResponse"];
       store_turn [label="Store Turn\nin Chroma"];
       user_response [label="User Sees\nResponse", fillcolor=lightgreen];
       
       user_msg -> api;
       api -> context;
       context -> specialists;
       specialists -> rag_query;
       rag_query -> prompt;
       prompt -> llm;
       llm -> store_turn;
       llm -> user_response;
       store_turn -> rag_query [label="Available for\nNext Query", style=dashed];
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
