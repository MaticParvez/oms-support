import { useEffect, useState } from "react";

const API = "/api";

interface Ticket {
  id: string;
  subject: string;
  status: string;
  priority: string;
  tier: string;
  audience: string;
  intent: string;
  email: string;
  sla_breached: boolean;
  sla_deadline: string | null;
  created_at: string;
  ai_confidence: number | null;
  escalation_reason: string | null;
  assigned_to: string | null;
}

const PRIORITY_COLOR: Record<string, string> = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#EAB308",
  low: "#22C55E",
};

const TIER_BADGE: Record<string, string> = {
  tier0: "#7B3FE4",
  L1: "#3B82F6",
  L2: "#F97316",
  L3: "#EF4444",
};

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState({ status: "", tier: "", priority: "" });
  const [selected, setSelected] = useState<Ticket | null>(null);

  const fetch_tickets = () => {
    const params = new URLSearchParams();
    if (filter.status) params.set("status", filter.status);
    if (filter.tier) params.set("tier", filter.tier);
    if (filter.priority) params.set("priority", filter.priority);
    params.set("limit", "50");

    fetch(`${API}/tickets?${params}`)
      .then((r) => r.json())
      .then((d) => { setTickets(d.tickets); setTotal(d.total); });
  };

  useEffect(() => { fetch_tickets(); }, [filter]);

  const escalate = async (id: string) => {
    const reason = prompt("Escalation reason:");
    if (!reason) return;
    await fetch(`${API}/tickets/${id}/escalate?reason=${encodeURIComponent(reason)}`, { method: "POST" });
    fetch_tickets();
  };

  const assign = async (id: string) => {
    const to = prompt("Assign to (email/name):");
    if (!to) return;
    await fetch(`${API}/tickets/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assigned_to: to }),
    });
    fetch_tickets();
  };

  const resolve = async (id: string) => {
    await fetch(`${API}/tickets/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "resolved" }),
    });
    fetch_tickets();
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Tickets ({total})</h2>
        <div style={{ display: "flex", gap: 12 }}>
          {(["status", "tier", "priority"] as const).map((f) => (
            <select
              key={f}
              value={filter[f]}
              onChange={(e) => setFilter((p) => ({ ...p, [f]: e.target.value }))}
              style={{ padding: "6px 12px", borderRadius: 6, border: "1px solid #E2E8F0", fontSize: 13 }}
            >
              <option value="">All {f}s</option>
              {f === "status" && ["open", "in_progress", "escalated", "resolved", "closed"].map((v) => <option key={v} value={v}>{v}</option>)}
              {f === "tier" && ["tier0", "L1", "L2", "L3"].map((v) => <option key={v} value={v}>{v}</option>)}
              {f === "priority" && ["critical", "high", "medium", "low"].map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          ))}
        </div>
      </div>

      <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 4px rgba(0,0,0,0.08)", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#F8FAFC", borderBottom: "1px solid #E2E8F0" }}>
              {["Subject", "Status", "Priority", "Tier", "Audience", "SLA", "Assigned", "Actions"].map((h) => (
                <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontWeight: 600, color: "#64748B" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id} style={{ borderBottom: "1px solid #F1F5F9", cursor: "pointer" }}
                onClick={() => setSelected(selected?.id === t.id ? null : t)}>
                <td style={{ padding: "10px 14px", maxWidth: 240 }}>
                  <div style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.subject}</div>
                  <div style={{ color: "#94A3B8", fontSize: 11 }}>{t.id.slice(0, 8)}</div>
                </td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ background: "#F1F5F9", borderRadius: 20, padding: "2px 10px", fontSize: 12 }}>{t.status}</span>
                </td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ color: PRIORITY_COLOR[t.priority] || "#64748B", fontWeight: 600, fontSize: 12 }}>● {t.priority}</span>
                </td>
                <td style={{ padding: "10px 14px" }}>
                  <span style={{ background: TIER_BADGE[t.tier] || "#64748B", color: "#fff", borderRadius: 20, padding: "2px 10px", fontSize: 12 }}>{t.tier}</span>
                </td>
                <td style={{ padding: "10px 14px", color: "#64748B" }}>{t.audience}</td>
                <td style={{ padding: "10px 14px" }}>
                  {t.sla_breached
                    ? <span style={{ color: "#EF4444", fontWeight: 600, fontSize: 12 }}>BREACHED</span>
                    : t.sla_deadline
                    ? <span style={{ color: "#22C55E", fontSize: 12 }}>{new Date(t.sla_deadline).toLocaleString()}</span>
                    : <span style={{ color: "#94A3B8", fontSize: 12 }}>—</span>}
                </td>
                <td style={{ padding: "10px 14px", color: "#64748B" }}>{t.assigned_to || "—"}</td>
                <td style={{ padding: "10px 14px" }}>
                  <div style={{ display: "flex", gap: 6 }} onClick={(e) => e.stopPropagation()}>
                    <button onClick={() => escalate(t.id)} style={btnStyle("#F97316")}>↑ Escalate</button>
                    <button onClick={() => assign(t.id)} style={btnStyle("#3B82F6")}>Assign</button>
                    <button onClick={() => resolve(t.id)} style={btnStyle("#22C55E")}>Resolve</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div style={{ marginTop: 20, background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 12px" }}>{selected.subject}</h3>
          {selected.ai_confidence && <p style={{ fontSize: 13, color: "#64748B" }}>AI Confidence: {(selected.ai_confidence * 100).toFixed(0)}%</p>}
          {selected.escalation_reason && <p style={{ fontSize: 13, color: "#F97316" }}>Escalation reason: {selected.escalation_reason}</p>}
          <p style={{ fontSize: 13, color: "#64748B" }}>Created: {new Date(selected.created_at).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}

function btnStyle(color: string) {
  return {
    padding: "4px 10px",
    fontSize: 11,
    border: "none",
    borderRadius: 6,
    background: color + "20",
    color: color,
    cursor: "pointer",
    fontWeight: 600,
  };
}
