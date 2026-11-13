# Project Structure

```text
kutana-ai-mvp/
├── apps/
│   ├── mobile-client/     # Future Flutter app
│   └── web-onboarding/    # Next.js/Tailwind — user-facing AI chat interface
├── packages/
│   └── ui-components/     # Shared design system
├── services/
│   ├── core-backend/      # Supabase (PostgreSQL, Auth, Row Level Security)
│   └── ai-engine/         # Python/FastAPI — LangChain, Claude API integration, pgvector
└── infrastructure/        # GitHub Actions workflows, Dockerfiles
```
