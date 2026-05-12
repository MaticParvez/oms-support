import { useState } from "react";
import Tickets from "./pages/Tickets";
import Analytics from "./pages/Analytics";
import KnowledgeBase from "./pages/KnowledgeBase";

type Page = "tickets" | "analytics" | "knowledge";

export default function Dashboard() {
  const [page, setPage] = useState<Page>("tickets");

  const navItem = (id: Page, label: string, icon: string) => (
    <button
      onClick={() => setPage(id)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "10px 16px",
        borderRadius: 8,
        border: "none",
        background: page === id ? "#7B3FE420" : "transparent",
        color: page === id ? "#7B3FE4" : "#64748B",
        cursor: "pointer",
        fontSize: 14,
        fontWeight: page === id ? 600 : 400,
        width: "100%",
        textAlign: "left",
      }}
    >
      <span style={{ fontSize: 18 }}>{icon}</span>
      {label}
    </button>
  );

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui, sans-serif", background: "#F8FAFC" }}>
      {/* Sidebar */}
      <div style={{ width: 220, background: "#fff", borderRight: "1px solid #E2E8F0", padding: "24px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
        <div style={{ padding: "0 12px 20px", fontWeight: 700, fontSize: 16, color: "#7B3FE4" }}>
          OMS Support
        </div>
        {navItem("tickets", "Tickets", "🎫")}
        {navItem("analytics", "Analytics", "📊")}
        {navItem("knowledge", "Knowledge Base", "📚")}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {page === "tickets" && <Tickets />}
        {page === "analytics" && <Analytics />}
        {page === "knowledge" && <KnowledgeBase />}
      </div>
    </div>
  );
}
