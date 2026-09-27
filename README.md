# Hi, I am Andar 👋

I build small, practical web apps and AI tools. Most of my work is in wine retail tech at Wine Adore and in tools for my parish community in Bandung.

## What I worked on this month (September 2026)

### 🍷 WineAssist — AI wine recommendation console

A staff console for Wine Adore. Staff type a customer request, and WineAssist recommends wines from the 213-bottle store catalog.

- I started the project on 15 September and shipped version `0.4.5` in 10 days: 150+ commits and 40 pull requests.
- A chain of OpenAI Agents SDK stages parses the request, searches the catalog, and writes the answer.
- Catalog search scores each wine as 70% preference fit plus 30% embedding similarity. PostgreSQL with pgvector holds the embeddings.
- Staff can generate a sales pitch for a wine or search the web for similar wines outside the catalog.
- A request log records the tokens and cost of each query, so I can test the cost of the pipeline.
- This month I also added CI hardening, grouped Dependabot updates, a backend sync job, and a phone layout pass.

`Python` `FastAPI` `OpenAI Agents SDK` `PostgreSQL` `pgvector` `React` `TypeScript` `Vite`

### ⚖️ Weight Journal — personal weight tracker

A small installable web app to log weight, see the trend, and track a goal.

- Today, history, and settings views with a weight dial and a trend chart.
- Sign-in with Neon Auth. Drizzle ORM stores the entries in Neon Postgres.
- CSV export and offline support.

`Next.js 16` `React 19` `Neon` `Drizzle ORM` `PWA`

## Other projects

### ⛪ [Presensi Katekumen Digital](https://github.com/ojeeeeedev/absensikatekumen) — QR attendance for a catechumen program

An attendance system for the Catechumenate program at St. Peter's Cathedral, Bandung. Facilitators scan a QR code on a phone, and the attendance goes directly to Google Sheets.

- Version `2.9.2`, with 600+ commits since November 2025.
- Vercel serverless functions verify the JWT session and send each scan to Google Apps Script.
- Student photos stay in private Supabase Storage. An authenticated proxy serves them.
- A mobile-first interface with a "liquid glass" style, haptic feedback, and profile search.

`JavaScript` `Vercel Functions` `Google Apps Script` `Google Sheets` `Supabase`

### 📈 Chart Tanpa Ribet — content system for an Indonesian investing account

A documented weekly workflow for an Instagram account about investing. AI prepares research, chart notes, captions, and performance reviews. A person approves every post before it goes public.

`Content ops` `ChatGPT Projects` `Canva` `Meta Business Suite`

### 🧪 Agents SDK experiments

Small scripts in JavaScript and Python to test agents, tools, and embeddings with the OpenAI Agents SDK.

## Tech I use

**Languages:** TypeScript, JavaScript, Python, SQL<br>
**Frontend:** React, Next.js, Vite, Tailwind CSS<br>
**Backend:** FastAPI, Node.js, Vercel Functions, Google Apps Script<br>
**Data:** PostgreSQL, pgvector, Neon, Supabase, Drizzle ORM, Google Sheets<br>
**AI:** OpenAI Agents SDK, embeddings, agent pipelines, token and cost tests<br>
**Tooling:** GitHub Actions, Dependabot, Docker, Claude Code

## Contact

- GitHub: [@ojeeeeedev](https://github.com/ojeeeeedev)
