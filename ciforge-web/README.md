# CIForge — Next.js SaaS Frontend

## Setup Instructions

### 1. Create Next.js App
```bash
npx create-next-app@latest ciforge-web --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd ciforge-web
```

### 2. Install Dependencies
```bash
npm install next-auth @auth/prisma-adapter
npm install prisma @prisma/client
npm install axios swr zustand
npm install framer-motion
npm install lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs @radix-ui/react-toast
npm install clsx tailwind-merge
npm install recharts
npm install react-syntax-highlighter
npm install @types/react-syntax-highlighter
```

### 3. Copy all src/ files from this project

### 4. Setup .env.local
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
DATABASE_URL=your-postgres-url
CIFORGE_API_URL=http://localhost:8000
```

### 5. Run
```bash
npm run dev
```
