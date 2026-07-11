# Lockstep

Next.js full-stack starter with Supabase Postgres. The app uses Route Handlers for the API layer (no separate backend service).

- **Repository:** [github.com/gorwelin/lockstep](https://github.com/gorwelin/lockstep)
- **Dev URL:** [http://localhost:3001](http://localhost:3001)
- **Business plan:** [`plan/`](plan/) (docs, charts, report)

## Prerequisites

- Node.js 20+
- npm
- A [Supabase](https://supabase.com) cloud project (free tier)
- GitHub CLI (`gh`) authenticated as **gorwelin** for repo operations

## Port strategy

Lockstep runs on **port 3001** to avoid conflicts with other local services:

| Port | Known use | Avoid |
|------|-----------|-------|
| 80 | unilink-cli workstation mirror | Yes |
| 3000 | optima-software (`nx serve`) | Yes |
| 4200 | UCase UI (`nx serve`) | Yes |
| 8091+ | UCase .NET services | Yes |
| 81–99, 7083 | CMS docker-compose stacks | Yes |

Check the port is free before starting:

```bash
lsof -i :3001
```

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.example .env.local
```

Edit `.env.local` with values from your Supabase project (**Settings → API**):

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 3. Create the database table

In the Supabase Dashboard → **SQL Editor**, run:

```sql
-- or use supabase/seed-health-checks.sql
create table if not exists public.health_checks (
  id bigint generated always as identity primary key,
  checked_at timestamptz not null default now()
);

insert into public.health_checks default values;
```

### 4. Run the dev server

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) and verify [http://localhost:3001/api/health](http://localhost:3001/api/health) returns `db: "connected"`.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server on port 3001 |
| `npm run build` | Production build |
| `npm run start` | Start production server on port 3001 |
| `npm run lint` | Run ESLint |

## Project structure

```
src/
├── app/
│   ├── api/health/route.ts   # Health + Supabase connectivity check
│   ├── layout.tsx
│   └── page.tsx
├── lib/supabase/
│   ├── client.ts             # Browser client
│   ├── middleware.ts         # Session refresh helper
│   └── server.ts             # Server/client Route Handler client
└── middleware.ts             # Supabase cookie refresh
supabase/
└── seed-health-checks.sql    # Initial table seed SQL
plan/
├── docs/                     # Business plan markdown
├── charts/                   # Generated charts
├── report/                   # Presentable HTML report
├── financials/               # Unit economics model
└── scripts/                  # Chart/report generators
```

## Business plan

Planning docs live under [`plan/`](plan/). See [`plan/README.md`](plan/README.md) for contents and how to rebuild the report.

## GitHub

Repo: [github.com/gorwelin/lockstep](https://github.com/gorwelin/lockstep) on the **gorwelin** personal account (`master` only).

Push with the gorwelin SSH host:

```bash
git remote -v   # should use github.com-gorwelin
```

## Health check

`GET /api/health` returns:

```json
{
  "status": "ok",
  "db": "connected",
  "healthCheckCount": 1
}
```

Without Supabase credentials or the `health_checks` table, it returns `503` with a helpful error message.
