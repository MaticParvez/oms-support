import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from "recharts";

const API = "/api";
const COLORS = ["#7B3FE4", "#3B82F6", "#F97316", "#EF4444", "#22C55E", "#EAB308"];

export default function Analytics() {
  const [days, setDays] = useState(30);
  const [summary, setSummary] = useState<any>(null);
  const [byTier, setByTier] = useState([]);
  const [byIntent, setByIntent] = useState([]);
  const [byAudience, setByAudience] = useState([]);
  const [volume, setVolume] = useState([]);

  useEffect(() => {
    fetch(`${API}/analytics/summary?days=${days}`).then((r) => r.json()).then(setSummary);
    fetch(`${API}/analytics/by-tier?days=${days}`).then((r) => r.json()).then(setByTier);
    fetch(`${API}/analytics/by-intent?days=${days}`).then((r) => r.json()).then(setByIntent);
    fetch(`${API}/analytics/by-audience?days=${days}`).then((r) => r.json()).then(setByAudience);
    fetch(`${API}/analytics/volume?days=${days}`).then((r) => r.json()).then(setVolume);
  }, [days]);

  const metric = (label: string, value: string | number | null, color = "#1E293B") => (
    <div style={{ background: "#fff", borderRadius: 12, padding: "16px 20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", flex: 1 }}>
      <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value ?? "—"}</div>
    </div>
  );

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Analytics</h2>
        <select value={days} onChange={(e) => setDays(Number(e.target.value))}
          style={{ padding: "6px 12px", borderRadius: 6, border: "1px solid #E2E8F0", fontSize: 13 }}>
          {[7, 14, 30, 90].map((d) => <option key={d} value={d}>Last {d} days</option>)}
        </select>
      </div>

      {summary && (
        <>
          <div style={{ display: "flex", gap: 16, marginBottom: 20, flexWrap: "wrap" }}>
            {metric("Total Tickets", summary.total_tickets)}
            {metric("Resolution Rate", summary.total_tickets ? `${summary.resolution_rate_pct}%` : "—", "#22C55E")}
            {metric("AI Self-Serve Rate", summary.total_tickets ? `${summary.ai_resolution_rate_pct}%` : "—", "#7B3FE4")}
            {metric("SLA Breach Rate", summary.total_tickets ? `${summary.sla_breach_rate_pct}%` : "—", "#EF4444")}
            {metric("Avg Resolution", summary.avg_resolution_hours ? `${summary.avg_resolution_hours}h` : "—")}
            {metric("Avg CSAT", summary.avg_csat ? `${summary.avg_csat}/5` : "—", "#F97316")}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
            <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
              <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#64748B" }}>Ticket Volume</h3>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={volume}>
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#7B3FE4" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
              <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#64748B" }}>By Intent</h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={byIntent} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="intent" type="category" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#7B3FE4" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
              <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#64748B" }}>By Tier</h3>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={byTier} dataKey="count" nameKey="tier" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {byTier.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
              <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#64748B" }}>By Audience</h3>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={byAudience} dataKey="count" nameKey="audience" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {byAudience.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
