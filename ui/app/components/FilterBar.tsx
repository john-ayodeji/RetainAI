"use client";

interface Filters {
  gender: string;
  subscription: string;
  contract: string;
  churn: string;
  query: string;
}

interface FilterBarProps {
  filters: Filters;
  setFilters: (f: Filters) => void;
  total: number;
  shown: number;
}

const GENDER_OPTIONS       = ["All", "Male", "Female"];
const SUBSCRIPTION_OPTIONS = ["All", "Basic", "Standard", "Premium"];
const CONTRACT_OPTIONS     = ["All", "Monthly", "Quarterly", "Annual"];
const CHURN_OPTIONS        = ["All", "Churned", "Retained"];

export default function FilterBar({ filters, setFilters, total, shown }: FilterBarProps) {
  function set(key: keyof Filters, value: string) {
    setFilters({ ...filters, [key]: value });
  }

  const selects: { key: keyof Filters; label: string; options: string[] }[] = [
    { key: "gender",       label: "gender",       options: GENDER_OPTIONS },
    { key: "subscription", label: "subscription", options: SUBSCRIPTION_OPTIONS },
    { key: "contract",     label: "contract",     options: CONTRACT_OPTIONS },
    { key: "churn",        label: "status",       options: CHURN_OPTIONS },
  ];

  const hasActiveFilter =
    filters.gender !== "All" ||
    filters.subscription !== "All" ||
    filters.contract !== "All" ||
    filters.churn !== "All" ||
    filters.query !== "";

  return (
    <>
      <style>{`
        .fb-wrap {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
          font-family: 'DM Mono', ui-monospace, monospace;
          font-size: 12px;
        }
        .fb-search {
          font-family: 'DM Mono', monospace;
          font-size: 12px;
          padding: 7px 12px;
          border: 0.5px solid rgba(0,0,0,.16);
          border-radius: 7px;
          background: #fff;
          color: #1a1916;
          outline: none;
          width: 200px;
          transition: border-color .15s;
        }
        .fb-search::placeholder { color: #a09d96; }
        .fb-search:focus { border-color: #1a1916; }

        .fb-select {
          font-family: 'DM Mono', monospace;
          font-size: 11px;
          padding: 6px 10px;
          border: 0.5px solid rgba(0,0,0,.16);
          border-radius: 7px;
          background: #fff;
          color: #6e6b64;
          outline: none;
          cursor: pointer;
          appearance: none;
          padding-right: 22px;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='none'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23a09d96' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 8px center;
          transition: border-color .15s;
        }
        .fb-select:focus { border-color: #1a1916; color: #1a1916; }
        .fb-select.active { border-color: #1a1916; color: #1a1916; background-color: #f8f7f4; }

        .fb-clear {
          font-family: 'DM Mono', monospace;
          font-size: 11px;
          padding: 6px 11px;
          border: 0.5px solid rgba(0,0,0,.16);
          border-radius: 7px;
          background: transparent;
          color: #6e6b64;
          cursor: pointer;
          transition: all .15s;
        }
        .fb-clear:hover { background: #1a1916; color: #fff; border-color: #1a1916; }

        .fb-count {
          margin-left: auto;
          font-size: 10px;
          color: #a09d96;
          white-space: nowrap;
        }
      `}</style>

      <div className="fb-wrap">

        {selects.map(({ key, label, options }) => (
          <select
            key={key}
            className={`fb-select ${filters[key] !== "All" ? "active" : ""}`}
            value={filters[key]}
            onChange={(e) => set(key, e.target.value)}
          >
            {options.map((o) => (
              <option key={o} value={o}>
                {o === "All" ? `all ${label}` : o.toLowerCase()}
              </option>
            ))}
          </select>
        ))}

        {hasActiveFilter && (
          <button
            className="fb-clear"
            onClick={() =>
              setFilters({ gender: "All", subscription: "All", contract: "All", churn: "All", query: "" })
            }
          >
            clear ×
          </button>
        )}

        <span className="fb-count">
          {shown.toLocaleString()} / {total.toLocaleString()}
        </span>
      </div>
    </>
  );
}