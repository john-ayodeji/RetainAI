import Link from "next/link";

export default function Home() {
  return (
    <>
      <style>{`
        .lp-shell {
          font-family: 'DM Mono', ui-monospace, monospace;
          height: 100vh;
          width: 100vw;
          overflow: hidden;
          background: #f8f7f4;
          color: #1a1916;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr;
        }

        /* ── left panel ── */
        .lp-left {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 40px 48px;
          border-right: 0.5px solid rgba(0,0,0,.09);
        }
        .lp-wordmark {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 20px;
          font-weight: 600;
          letter-spacing: -.02em;
          color: #1a1916;
        }
        .lp-hero {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          gap: 20px;
        }
        .lp-eyebrow {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .22em;
          color: #a09d96;
        }
        .lp-headline {
          font-family: 'Fraunces', Georgia, serif;
          font-size: clamp(32px, 4vw, 52px);
          font-weight: 600;
          letter-spacing: -.03em;
          line-height: 1.08;
          color: #1a1916;
          max-width: 420px;
        }
        .lp-headline em {
          font-style: italic;
          font-weight: 300;
          color: #6e6b64;
        }
        .lp-sub {
          font-size: 13px;
          line-height: 1.7;
          color: #6e6b64;
          max-width: 360px;
        }
        .lp-actions {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
        }
        .lp-btn-primary {
          font-family: 'DM Mono', monospace;
          font-size: 12px;
          font-weight: 500;
          padding: 10px 22px;
          border-radius: 7px;
          background: #1a1916;
          color: #fff;
          border: 0.5px solid #1a1916;
          text-decoration: none;
          transition: opacity .15s;
          white-space: nowrap;
        }
        .lp-btn-primary:hover { opacity: .8; }
        .lp-btn-ghost {
          font-family: 'DM Mono', monospace;
          font-size: 12px;
          padding: 10px 22px;
          border-radius: 7px;
          background: transparent;
          color: #6e6b64;
          border: 0.5px solid rgba(0,0,0,.16);
          text-decoration: none;
          transition: all .15s;
          white-space: nowrap;
        }
        .lp-btn-ghost:hover { border-color: #1a1916; color: #1a1916; }
        .lp-footer {
          font-size: 10px;
          color: #a09d96;
          letter-spacing: .08em;
        }

        /* ── right panel ── */
        .lp-right {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 40px 48px;
          background: #fff;
        }
        .lp-right-label {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .2em;
          color: #a09d96;
          text-align: right;
        }
        .lp-stats {
          display: flex;
          flex-direction: column;
          gap: 1px;
          flex: 1;
          justify-content: center;
        }
        .lp-stat-row {
          display: flex;
          align-items: baseline;
          justify-content: space-between;
          padding: 18px 0;
          border-bottom: 0.5px solid rgba(0,0,0,.07);
        }
        .lp-stat-row:first-child { border-top: 0.5px solid rgba(0,0,0,.07); }
        .lp-stat-name {
          font-size: 11px;
          color: #a09d96;
          text-transform: uppercase;
          letter-spacing: .14em;
        }
        .lp-stat-val {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 32px;
          font-weight: 600;
          letter-spacing: -.02em;
          color: #1a1916;
        }
        .lp-stat-val.danger { color: #a32d2d; }
        .lp-stat-val.safe   { color: #3b6d11; }
        .lp-right-foot {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .lp-badge {
          font-size: 10px;
          padding: 4px 10px;
          border-radius: 50px;
          background: #eaf3de;
          color: #27500a;
          border: 0.5px solid #c0dd97;
          letter-spacing: .06em;
        }
        .lp-right-note {
          font-size: 10px;
          color: #a09d96;
        }

        /* ── mobile ── */
        @media (max-width: 680px) {
          .lp-shell {
            grid-template-columns: 1fr;
            grid-template-rows: auto auto;
            height: auto;
            min-height: 100vh;
            overflow: auto;
          }
          .lp-left {
            border-right: none;
            border-bottom: 0.5px solid rgba(0,0,0,.09);
            padding: 32px 24px;
            gap: 32px;
          }
          .lp-right {
            padding: 32px 24px;
            gap: 24px;
          }
          .lp-headline { font-size: 36px; }
          .lp-stat-val { font-size: 26px; }
        }
      `}</style>

      <div className="lp-shell">
        {/* ── left ── */}
        <div className="lp-left">
          <div className="lp-wordmark">RetainAI</div>

          <div className="lp-hero">
            <div className="lp-eyebrow">Churn intelligence</div>
            <h1 className="lp-headline">
              Know who's leaving <em>before</em> they do.
            </h1>
            <p className="lp-sub">
              RetainAI scores every customer in real time, surfaces churn risk,
              and gives your team the context to act - not just the data.
            </p>
            <div className="lp-actions">
              <Link href="/dashboard" className="lp-btn-primary">
                Open dashboard →
              </Link>
              <a
                href="https://nextjs.org/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="lp-btn-ghost"
              >
                Documentation
              </a>
            </div>
          </div>

          <div className="lp-footer">
            &copy; 2026 RetainAI. All rights reserved.
          </div>
        </div>

        {/* ── right ── */}
        <div className="lp-right">
          <div className="lp-right-label">Live snapshot</div>

          <div className="lp-stats">
            {[
              { name: "Total customers",  value: "12,400", cls: "" },
              { name: "Churned",          value: "1,860",  cls: "danger" },
              { name: "Retained",         value: "10,540", cls: "safe" },
              { name: "Churn rate",       value: "15.0%",  cls: "danger" },
              { name: "High risk",        value: "634",    cls: "danger" },
            ].map((s) => (
              <div key={s.name} className="lp-stat-row">
                <span className="lp-stat-name">{s.name}</span>
                <span className={`lp-stat-val ${s.cls}`}>{s.value}</span>
              </div>
            ))}
          </div>

          <div className="lp-right-foot">
            <span className="lp-badge">● model live</span>
            {/* <span className="lp-right-note">scores update per page load</span> */}
          </div>
        </div>
      </div>
    </>
  );
}