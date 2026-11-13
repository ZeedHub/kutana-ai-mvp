# kutana-ai-mvp
Investor MVP for Kutana AI. A privacy-first, LLM-driven matchmaking engine utilizing pgvector embeddings for psychological compatibility scoring.
# Kutana AI – The Private AI Profiler (MVP)

**Status:** Pre-Seed Proof of Concept 
**Target Market:** Nairobi, Kenya

Kutana AI is a next-generation matchmaking engine that replaces superficial swipe mechanics with deep conversational profiling. This repository contains the investor-ready MVP demonstrating the core algorithmic loop: 

1. **Conversational Ingestion:** A token-optimized chat interface that extracts psychological traits, financial expectations, and unfiltered lifestyle realities within a strict, cost-controlled 10-message limit.
2. **Anonymized Vectorization (ODPC Compliant):** Raw chat data is instantly summarized and converted into embeddings using `pgvector`. PII and raw chat logs are systematically destroyed to comply with the Kenya Data Protection Act (2019).
3. **Compatibility Matrix:** High-speed cosine similarity searches evaluate user vectors against the database to generate a granular, category-by-category compatibility leaderboard.

## Tech Stack
* **Client/Onboarding UI:** Next.js, Tailwind CSS
* **Backend AI Engine:** Python, FastAPI, LangChain, Claude 3.5 API
* **Database & Security:** Supabase (PostgreSQL + `pgvector`), Row Level Security (RLS)
