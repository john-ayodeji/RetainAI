"use client";

import { useEffect, useMemo, useState } from "react";
import StatCards from "@/app/components/StatCards";
import FilterBar from "@/app/components/FilterBar";
import CustomerTable from "@/app/components/CustomerTable";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://silver-space-giggle-4jj4ppj994wwc5q66-8000.app.github.dev/api";

function normalizeCustomers(payload: unknown): any[] {
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === "object") {
    const p = payload as Record<string, unknown>;
    if (Array.isArray(p.data)) return p.data as any[];
    if (Array.isArray(p.records)) return p.records as any[];
  }
  return [];
}

export default function DashboardPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    gender: "All",
    subscription: "All",
    contract: "All",
    churn: "All",
    query: "",
  });

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    async function loadCustomers() {
      try {
        const firstRes = await fetch(`${API_BASE}/filter/users?page=1&limit=100`);
        const firstData = await firstRes.json();
        const firstPage = normalizeCustomers(firstData);
        const totalPages = Number(firstData?.total_pages || 1);

        if (!mounted) return;
        if (totalPages <= 1) { setCustomers(firstPage); return; }

        const rest = await Promise.all(
          Array.from({ length: totalPages - 1 }, (_, i) =>
            fetch(`${API_BASE}/filter/users?page=${i + 2}&limit=100`).then((r) => r.json())
          )
        );

        if (!mounted) return;
        setCustomers([...firstPage, ...rest.flatMap(normalizeCustomers)]);
      } catch (err) {
        if (mounted) setError(String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadCustomers();
    return () => { mounted = false; };
  }, []);

  const filtered = useMemo(() => {
    const q = filters.query.toLowerCase();
    return customers.filter((c) => {
      const gender = String(c.Gender || c.gender || "");
      const subscription = String(c["Subscription Type"] || c.subscription || c.Plan || "");
      const contract = String(c["Contract Length"] || c.contract || c.Contract || "");
      const churn = String(c.Churn ?? c.churn ?? "");

      if (filters.gender !== "All" && gender !== filters.gender) return false;
      if (filters.subscription !== "All" && subscription !== filters.subscription) return false;
      if (filters.contract !== "All" && contract !== filters.contract) return false;
      if (filters.churn !== "All") {
        if (churn !== (filters.churn === "Churned" ? "1" : "0")) return false;
      }
      if (q) {
        const cid = String(c.CustomerID || c.customer_id || c.id || "").toLowerCase();
        const email = (c.email || c.Email || "").toLowerCase();
        const tags = [gender, subscription, contract].join(" ").toLowerCase();
        if (!cid.includes(q) && !email.includes(q) && !tags.includes(q)) return false;
      }
      return true;
    });
  }, [customers, filters]);

  const totalChurned = filtered.filter(
    (c) => String(c.Churn ?? c.churn ?? "") === "1"
  ).length;
  const churnRate = filtered.length === 0 ? 0 : (totalChurned / filtered.length) * 100;

  return (
    <>
      <style>{`
        /* ── shell ── */
        .db-shell {
          font-family: 'DM Mono', ui-monospace, monospace;
          min-height: 100vh;
          background: #f8f7f4;
          color: #1a1916;
          font-size: 13px;
          box-sizing: border-box;
        }
        .db-shell * { box-sizing: border-box; }

        /* ── topbar ── */
        .db-topbar {
          position: fixed;
          top: 0; left: 0; right: 0;
          height: 52px;
          background: #fff;
          border-bottom: 0.5px solid rgba(0,0,0,.09);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 28px;
          z-index: 50;
        }
        .db-wordmark {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 18px;
          font-weight: 600;
          letter-spacing: -.02em;
          color: #1a1916;
        }
        .db-topbar-right {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .18em;
          color: #a09d96;
        }

        /* ── page body ── */
        .db-body {
          padding: 72px 28px 40px;
          max-width: 1200px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        /* ── section label ── */
        .db-section-label {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .2em;
          color: #a09d96;
          margin-bottom: 8px;
        }

        /* ── loading / error ── */
        .db-status {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 11px;
          color: #a09d96;
          padding: 4px 0;
        }
        .db-dot {
          width: 5px; height: 5px;
          border-radius: 50%;
          background: #a09d96;
          animation: dbpulse 1.1s ease-in-out infinite;
        }
        .db-dot:nth-child(2) { animation-delay: .18s; }
        .db-dot:nth-child(3) { animation-delay: .36s; }
        @keyframes dbpulse { 0%,100%{opacity:.25} 50%{opacity:1} }

        .db-error {
          padding: 10px 14px;
          border-radius: 8px;
          background: #fcebeb;
          border: 0.5px solid #f7c1c1;
          color: #791f1f;
          font-size: 11px;
        }
      `}</style>

      <div className="db-shell">
        {/* topbar */}
        <header className="db-topbar">
          <span className="db-wordmark">RetainAI</span>
          <span className="db-topbar-right">churn intelligence dashboard</span>
        </header>

        <div className="db-body">
          {/* stat cards */}
          <div>
            <div className="db-section-label">overview</div>
            <StatCards
              customers={filtered}
              totalCount={customers.length}
              churnedCount={totalChurned}
              churnRate={churnRate}
            />
          </div>

          {/* filter bar */}
          <div>
            <div className="db-section-label">filters</div>
            <FilterBar
              filters={filters}
              setFilters={setFilters}
              total={customers.length}
              shown={filtered.length}
            />
          </div>

          {/* table */}
          <div>
            <div className="db-section-label">
              {loading ? (
                <span className="db-status">
                  <span className="db-dot" />
                  <span className="db-dot" />
                  <span className="db-dot" />
                  loading customers
                </span>
              ) : error ? null : (
                `${filtered.length} customers · ${totalChurned} churned`
              )}
            </div>

            {error ? (
              <div className="db-error">Failed to load customers: {error}</div>
            ) : (
              <CustomerTable customers={filtered} loading={loading} error={error} />
            )}
          </div>
        </div>
      </div>
    </>
  );
}