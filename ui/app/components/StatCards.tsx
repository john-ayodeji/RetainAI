import React from "react";

function countChurned(list: any[]) {
  return list.filter((row) => String(row.Churn ?? row.churn ?? "") === "1").length;
}

export default function StatCards({
  customers,
  totalCount,
  churnedCount,
  churnRate,
}: {
  customers: any[];
  totalCount: number;
  churnedCount: number;
  churnRate?: number;
}) {
  const churned = typeof churnedCount === "number" ? churnedCount : countChurned(customers);
  const retained = Math.max(totalCount - churned, 0);
  const rate =
    typeof churnRate === "number"
      ? churnRate
      : totalCount === 0
      ? 0
      : (churned / totalCount) * 100;

  const cards = [
    {
      value: totalCount.toLocaleString(),
      label: "Total customers",
      color: "neutral",
    },
    {
      value: churned.toLocaleString(),
      label: "Churned customers",
      color: "danger",
    },
    {
      value: retained.toLocaleString(),
      label: "Retained customers",
      color: "safe",
    },
    {
      value: `${rate.toFixed(1)}%`,
      label: "Overall churn rate",
      color: rate >= 40 ? "danger" : rate >= 20 ? "warn" : "safe",
    },
  ];

  return (
    <>
      <style>{`
        .sc-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          font-family: 'DM Mono', ui-monospace, monospace;
        }
        @media (max-width: 720px) { .sc-grid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 420px) { .sc-grid { grid-template-columns: 1fr; } }

        .sc-card {
          background: #fff;
          border: 0.5px solid rgba(0,0,0,.09);
          border-radius: 12px;
          padding: 14px 16px 16px;
        }
        .sc-value {
          font-family: 'Fraunces', Georgia, serif;
          font-size: 30px;
          font-weight: 600;
          letter-spacing: -.025em;
          line-height: 1;
          color: #1a1916;
        }
        .sc-value.danger { color: #a32d2d; }
        .sc-value.safe   { color: #3b6d11; }
        .sc-value.warn   { color: #854f0b; }
        .sc-label {
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .18em;
          color: #a09d96;
          margin-top: 8px;
        }
      `}</style>

      <div className="sc-grid">
        {cards.map((card) => (
          <div key={card.label} className="sc-card">
            <div className={`sc-value ${card.color !== "neutral" ? card.color : ""}`}>
              {card.value}
            </div>
            <div className="sc-label">{card.label}</div>
          </div>
        ))}
      </div>
    </>
  );
}