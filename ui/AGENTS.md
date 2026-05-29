<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

Build a Next.js dashboard page for a customer churn prediction system called RetainAI.

DESIGN SYSTEM

Theme: Dark. Professional. Data-dense but not cluttered.

Color tokens (define as Tailwind config or CSS variables):
  --bg-base:       #080a0f   (page background)
  --bg-surface:    #111520   (cards, panels)
  --bg-elevated:   #1a1f2e   (table rows hover, inputs)
  --border:        rgba(255,255,255,0.07)
  --border-strong: rgba(255,255,255,0.12)
  --text-primary:  #f0f2f8
  --text-muted:    #8891aa
  --text-faint:    #6b7590
  --accent-blue:   #4f7fff
  --risk-high:     #ff5c5c   (text: #ff7b7b, bg: rgba(255,92,92,0.10))
  --risk-medium:   #ffb547   (text: #ffca7a, bg: rgba(255,181,71,0.10))
  --risk-low:      #2dd98f   (text: #5eeaaa, bg: rgba(45,217,143,0.10))

  Typography:
  Display/headings: Syne (Google Font), weights 700–800
  Body: DM Sans (Google Font), weights 300–500
  Monospace (numbers, probabilities, code): DM Mono

Border radius: 12px for cards, 8px for pills/badges, 6px for inputs
No box shadows. Borders only.

PAGE: /dashboard

LAYOUT
Full-width dark page. Fixed top navbar (60px tall). Page content starts below navbar with 32px padding on all sides.

NAVBAR
Left: logo — small green pulsing dot + "RetainAI" in Syne bold 18px
Right: nothing else needed for now

SECTION 1 — SUMMARY STATS (top of page, below navbar)

Four stat cards in a horizontal row, equal width, 16px gap.
Each card: bg-surface, border, border-radius 12px, padding 20px 24px.

Card 1: Total Customers       — large number, muted label below
Card 2: High Risk             — number in risk-high color
Card 3: Medium Risk           — number in risk-medium color  
Card 4: Overall Churn Rate    — number as percentage, neutral color

The numbers in these cards must react to the active filters. If the user filters to "High Risk only", Card 1 shows only the filtered count, etc.

SECTION 2 — FILTER BAR

Sits between stat cards and the table. Left-aligned. Three filter controls in a row:

1. Risk Level — segmented control or select: All | High | Medium | Low
2. Subscription — select: All | Basic | Standard | Premium  
3. Contract — select: All | Monthly | Quarterly | Annual

All filters are AND logic. Filters update the stat cards and table instantly (client-side, no API call needed for filtering).

A small muted text on the right showing: "Showing X of Y customers"

SECTION 3 — CUSTOMER TABLE

Full-width. bg-surface card wrapping the table. 1px border. 12px border-radius.

Table toolbar (inside the card, above the table):
  Left: "All Customers" label in 14px Syne 600
  Right: a search input — searches by customer name, placeholder "Search customers..."

Table columns:
  1. Customer    — initials avatar circle (bg-elevated, accent-blue text) + full name + email below in muted text
  2. Plan        — Basic / Standard / Premium as a plain muted text label
  3. Contract    — Monthly / Quarterly / Annual
  4. Tenure      — "X months" in muted text
  5. Churn Prob  — percentage in DM Mono, colored by risk (high = risk-high color, med = risk-medium, low = risk-low)
  6. Risk        — pill badge with risk level. Style:
                    HIGH   → background risk-high bg, text risk-high text, border 1px risk-high at 20% opacity
                    MEDIUM → same pattern with risk-medium colors
                    LOW    → same pattern with risk-low colors
  7. Action      — "Analyse →" text button in accent-blue, no border, hover underline. Links to /customers/[id]

Table rows:
  Default bg: transparent
  Hover bg: bg-elevated
  Border between rows: 1px var(--border)
  Row height: 56px
  Font size: 13px body, 13px DM Mono for the probability

Default sort: churn probability descending (highest risk first).
Clicking the "Churn Prob" column header toggles sort asc/desc.

Pagination: simple previous/next at the bottom right of the card. Show 10 rows per page.


INTERACTIONS

1. Filters update stat cards and table instantly — no page reload
3. Clicking sort on Churn Prob column toggles asc/desc
4. "Analyse →" navigates to /customers/[id] (stub page is fine, just needs to resolve)
5. Pagination updates the visible rows, stat cards always reflect full filtered set

in /customers/[id], asides what we already have, it should have like chatgpt kind of ui, that tags the customers info to send to the /explain api route