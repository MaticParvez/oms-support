import { useEffect, useState } from "react";

const API = "/api";

export default function KnowledgeBase() {
  const [stats, setStats] = useState<{ total_chunks: number } | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [gaps, setGaps] = useState<any[]>([]);
  const [urlInput, setUrlInput] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch(`${API}/knowledge/stats`).then((r) => r.json()).then(setStats);
    fetch(`${API}/feedback/gaps?limit=10`).then((r) => r.json()).then(setGaps);
  }, []);

  const search = async () => {
    if (!query.trim()) return;
    const r = await fetch(`${API}/knowledge/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, n_results: 5 }),
    });
    const d = await r.json();
    setResults(d.results);
  };

  const ingestUrl = async () => {
    if (!urlInput.trim()) return;
    setStatus("Ingesting...");
    try {
      const r = await fetch(`${API}/knowledge/ingest/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput, category: "docs" }),
      });
      const d = await r.json();
      setStatus(`Ingested ${d.chunks_stored} chunks`);
      setUrlInput("");
      fetch(`${API}/knowledge/stats`).then((r) => r.json()).then(setStats);
    } catch {
      setStatus("Error ingesting URL");
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 20 }}>Knowledge Base</h2>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={{ background: "#fff", borderRadius: 12, padding: "16px 20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", flex: 1 }}>
          <div style={{ fontSize: 12, color: "#94A3B8" }}>Total Chunks</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#7B3FE4" }}>{stats?.total_chunks ?? "—"}</div>
        </div>
        <div style={{ background: "#fff", borderRadius: 12, padding: "16px 20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", flex: 1 }}>
          <div style={{ fontSize: 12, color: "#94A3B8" }}>Knowledge Gaps Flagged</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#F97316" }}>{gaps.length}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {/* Ingest URL */}
        <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 12px", fontSize: 14 }}>Ingest URL</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://docs.polygon.technology/oms/..."
              style={{ flex: 1, padding: "8px 12px", borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 13 }}
            />
            <button onClick={ingestUrl} style={{ padding: "8px 16px", background: "#7B3FE4", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer", fontSize: 13 }}>
              Ingest
            </button>
          </div>
          {status && <div style={{ marginTop: 8, fontSize: 12, color: "#64748B" }}>{status}</div>}
        </div>

        {/* Search */}
        <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 12px", fontSize: 14 }}>Search Knowledge Base</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="Search docs..."
              style={{ flex: 1, padding: "8px 12px", borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 13 }}
            />
            <button onClick={search} style={{ padding: "8px 16px", background: "#3B82F6", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer", fontSize: 13 }}>
              Search
            </button>
          </div>
        </div>
      </div>

      {results.length > 0 && (
        <div style={{ marginTop: 20, background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 12px", fontSize: 14 }}>Search Results</h3>
          {results.map((r, i) => (
            <div key={i} style={{ borderBottom: "1px solid #F1F5F9", paddingBottom: 12, marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontWeight: 600, fontSize: 13 }}>{r.metadata?.title || r.metadata?.source}</span>
                <span style={{ fontSize: 12, color: "#7B3FE4" }}>Score: {(r.score * 100).toFixed(0)}%</span>
              </div>
              <p style={{ margin: 0, fontSize: 13, color: "#64748B", lineHeight: 1.5 }}>{r.text.slice(0, 300)}...</p>
            </div>
          ))}
        </div>
      )}

      {gaps.length > 0 && (
        <div style={{ marginTop: 20, background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 12px", fontSize: 14, color: "#F97316" }}>Knowledge Gaps (from user feedback)</h3>
          {gaps.map((g) => (
            <div key={g.id} style={{ borderBottom: "1px solid #F1F5F9", paddingBottom: 8, marginBottom: 8, display: "flex", gap: 12, fontSize: 13 }}>
              <span style={{ flex: 1 }}>{g.gap}</span>
              {g.category && <span style={{ background: "#FFF3CD", padding: "2px 8px", borderRadius: 12, fontSize: 12 }}>{g.category}</span>}
              <span style={{ color: "#94A3B8", fontSize: 12 }}>{new Date(g.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
