"use client";
import Link from "next/link";
import React, { useEffect, useRef, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://retain-ai-alpha.vercel.app/api";

// ─── tiny syntax highlighter ────────────────────────────────────────────────
function JsonHighlight({ data }: { data: object }) {
  const lines = JSON.stringify(data, null, 2).split("\n");
  return (
    <pre className="json-pre">
      {lines.map((line, i) => {
        const highlighted = line
          .replace(
            /("[\w\s]+")\s*:/g,
            '<span class="jk">$1</span>:'
          )
          .replace(
            /:\s*(".*?")/g,
            (_, s) => `: <span class="js">${s}</span>`
          )
          .replace(
            /:\s*(\d+\.?\d*)/g,
            (_, n) => `: <span class="jn">${n}</span>`
          )
          .replace(
            /:\s*(true|false|null)/g,
            (_, b) => `: <span class="jb">${b}</span>`
          );
        return (
          <span
            key={i}
            dangerouslySetInnerHTML={{ __html: highlighted + "\n" }}
          />
        );
      })}
    </pre>
  );
}

// ─── types ───────────────────────────────────────────────────────────────────
interface Message {
  role: "user" | "assistant";
  text: string;
  thinking?: boolean;
}

// ─── component ───────────────────────────────────────────────────────────────
export default function CustomerDetail({ params }: any) {
  // unwrap the params promise before reading route values
  const routeParams: any = (React as any).use(params);
  const id = routeParams?.id ?? "";

  const [customer, setCustomer] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [fetchDebug, setFetchDebug] = useState<any>(null);
  const [manualId, setManualId] = useState("");
  const [manualJson, setManualJson] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // scroll chat to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // initial load
  useEffect(() => {
    let mounted = true;
    try {
      if (typeof window !== "undefined") {
        const sess = sessionStorage.getItem("selectedCustomer");
        if (sess) {
          const parsed = JSON.parse(sess);
          const pid = parsed?.CustomerID ?? parsed?.customer_id ?? parsed?.id;
          if (String(pid) === String(id)) {
            if (mounted) setCustomer(parsed);
            sessionStorage.removeItem("selectedCustomer");
            setLoading(false);
            return;
          }
        }
      }
    } catch (_) {}

    fetchById(id, mounted);
    return () => { mounted = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  function fetchById(fetchId: string, mounted = true) {
    setLoading(true);
    setFetchError(null);
    const url = `${API_BASE}/customers/${encodeURIComponent(String(fetchId))}`;
    fetch(url)
      .then(async (r) => {
        const text = await r.text();
        let body: any = text;
        try { body = JSON.parse(text); } catch (_) {}
        setFetchDebug({ url, status: r.status, body });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return body;
      })
      .then((payload) => { if (mounted) setCustomer(payload?.data ?? null); })
      .catch((e) => { if (mounted) setFetchError(String(e)); })
      .finally(() => { if (mounted) setLoading(false); });
  }

  function applyManualJson() {
    try {
      setCustomer(JSON.parse(manualJson));
      setManualJson("");
      setFetchError(null);
    } catch (_) {
      setFetchError("Invalid JSON");
    }
  }

  function sendExplain(question: string) {
    if (!customer) {
      setMessages((m) => [...m, { role: "assistant", text: "No customer data loaded." }]);
      return;
    }
    setMessages((m) => [
      ...m,
      { role: "user", text: question },
      { role: "assistant", text: "Thinking…", thinking: true },
    ]);
    const cid = customer.CustomerID ?? customer.customer_id ?? customer.id ?? id;
    fetch(`${API_BASE}/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, customer, customer_meta: { CustomerID: cid } }),
    })
      .then((r) => r.json())
      .then((d) =>
        setMessages((m) => [
          ...m.filter((x) => !x.thinking),
          { role: "assistant", text: d.answer ?? JSON.stringify(d) },
        ])
      )
      .catch((e) =>
        setMessages((m) => [
          ...m.filter((x) => !x.thinking),
          { role: "assistant", text: `Error: ${String(e)}` },
        ])
      );
  }

  // ─── derived ──────────────────────────────────────────────────────────────
  const cid =
    customer?.CustomerID ?? customer?.CustomerId ?? customer?.customer_id ?? customer?.id ?? id;
  const isChurn = String(customer?.Churn ?? customer?.churn ?? "") === "1";
  const status = customer ? (isChurn ? "At risk" : "Stable") : "Pending";
  const tenure = customer?.Tenure ?? customer?.tenure;
  const contract = customer?.["Contract Length"] ?? customer?.contract;
  const sub = customer?.["Subscription Type"] ?? customer?.subscription;
  const gender = customer?.Gender ?? customer?.gender;

  const tags = [gender, sub, contract, tenure ? `Tenure ${tenure}mo` : null, `Churn: ${isChurn ? "Yes" : "No"}`].filter(Boolean) as string[];
  const stats = [
    // { label: "Churn risk", value: isChurn ? "High" : "Low", danger: isChurn },
    { label: "Tenure", value: tenure ? `${tenure} mo` : "—" },
    { label: "Contract", value: contract ?? "—" },
    { label: "Subscription", value: sub ?? "—" },
  ];

  const presets = [
    "What's the single biggest retention lever for this customer?",
    "Draft a personalized win-back message for this customer",
    "What's the risk if we do nothing this month?"
  ];

  // ─── render ───────────────────────────────────────────────────────────────
  return (
    <>
      <style>{`
        /* ── base ── */
        .cd-shell{font-family:'DM Mono',ui-monospace,monospace;min-height:100vh;background:#f8f7f4;color:#1a1916;font-size:13px;line-height:1.5;padding:20px;box-sizing:border-box}
        .cd-shell *{box-sizing:border-box}

        /* ── topbar ── */
        .cd-topbar{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#fff;border:0.5px solid rgba(0,0,0,.09);border-radius:10px;margin-bottom:16px}
        .cd-back{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-family:inherit;color:#6e6b64;padding:5px 12px;border:0.5px solid rgba(0,0,0,.16);border-radius:50px;background:none;cursor:pointer;text-decoration:none;transition:all .15s}
        .cd-back:hover{color:#1a1916;border-color:#1a1916}
        .cd-topbar-label{font-size:11px;color:#a09d96;text-transform:uppercase;letter-spacing:.14em;text-align:right}

        /* ── grid ── */
        .cd-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
        @media(max-width:720px){.cd-grid{grid-template-columns:1fr}}

        /* ── card ── */
        .cd-card{background:#fff;border:0.5px solid rgba(0,0,0,.09);border-radius:14px;overflow:hidden}
        .cd-card-head{padding:16px 18px 14px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-label{font-size:10px;text-transform:uppercase;letter-spacing:.2em;color:#a09d96;margin-bottom:6px}
        .cd-title-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
        .cd-title{font-family:'Fraunces',Georgia,serif;font-size:26px;font-weight:600;letter-spacing:-.02em;display:flex;align-items:center;gap:10px}

        /* ── badge ── */
        .cd-badge{font-family:'DM Mono',monospace;font-size:10px;font-weight:500;padding:3px 9px;border-radius:50px;letter-spacing:.08em}
        .cd-badge-risk{background:#fcebeb;color:#791f1f;border:0.5px solid #f7c1c1}
        .cd-badge-stable{background:#eaf3de;color:#27500a;border:0.5px solid #c0dd97}
        .cd-badge-pending{background:#faeeda;color:#633806;border:0.5px solid #fac775}

        /* ── tags ── */
        .cd-tags{padding:12px 18px;display:flex;flex-wrap:wrap;gap:6px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-tag{font-size:11px;padding:3px 9px;border:0.5px solid rgba(0,0,0,.16);border-radius:50px;color:#6e6b64;background:#f8f7f4}

        /* ── stats grid ── */
        .cd-stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:rgba(0,0,0,.09);border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-stat{background:#f8f7f4;padding:12px 14px}
        .cd-stat-label{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:#a09d96;margin-bottom:4px}
        .cd-stat-val{font-size:15px;font-weight:500;color:#1a1916}
        .cd-stat-val.danger{color:#a32d2d}
        .cd-stat-val.safe{color:#3b6d11}

        /* ── json ── */
        .cd-json{padding:14px 18px;overflow:auto;max-height:260px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .json-pre{font-family:'DM Mono',monospace;font-size:11px;color:#6e6b64;line-height:1.9;white-space:pre-wrap;word-break:break-word;margin:0}
        .jk{color:#185fa5}.js{color:#3b6d11}.jn{color:#854f0b}.jb{color:#993556}

        /* ── fetch row ── */
        .cd-fetch{padding:12px 18px;display:flex;gap:8px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-input{flex:1;font-family:'DM Mono',monospace;font-size:12px;padding:7px 11px;border:0.5px solid rgba(0,0,0,.16);border-radius:7px;background:#f8f7f4;color:#1a1916;outline:none}
        .cd-input:focus{border-color:#1a1916}
        .cd-btn{font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:7px 13px;border:0.5px solid rgba(0,0,0,.16);border-radius:7px;background:#1a1916;color:#fff;cursor:pointer;white-space:nowrap;transition:opacity .15s}
        .cd-btn:hover{opacity:.8}
        .cd-btn-ghost{background:transparent;color:#6e6b64}
        .cd-btn-ghost:hover{background:#f8f7f4;opacity:1;color:#1a1916}

        /* ── json paste ── */
        .cd-paste{padding:14px 18px}
        .cd-textarea{width:100%;font-family:'DM Mono',monospace;font-size:11px;padding:9px 11px;border:0.5px solid rgba(0,0,0,.16);border-radius:7px;background:#f8f7f4;color:#1a1916;outline:none;resize:vertical;min-height:100px;margin-top:8px}
        .cd-textarea:focus{border-color:#1a1916}
        .cd-paste-btns{display:flex;gap:8px;margin-top:8px}

        /* ── error ── */
        .cd-error{margin:10px 18px;padding:9px 12px;border-radius:8px;background:#fcebeb;border:0.5px solid #f7c1c1;color:#791f1f;font-size:11px}

        /* ── chat card ── */
        .cd-chat{display:flex;flex-direction:column}
        .cd-chat-head{padding:16px 18px 14px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-chat-title{font-family:'Fraunces',Georgia,serif;font-size:20px;font-weight:600;letter-spacing:-.01em}
        .cd-chat-sub{font-size:11px;color:#a09d96;margin-top:3px}

        /* ── presets ── */
        .cd-presets{padding:12px 18px;display:flex;flex-direction:column;gap:6px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-preset{font-family:'DM Mono',monospace;font-size:11px;text-align:left;padding:7px 11px;border:0.5px solid rgba(0,0,0,.16);border-radius:7px;background:#f8f7f4;color:#6e6b64;cursor:pointer;display:flex;align-items:center;gap:8px;transition:all .15s}
        .cd-preset:hover{background:#1a1916;color:#fff;border-color:#1a1916}
        .cd-preset-dot{width:5px;height:5px;border-radius:50%;background:#a09d96;flex-shrink:0;transition:background .15s}
        .cd-preset:hover .cd-preset-dot{background:#fff}

        /* ── messages ── */
        .cd-messages{padding:14px 18px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;min-height:200px;max-height:300px;border-bottom:0.5px solid rgba(0,0,0,.09)}
        .cd-empty{display:flex;align-items:center;justify-content:center;flex:1;min-height:160px;font-size:11px;color:#a09d96;text-align:center;border:0.5px dashed rgba(0,0,0,.16);border-radius:8px;padding:20px}
        .cd-msg{max-width:92%;padding:9px 13px;font-size:12px;line-height:1.65;border-radius:9px}
        .cd-msg-user{align-self:flex-end;background:#1a1916;color:#fff}
        .cd-msg-ai{align-self:flex-start;background:#f8f7f4;border:0.5px solid rgba(0,0,0,.12);color:#1a1916}
        .cd-msg-thinking{opacity:.45;font-style:italic}

        /* ── chat input ── */
        .cd-chat-input-row{padding:12px 18px;display:flex;gap:8px}

        /* ── loading ── */
        .cd-loading{display:flex;align-items:center;justify-content:center;min-height:200px;gap:4px}
        .cd-dot{width:5px;height:5px;border-radius:50%;background:#a09d96;animation:cdpulse 1.1s ease-in-out infinite}
        .cd-dot:nth-child(2){animation-delay:.18s}
        .cd-dot:nth-child(3){animation-delay:.36s}
        @keyframes cdpulse{0%,100%{opacity:.25}50%{opacity:1}}

        /* ── reload btn ── */
        .cd-reload{font-family:'DM Mono',monospace;font-size:11px;padding:5px 11px;border:0.5px solid rgba(0,0,0,.16);border-radius:7px;background:transparent;color:#6e6b64;cursor:pointer;transition:all .15s}
        .cd-reload:hover{background:#1a1916;color:#fff;border-color:#1a1916}
      `}</style>

      <div className="cd-shell">
        {/* topbar */}
        <div className="cd-topbar">
          <Link href="/dashboard" className="cd-back">
            ← dashboard
          </Link>
          <div className="cd-topbar-label">customer detail / inspect &amp; explain</div>
        </div>

        <div className="cd-grid">
          {/* ── left: customer record ── */}
          <div className="cd-card">
            <div className="cd-card-head">
              <div className="cd-label">Customer record</div>
              <div className="cd-title-row">
                <div className="cd-title">
                  #{cid}
                  <span
                    className={`cd-badge ${
                      status === "At risk"
                        ? "cd-badge-risk"
                        : status === "Stable"
                        ? "cd-badge-stable"
                        : "cd-badge-pending"
                    }`}
                  >
                    {status}
                  </span>
                </div>
                <button className="cd-reload" onClick={() => fetchById(String(id))}>
                  ↻ reload
                </button>
              </div>
            </div>

            {/* tags */}
            {/* <div className="cd-tags">
              <span className="cd-tag">#{cid}</span>
              {tags.map((t) => (
                <span key={t} className="cd-tag">{t}</span>
              ))}
            </div> */}

            {/* stats */}
            {customer && (
              <div className="cd-stats">
                {stats.map((s) => (
                  <div key={s.label} className="cd-stat">
                    <div className="cd-stat-label">{s.label}</div>
                    <div className={`cd-stat-val`}>
                      {s.value}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* json / loading / empty */}
            {loading ? (
              <div className="cd-loading">
                <span className="cd-dot" />
                <span className="cd-dot" />
                <span className="cd-dot" />
              </div>
            ) : customer ? (
              <div className="cd-json">
                {/* <div className="cd-label" style={{ marginBottom: 8 }}>Raw record</div> */}
                {/* <JsonHighlight data={customer} /> */}
              </div>
            ) : (
              <div style={{ padding: "14px 18px", fontSize: 12, color: "#6e6b64" }}>
                No record found for this ID.
              </div>
            )}

            {/* errors */}
            {fetchError && <div className="cd-error">Error: {fetchError}</div>}

            {/* manual fetch */}
            {/* <div className="cd-fetch">
              <input
                className="cd-input"
                value={manualId}
                onChange={(e) => setManualId(e.target.value)}
                placeholder="fetch by customer id…"
                onKeyDown={(e) => e.key === "Enter" && fetchById(manualId)}
              />
              <button className="cd-btn" onClick={() => fetchById(manualId)}>
                fetch
              </button>
            </div> */}

            {/* paste json */}
            {/* <div className="cd-paste">
              <div className="cd-label">Or paste customer JSON</div>
              <textarea
                className="cd-textarea"
                value={manualJson}
                onChange={(e) => setManualJson(e.target.value)}
                placeholder='{ "CustomerID": 123, ... }'
              />
              <div className="cd-paste-btns">
                <button className="cd-btn" onClick={applyManualJson}>apply</button>
                <button
                  className="cd-btn cd-btn-ghost"
                  onClick={() => { setManualJson(""); setFetchError(null); }}
                >
                  clear
                </button>
              </div>
            </div> */}

            {/* debug */}
            {fetchDebug && !customer && (
              <div style={{ padding: "0 18px 14px" }}>
                <div className="cd-label" style={{ marginBottom: 6 }}>Request debug</div>
                <pre
                  style={{
                    fontSize: 10,
                    background: "#f8f7f4",
                    border: "0.5px solid rgba(0,0,0,.09)",
                    borderRadius: 7,
                    padding: "10px 12px",
                    maxHeight: 120,
                    overflow: "auto",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    color: "#6e6b64",
                  }}
                >
                  {`URL: ${fetchDebug.url}\nStatus: ${fetchDebug.status}\n\n${typeof fetchDebug.body === "string" ? fetchDebug.body : JSON.stringify(fetchDebug.body, null, 2)}`}
                </pre>
              </div>
            )}
          </div>

          {/* ── right: chat ── */}
          <div className="cd-card cd-chat">
            <div className="cd-chat-head">
              <div className="cd-label">AI assistant</div>
              <div className="cd-chat-title">Ask the model</div>
              <div className="cd-chat-sub">Churn analysis &amp; retention guidance</div>
            </div>

            <div className="cd-presets">
              {presets.map((q) => (
                <button key={q} className="cd-preset" onClick={() => sendExplain(q)}>
                  <span className="cd-preset-dot" />
                  {q}
                </button>
              ))}
            </div>

            <div className="cd-messages">
              {messages.length === 0 ? (
                <div className="cd-empty">
                  No messages yet. Pick a preset or type below.
                </div>
              ) : (
                messages.map((m, i) => (
                  <div
                    key={i}
                    className={`cd-msg ${
                      m.role === "user" ? "cd-msg-user" : "cd-msg-ai"
                    } ${m.thinking ? "cd-msg-thinking" : ""}`}
                  >
                    {m.text}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="cd-chat-input-row">
              <input
                className="cd-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="ask something about this customer…"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && input.trim()) {
                    sendExplain(input.trim());
                    setInput("");
                  }
                }}
              />
              <button
                className="cd-btn"
                onClick={() => {
                  if (input.trim()) { sendExplain(input.trim()); setInput(""); }
                }}
              >
                ask
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}