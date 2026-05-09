# ConstructProcure AI - Frontend Dashboard

This is the frontend dashboard for the ConstructProcure AI platform. It provides a clean, minimal interface to submit procurement requests and track the multi-agent AI pipeline's execution and results.

## Technologies Used
- React + Vite
- TypeScript
- TailwindCSS v4
- Axios
- React Router DOM
- Lucide React (Icons)
- React Markdown

## Project Structure
```text
frontend/
├── src/
│   ├── api/          # Axios client and API types/interfaces
│   ├── components/   # Reusable UI components
│   ├── pages/        # Route pages (Home, Results)
│   ├── App.tsx       # Main router setup
│   ├── main.tsx      # Entry point
│   └── index.css     # TailwindCSS entry and globals
├── vite.config.ts    # Vite and Tailwind config
└── package.json      # Dependencies and scripts
```

## Setup Instructions

### 1. Configure Environment
Create `.env.development` for local development and `.env.production` for production builds:

```env
# .env.development
VITE_API_BASE_URL=http://localhost:8000
```

```env
# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

### 2. Install Dependencies
Run the following command to install all necessary packages:
```bash
npm install
```

### 3. Run Locally
Start the local development server:
```bash
npm run dev
```

### 4. Build for Production
To create an optimized production build:
```bash
npm run build
```
The output will be in the `dist/` directory.

## Features
- **Submit Procurement Requests**: Input material type, quantity, unit, and deadline to kick off the AI pipeline.
- **Track Status**: Polls the backend API to show the real-time progress of the pipeline.
- **View Results**: Compare top suppliers, review detailed quotations, and read the final analyst recommendation.
