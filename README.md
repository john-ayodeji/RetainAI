# RetainAI
RetainAI predicts customer churn, clearly explains why it happens, and help businesses take the right actions to keep users

retention-intelligence/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── ml/
│   ├── train.py
│   ├── preprocess.py
│   ├── evaluate.py
│   ├── explain.py
│   ├── predict.py
│   └── artifacts/
│       ├── model.pkl
│       ├── scaler.pkl
│       └── feature_names.json
│
├── api/
│   ├── main.py
│   ├── routers/
│   │   ├── predict.py
│   │   ├── explain.py
│   │   └── simulate.py
│   ├── services/
│   │   ├── llm_service.py
│   │   └── shap_service.py
│   ├── schemas.py
│   └── config.py
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── app/                            # Next.js App Router root
│   │   │   ├── layout.tsx                  # Root layout: fonts, global providers, metadata
│   │   │   ├── page.tsx                    # / → redirects to /dashboard
│   │   │   ├── globals.css                 # Global styles, Tailwind imports
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx                # /dashboard → customer list + summary stats
│   │   │   │
│   │   │   └── customers/
│   │   │       └── [id]/
│   │   │           └── page.tsx            # /customers/[id] → full analysis for one customer
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                         # Small reusable primitives
│   │   │   │   ├── RiskBadge.tsx           # HIGH / MEDIUM / LOW pill with color
│   │   │   │   ├── StatCard.tsx            # Single metric card (churn %, total at-risk, etc.)
│   │   │   │   └── Spinner.tsx             # Loading state
│   │   │   │
│   │   │   ├── customer/                   # Customer-specific components
│   │   │   │   ├── CustomerCard.tsx        # Profile card: name, plan, tenure, risk badge
│   │   │   │   ├── CustomerTable.tsx       # Paginated table of all customers on dashboard
│   │   │   │   └── CustomerFilters.tsx     # Filter bar: risk level, subscription, contract
│   │   │   │
│   │   │   ├── analysis/                   # Prediction + explainability components
│   │   │   │   ├── ShapChart.tsx           # Horizontal bar chart of top SHAP factors (Recharts)
│   │   │   │   ├── ChurnGauge.tsx          # Visual dial showing churn probability 0–100%
│   │   │   │   └── WhatIfPanel.tsx         # Sliders to modify features + live re-prediction
│   │   │   │
│   │   │   └── chat/
│   │   │       ├── ChatPanel.tsx           # Full Q&A interface container
│   │   │       ├── ChatMessage.tsx         # Single message bubble (user or AI)
│   │   │       └── ChatInput.tsx           # Input box + send button
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                      # All fetch calls to FastAPI (predict, explain, simulate)
│   │   │   ├── types.ts                    # Shared TypeScript types: Customer, Prediction, ShapResult
│   │   │   └── utils.ts                    # Helpers: formatRisk(), formatCurrency(), cn() for classnames
│   │   │
│   │   └── hooks/
│   │       ├── usePredict.ts               # Fetches prediction for a customer, manages loading state
│   │       ├── useExplain.ts               # Sends question to /explain, streams or awaits LLM response
│   │       └── useSimulate.ts              # Sends modified feature set to /simulate, returns new prob
│   │
│   ├── .env.local                          # NEXT_PUBLIC_API_URL=http://localhost:8000
│   ├── next.config.ts                      # Next.js config: API rewrites to FastAPI to avoid CORS
│   ├── tailwind.config.ts                  # Tailwind config: theme, colors, fonts
│   ├── tsconfig.json                       # TypeScript config
│   └── package.json
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_training.ipynb
│   └── 03_shap_analysis.ipynb
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md