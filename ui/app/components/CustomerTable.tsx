"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://retain-ai-alpha.vercel.app/api";

function getCustomerId(row: any) {
  return row.CustomerID ?? row.CustomerId ?? row.customer_id ?? row.customerID ?? row.id ?? row.email ?? "";
}
function getCustomerLabel(row: any) {
  const customerId = getCustomerId(row);
  return customerId ? `Customer #${customerId}` : "Customer";
}
function getProbability(row: any) {
  return Number(row.predicted_churn_probability ?? row.churn_probability ?? row.churn_prob ?? 0);
}
function riskFromProbability(probability: number) {
  if (probability >= 0.7) return "High";
  if (probability >= 0.4 && probability < 0.7) return "Medium";
  return "Low";
}
function formatProbability(probability: number) {
  return `${(probability * 100).toFixed(1)}%`;
}
function buildPredictPayload(row: any) {
  const payload = { ...row };
  delete payload.predicted_churn_probability;
  delete payload.churn_probability;
  delete payload.churn_prob;
  return payload;
}

export default function CustomerTable({ customers, loading, error }: any) {
  const [page, setPage] = useState(1);
  const [sortDesc, setSortDesc] = useState(true);
  const [predictedRows, setPredictedRows] = useState<any[]>([]);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const perPage = 10;

  useEffect(() => { setPage(1); }, [customers]);

  const totalPages = Math.max(1, Math.ceil(customers.length / perPage));

  useEffect(() => {
    let active = true;
    const pageRows = customers.slice((page - 1) * perPage, page * perPage);

    if (pageRows.length === 0) { setPredictedRows([]); return; }

    setPredictionLoading(true);
    setPredictionError(null);

    Promise.all(
      pageRows.map(async (row: any) => {
        try {
          const response = await fetch(`${API_BASE}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ features: buildPredictPayload(row) }),
          });
          const data = await response.json();
          return { ...row, predicted_churn_probability: Number(data?.churn_probability ?? 0) };
        } catch {
          return { ...row, predicted_churn_probability: 0 };
        }
      })
    )
      .then((rows) => {
        if (!active) return;
        rows.sort((a, b) => {
          const aProb = getProbability(a);
          const bProb = getProbability(b);
          return sortDesc ? bProb - aProb : aProb - bProb;
        });
        setPredictedRows(rows);
      })
      .catch((err) => { if (active) setPredictionError(String(err)); })
      .finally(() => { if (active) setPredictionLoading(false); });

    return () => { active = false; };
  }, [customers, page, sortDesc]);

  const displayRows = useMemo(() => predictedRows, [predictedRows]);

  const paginationItems = useMemo(() => {
    const items: Array<number | string> = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) items.push(i);
    } else {
      items.push(1);
      let start = Math.max(2, page - 1);
      let end = Math.min(totalPages - 1, page + 1);
      if (start > 2) items.push("...");
      for (let i = start; i <= end; i++) items.push(i);
      if (end < totalPages - 1) items.push("...");
      items.push(totalPages);
    }
    return items;
  }, [page, totalPages]);

  if (loading) return (
    <div className="ct-card">
      <div className="ct-loading-full">
        <span className="ct-dot" /><span className="ct-dot" /><span className="ct-dot" />
        <span>loading customers</span>
      </div>
    </div>
  );

  if (error) return (
    <div className="ct-card">
      <div className="ct-error-box">Error: {error}</div>
    </div>
  );

  if (predictionError) return (
    <div className="ct-card">
      <div className="ct-error-box">Prediction error: {predictionError}</div>
    </div>
  );

  return (
    <>
      <style>{`
        .ct-card {
          background: #fff;
          border: 0.5px solid rgba(0,0,0,.09);
          border-radius: 14px;
          overflow: hidden;
          font-family: 'DM Mono', ui-monospace, monospace;
          font-size: 12px;
          color: #1a1916;
        }

        /* head */
        .ct-head {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          padding: 14px 18px;
          border-bottom: 0.5px solid rgba(0,0,0,.09);
        }
        .ct-head-title {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 16px;
          font-weight: 600;
          letter-spacing: -.01em;
          color: #1a1916;
        }
        .ct-head-sub {
          font-size: 10px;
          color: #a09d96;
          margin-top: 3px;
        }
        .ct-sort-btn {
          font-family: 'DM Mono', monospace;
          font-size: 10px;
          padding: 5px 11px;
          border: 0.5px solid rgba(0,0,0,.16);
          border-radius: 50px;
          background: transparent;
          color: #6e6b64;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          transition: all .15s;
          white-space: nowrap;
        }
        .ct-sort-btn:hover { background: #1a1916; color: #fff; border-color: #1a1916; }

        /* table */
        .ct-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; }

        .ct-th {
          padding: 9px 14px;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .14em;
          color: #a09d96;
          font-weight: 400;
          white-space: nowrap;
          border-bottom: 0.5px solid rgba(0,0,0,.09);
          background: #f8f7f4;
        }
        .ct-th-sort {
          cursor: pointer;
        }
        .ct-th-sort:hover { color: #1a1916; }

        .ct-td {
          padding: 11px 14px;
          border-bottom: 0.5px solid rgba(0,0,0,.06);
          vertical-align: middle;
          color: #6e6b64;
        }
        .ct-tr:last-child .ct-td { border-bottom: none; }
        .ct-tr:hover .ct-td { background: #f8f7f4; }

        /* avatar */
        .ct-avatar {
          width: 30px; height: 30px;
          border-radius: 50%;
          background: #e6f1fb;
          border: 0.5px solid #b5d4f4;
          display: flex; align-items: center; justify-content: center;
          font-size: 10px; font-weight: 500;
          color: #185fa5;
          flex-shrink: 0;
        }
        .ct-customer-name { font-size: 12px; font-weight: 500; color: #1a1916; }
        .ct-customer-sub  { font-size: 10px; color: #a09d96; margin-top: 2px; }

        /* prob */
        .ct-prob { font-size: 13px; font-weight: 500; color: #1a1916; }

        /* risk badge */
        .ct-badge {
          font-size: 10px; font-weight: 500;
          padding: 3px 9px;
          border-radius: 50px;
          border: 0.5px solid;
          white-space: nowrap;
          letter-spacing: .04em;
        }
        .ct-badge-high { background: #fcebeb; color: #791f1f; border-color: #f7c1c1; }
        .ct-badge-med  { background: #faeeda; color: #633806; border-color: #fac775; }
        .ct-badge-low  { background: #eaf3de; color: #27500a; border-color: #c0dd97; }

        /* action link */
        .ct-action {
          font-size: 11px;
          color: #185fa5;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          border: 0.5px solid #b5d4f4;
          border-radius: 50px;
          background: #e6f1fb;
          transition: all .15s;
          white-space: nowrap;
        }
        .ct-action:hover { background: #185fa5; color: #fff; border-color: #185fa5; }

        /* scoring state */
        .ct-scoring {
          padding: 20px 14px;
          font-size: 11px;
          color: #a09d96;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        /* loading / error full */
        .ct-loading-full {
          display: flex; align-items: center; gap: 5px;
          padding: 24px 18px;
          font-size: 11px; color: #a09d96;
        }
        .ct-error-box {
          padding: 14px 18px;
          font-size: 11px; color: #791f1f;
          background: #fcebeb;
          border-radius: 8px;
          margin: 12px;
          border: 0.5px solid #f7c1c1;
        }

        /* dots */
        .ct-dot {
          width: 5px; height: 5px; border-radius: 50%;
          background: #a09d96;
          animation: ctpulse 1.1s ease-in-out infinite;
          flex-shrink: 0;
        }
        .ct-dot:nth-child(2) { animation-delay: .18s; }
        .ct-dot:nth-child(3) { animation-delay: .36s; }
        @keyframes ctpulse { 0%,100%{opacity:.25} 50%{opacity:1} }

        /* pagination */
        .ct-pagination {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
          padding: 12px 18px;
          border-top: 0.5px solid rgba(0,0,0,.09);
        }
        .ct-pg-btn {
          font-family: 'DM Mono', monospace;
          font-size: 11px;
          padding: 5px 11px;
          border: 0.5px solid rgba(0,0,0,.16);
          border-radius: 7px;
          background: transparent;
          color: #6e6b64;
          cursor: pointer;
          min-width: 32px;
          text-align: center;
          transition: all .15s;
        }
        .ct-pg-btn:hover:not(:disabled) { background: #1a1916; color: #fff; border-color: #1a1916; }
        .ct-pg-btn:disabled { opacity: .35; cursor: not-allowed; }
        .ct-pg-btn.active { background: #1a1916; color: #fff; border-color: #1a1916; }
        .ct-pg-ellipsis { font-size: 11px; color: #a09d96; padding: 0 3px; user-select: none; }
      `}</style>

      <div className="ct-card">
        {/* head */}
        <div className="ct-head">
          <div>
            <div className="ct-head-title">All customers</div>
            <div className="ct-head-sub">
              The first 10 visible users are scored with /api/predict before rendering.
            </div>
          </div>
          <div style={{ fontSize: 10, color: "#a09d96", textAlign: "right", display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
            <button className="ct-sort-btn" onClick={() => setSortDesc((v) => !v)}>
              predicted churn {sortDesc ? "↓" : "↑"}
            </button>
          </div>
        </div>

        {/* table */}
        <table className="ct-table">
          <thead>
            <tr>
              <th className="ct-th">Customer</th>
              <th className="ct-th">Gender</th>
              <th className="ct-th">Subscription</th>
              <th className="ct-th">Contract</th>
              <th className="ct-th">Tenure</th>
              <th className="ct-th ct-th-sort" onClick={() => setSortDesc((v) => !v)}>
                Predicted churn {sortDesc ? "↓" : "↑"}
              </th>
              <th className="ct-th">Risk</th>
              <th className="ct-th">Action</th>
            </tr>
          </thead>
          <tbody>
            {predictionLoading ? (
              <tr>
                <td colSpan={8} className="ct-td">
                  <div className="ct-scoring">
                    <span className="ct-dot" />
                    <span className="ct-dot" />
                    <span className="ct-dot" />
                    calculating churn scores for this page…
                  </div>
                </td>
              </tr>
            ) : (
              displayRows.map((row: any) => {
                const customerId = getCustomerId(row);
                const probability = getProbability(row);
                const risk = riskFromProbability(probability);
                const linkTarget = customerId ? encodeURIComponent(String(customerId)) : "";
                const initials = String(customerId || "").slice(0, 2).toUpperCase();

                return (
                  <tr key={String(customerId || JSON.stringify(row))} className="ct-tr">
                    <td className="ct-td">
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div className="ct-avatar">{initials || "ID"}</div>
                        <div>
                          <div className="ct-customer-name">{getCustomerLabel(row)}</div>
                          <div className="ct-customer-sub">
                            Age {row.Age ?? "—"} · {row.Gender ?? "—"} · Support calls {row["Support Calls"] ?? row.support_calls ?? "—"}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="ct-td">{row.Gender ?? row.gender ?? "—"}</td>
                    <td className="ct-td">{row["Subscription Type"] ?? row.subscription ?? "—"}</td>
                    <td className="ct-td">{row["Contract Length"] ?? row.contract ?? "—"}</td>
                    <td className="ct-td">{row.Tenure != null ? `${row.Tenure} months` : "—"}</td>
                    <td className="ct-td">
                      <span className="ct-prob">{formatProbability(probability)}</span>
                    </td>
                    <td className="ct-td">
                      <span className={`ct-badge ${
                        risk === "High" ? "ct-badge-high" :
                        risk === "Medium" ? "ct-badge-med" :
                        "ct-badge-low"
                      }`}>
                        {risk}
                      </span>
                    </td>
                    <td className="ct-td">
                      <Link href={`/customers/${linkTarget}`} className="ct-action">
                        Analyse →
                      </Link>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* pagination */}
        <div className="ct-pagination">
          <button
            className="ct-pg-btn"
            onClick={() => setPage((v) => Math.max(1, v - 1))}
            disabled={page === 1}
          >
            Previous
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {paginationItems.map((p, idx) =>
              p === "..." ? (
                <span key={`ell-${idx}`} className="ct-pg-ellipsis">…</span>
              ) : (
                <button
                  key={`pg-${p}`}
                  className={`ct-pg-btn ${p === page ? "active" : ""}`}
                  onClick={() => setPage(Number(p))}
                >
                  {p}
                </button>
              )
            )}
          </div>

          <button
            className="ct-pg-btn"
            onClick={() => setPage((v) => Math.min(totalPages, v + 1))}
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      </div>
    </>
  );
}