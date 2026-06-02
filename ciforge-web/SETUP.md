# CIForge Next.js SaaS — Complete Setup Guide

## Project Structure

```
ciforge-web/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx          ← Login page
│   │   ├── (dashboard)/
│   │   │   └── dashboard/
│   │   │       ├── layout.tsx        ← Protected layout
│   │   │       ├── page.tsx          ← Overview
│   │   │       ├── pipelines/
│   │   │       │   ├── page.tsx      ← Pipeline list
│   │   │       │   └── new/
│   │   │       │       └── page.tsx  ← Generate new
│   │   │       └── settings/
│   │   │           └── page.tsx      ← Settings
│   │   ├── api/
│   │   │   ├── auth/[...nextauth]/
│   │   │   │   └── route.ts          ← Auth handler
│   │   │   └── pipelines/
│   │   │       ├── generate/route.ts ← Generate API
│   │   │       └── status/[id]/route.ts
│   │   ├── layout.tsx                ← Root layout
│   │   ├── page.tsx                  ← Landing page
│   │   └── globals.css
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── stats-row.tsx
│   │   │   ├── pipeline-list.tsx
│   │   │   ├── pipeline-chart.tsx
│   │   │   ├── pipeline-viewer.tsx
│   │   │   ├── generate-modal.tsx
│   │   │   ├── quick-generate.tsx
│   │   │   ├── language-breakdown.tsx
│   │   │   └── activity-feed.tsx
│   │   ├── landing/
│   │   │   ├── hero.tsx
│   │   │   └── sections.tsx          ← All other sections
│   │   ├── layout/
│   │   │   ├── navbar.tsx
│   │   │   └── footer.tsx
│   │   ├── ui/
│   │   │   ├── particle-canvas.tsx
│   │   │   └── toaster.tsx
│   │   └── providers.tsx
│   ├── hooks/
│   │   └── use-generate.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── store/
│   │   └── pipeline-store.ts
│   ├── types/
│   │   └── index.ts
│   ├── auth.ts                       ← NextAuth config
│   └── middleware.ts                 ← Route protection
├── .env.example
├── next.config.js
├── tailwind.config.ts
└── package.json
```

---

## Step 1 — Create Next.js App

```bash
npx create-next-app@latest ciforge-web \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd ciforge-web
```

---

## Step 2 — Install All Dependencies

```bash
npm install next-auth@beta axios swr zustand framer-motion lucide-react \
  @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs \
  @radix-ui/react-toast @radix-ui/react-select clsx tailwind-merge \
  recharts react-syntax-highlighter

npm install -D @types/react-syntax-highlighter
```

---

## Step 3 — Copy All Files

Copy every file from this project into your `ciforge-web/` folder,
maintaining the exact same folder structure shown above.

---

## Step 4 — Fix sections.tsx

The `sections.tsx` file exports multiple components AND has a `"use client"` 
directive + useState inside it. Split the CodeDemo into its own file:

Create `src/components/landing/code-demo.tsx` and move the CodeDemo function there.
Then import it in `sections.tsx` and re-export.

---

## Step 5 — Setup Environment

```bash
cp .env.example .env.local
```

Fill in `.env.local`:

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=run-openssl-rand-base64-32-here
GITHUB_CLIENT_ID=get-from-github-settings
GITHUB_CLIENT_SECRET=get-from-github-settings
CIFORGE_API_URL=http://localhost:8000
```

### Get GitHub OAuth credentials:
1. Go to github.com/settings/developers
2. Click "New OAuth App"
3. Homepage URL: `http://localhost:3000`
4. Callback URL: `http://localhost:3000/api/auth/callback/github`
5. Copy Client ID and Secret

---

## Step 6 — Update tailwind.config.ts

Make sure `globals.css` has:
```css
@import url("https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600&display=swap");
```

---

## Step 7 — Start Both Servers

Terminal 1 — FastAPI backend:
```bash
cd CIForge
venv312\Scripts\activate
poetry run uvicorn src.api.server:create_api --factory --host 0.0.0.0 --port 8000
```

Terminal 2 — Next.js frontend:
```bash
cd ciforge-web
npm run dev
```

Open: http://localhost:3000

---

## Step 8 — Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set env vars in Vercel dashboard or:
vercel env add NEXTAUTH_SECRET
vercel env add GITHUB_CLIENT_ID
vercel env add GITHUB_CLIENT_SECRET
vercel env add CIFORGE_API_URL
```

---

## Step 9 — Deploy Backend to Railway

1. Go to railway.app
2. New Project → Deploy from GitHub repo
3. Select your CIForge repo
4. Add env vars:
   - `CICD_AGENT_LLM_PROVIDER=groq`
   - `CICD_AGENT_GROQ_API_KEY=your-key`
5. Set start command: `poetry run uvicorn src.api.server:create_api --factory --host 0.0.0.0 --port $PORT`

---

## Pages Summary

| Route | Description |
|---|---|
| `/` | Landing page with hero, features, demo |
| `/login` | Sign in with GitHub or email |
| `/dashboard` | Overview with stats, recent pipelines |
| `/dashboard/pipelines` | All pipelines with filters |
| `/dashboard/pipelines/new` | Generate new pipeline |
| `/dashboard/settings` | Profile, API keys, notifications |

---

## All Features Working

- ✅ Landing page with particle canvas
- ✅ Scroll animations with Framer Motion
- ✅ GitHub OAuth login
- ✅ Protected dashboard routes (middleware)
- ✅ Sidebar navigation
- ✅ Stats cards with hover effects
- ✅ Area chart (Recharts)
- ✅ Pipeline list with status badges
- ✅ Generate modal with animated progress
- ✅ Full pipeline generation page
- ✅ Pipeline YAML viewer with copy + download
- ✅ Quick generate widget
- ✅ Language breakdown bars
- ✅ Activity feed
- ✅ Settings page
- ✅ Toast notifications
- ✅ Zustand pipeline store (persisted)
- ✅ API routes proxying to FastAPI
- ✅ TypeScript throughout
- ✅ Mobile responsive
