


import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Upload,
  FileText,
  MessageSquare,
  Search,
  Lock,
  Sparkles,
  Plus,
  LogOut,
  Menu,
  X,
  Send,
  Paperclip,
  ChevronRight,
  Database,
  Brain,
  Settings,
  Eye,
  Trash2,
  MoreHorizontal,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Copy,
  ArrowLeft,
} from "lucide-react";

const API_URL =
  (import.meta as ImportMeta & { env?: { VITE_API_URL?: string } }).env
    ?.VITE_API_URL || "";

const API = async (path: string, opts: any = {}) => {
  const url = API_URL ? `${API_URL}${path}` : path;
  try {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      ...opts,
    });
    const body = await response.json().catch(() => ({}));
    return { status: response.status, body };
  } catch (error) {
    console.error("API request failed:", error);
    return {
      status: 0,
      body: { detail: "Unable to connect to backend server" },
    };
  }
};

const cream = "#E1E0CC";
const darkCard = "#101010";
const lighterCard = "#171717";
const border = "rgba(225,224,204,0.10)";
const ease = [0.16, 1, 0.3, 1] as const;

/* ================= BEE ================= */

function BeeIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32">
      <ellipse
        cx="17"
        cy="12"
        rx="8"
        ry="6"
        fill="rgba(225,224,204,.5)"
        transform="rotate(-18 17 12)"
      />
      <ellipse
        cx="19"
        cy="9"
        rx="7"
        ry="5.4"
        fill="rgba(225,224,204,.35)"
        transform="rotate(-8 19 9)"
      />
      <ellipse cx="16" cy="17" rx="9" ry="6.5" fill="#F2B23A" />
      <path
        d="M9 13.5h14M8.5 17h15M10 20.5h12"
        stroke="#111"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="24.5" cy="14" r="1.6" fill="#111" />
    </svg>
  );
}

function BeeTrail() {
  return (
    <svg
      width={100}
      height={60}
      viewBox="0 0 100 60"
      style={{ position: "absolute", top: 14, right: 14, opacity: 0.8 }}
    >
      <path
        d="M8 45 Q35 50 45 30 T80 18"
        stroke="#F2B23A"
        strokeWidth="1.2"
        strokeDasharray="2 4"
        fill="none"
        opacity=".5"
      />
      <g transform="translate(74,6)">
        <BeeIcon size={22} />
      </g>
    </svg>
  );
}

function CursorBee() {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const target = useRef({ x: -100, y: -100 });
  const cur = useRef({ x: -100, y: -100 });
  useEffect(() => {
    const move = (e: MouseEvent) => {
      target.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener("mousemove", move);
    let raf: number;
    const tick = (t: number) => {
      cur.current.x += (target.current.x - cur.current.x) * 0.1;
      cur.current.y += (target.current.y - cur.current.y) * 0.1;
      setPos({ x: cur.current.x, y: cur.current.y + Math.sin(t / 350) * 5 });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      window.removeEventListener("mousemove", move);
      cancelAnimationFrame(raf);
    };
  }, []);
  return (
    <div
      style={{
        position: "fixed",
        left: pos.x,
        top: pos.y,
        transform: "translate(-50%,-60%) rotate(-15deg)",
        pointerEvents: "none",
        zIndex: 9999,
      }}
    >
      <BeeIcon size={22} />
    </div>
  );
}

/* ================= LOGIN ================= */

function LoginPage({
  email,
  setEmail,
  password,
  setPassword,
  isRegister,
  setIsRegister,
  login,
  register,
}: any) {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 430,
          background: "#0c0c0c",
          border: `1px solid ${border}`,
          borderRadius: 28,
          padding: 34,
          position: "relative",
        }}
      >
        <BeeTrail />
        <div style={smallLabel}>
          NEXUS<span className="serif">*</span>
        </div>
        <h1
          style={{
            fontSize: 40,
            fontWeight: 400,
            letterSpacing: "-.05em",
            margin: "22px 0 8px",
          }}
        >
          {isRegister ? "Create your" : "Welcome"}
          <br />
          <span className="serif">{isRegister ? "account." : "back."}</span>
        </h1>
        <p
          style={{
            color: "rgba(225,224,204,.45)",
            fontSize: 13,
            marginBottom: 28,
          }}
        >
          {isRegister
            ? "Sign up for your document intelligence workspace."
            : "Sign in to your document intelligence workspace."}
        </p>

        <div style={fieldLabel}>EMAIL</div>
        <input
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={authInput}
        />

        <div style={{ ...fieldLabel, marginTop: 16 }}>PASSWORD</div>
        <input
          placeholder="••••••••••••"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={authInput}
        />

        <button
          onClick={isRegister ? register : login}
          style={{
            ...primaryButton,
            width: "100%",
            justifyContent: "space-between",
            marginTop: 22,
          }}
        >
          {isRegister ? "Create account" : "Sign in"}
          <span style={buttonCircle}>
            <ArrowRight size={16} />
          </span>
        </button>

        <div
          style={{
            textAlign: "center",
            marginTop: 16,
            fontSize: 12,
            color: "rgba(225,224,204,.4)",
          }}
        >
          {isRegister ? "Already have an account? " : "Don't have an account? "}
          <a
            onClick={() => setIsRegister(!isRegister)}
            style={{
              color: cream,
              textDecoration: "underline",
              cursor: "pointer",
            }}
          >
            {isRegister ? "Sign in" : "Create account"}
          </a>
        </div>
      </div>
    </div>
  );
}

/* ================= APP ================= */

function App() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token"),
  );
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  const [docs, setDocs] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<any>(null);
  const [convs, setConvs] = useState<any[]>([]);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (token) {
      fetchDocs();
      fetchConvs();
    }
  }, [token]);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  async function register() {
    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password");
      return;
    }
    const r = await API("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email: email.trim(), password }),
    });
    if (r.status === 200) {
      alert("Registered successfully. You can now login.");
      setIsRegister(false);
    } else alert(r.body.detail || "Registration failed");
  }

  async function login() {
    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password");
      return;
    }
    const r = await API("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: email.trim(), password }),
    });
    if (r.status === 200 && r.body.access_token) {
      localStorage.setItem("token", r.body.access_token);
      setToken(r.body.access_token);
    } else alert(r.body.detail || "Login failed");
  }

  async function fetchDocs() {
    const r = await API("/documents/", { method: "GET", headers });
    if (r.status === 200) {
      const data = Array.isArray(r.body)
        ? r.body
        : Array.isArray(r.body?.documents)
          ? r.body.documents
          : [];
      setDocs(data);
    } else {
      console.error("Failed to fetch documents:", r.body);
      setDocs([]);
    }
  }

  async function upload() {
    if (!file) {
      alert("Please choose a PDF file");
      return;
    }
    setUploading(true);
    const form = new FormData();
    form.append("file", file, file.name);
    const url = API_URL ? `${API_URL}/documents/upload` : "/documents/upload";
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const body = await response.json().catch(() => ({}));
      if (response.status === 200) {
        setFile(null);
        await fetchDocs();
      } else alert(body.detail || "Upload failed");
    } catch (error) {
      console.error(error);
      alert("Unable to connect to backend");
    } finally {
      setUploading(false);
    }
  }

  async function ask(docId?: number) {
    const cleanQuery = query.trim();
    if (!cleanQuery) return;
    setLoading(true);
    const payload: any = { query: cleanQuery, top_k: 5 };
    if (docId !== undefined) payload.document_id = docId;
    const r = await API("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (r.status === 200) {
      setAnswer(r.body);
      await fetchConvs();
    } else {
      const detail = r.body?.detail;
      if (Array.isArray(detail))
        alert(detail.map((e: any) => e.msg || JSON.stringify(e)).join("\n"));
      else alert(detail || `Request failed with status ${r.status}`);
    }
    setLoading(false);
  }

  async function fetchConvs() {
    const r = await API("/conversations", { method: "GET", headers });
    if (r.status === 200) {
      const data = Array.isArray(r.body)
        ? r.body
        : Array.isArray(r.body?.conversations)
          ? r.body.conversations
          : [];
      setConvs(data);
    } else {
      console.error("Failed to fetch conversations:", r.body);
      setConvs([]);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setDocs([]);
    setConvs([]);
    setAnswer(null);
    setQuery("");
  }

  const globalStyles = `
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; background: #000; color: ${cream}; font-family: Almarai, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    button, input { font-family: inherit; }
    ::selection { background: ${cream}; color: #000; }
    .grain { position: absolute; inset: 0; pointer-events: none; opacity: .08; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.8'/%3E%3C/svg%3E"); mix-blend-mode: overlay; }
    .serif { font-family: "Instrument Serif", Georgia, serif; font-style: italic; }
    .glass { background: rgba(16,16,16,.72); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid ${border}; }
    .hover-card { transition: transform .35s ease, border-color .35s ease, background .35s ease; }
    .hover-card:hover { transform: translateY(-4px); border-color: rgba(225,224,204,.22); background: #171717; }
    .sparkle-bg { position: relative; overflow: hidden; }
    .sparkle-bg::before {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 0;
      opacity: .35;
      background-image:
        radial-gradient(circle, rgba(225,224,204,.75) 1px, transparent 1.7px),
        radial-gradient(circle, rgba(242,178,58,.55) 1px, transparent 1.8px);
      background-size: 150px 150px, 230px 230px;
      background-position: 15px 25px, 80px 100px;
    }
    .sparkle-bg::after {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 0;
      opacity: .18;
      background-image: radial-gradient(circle, rgba(225,224,204,.9) 1px, transparent 2px);
      background-size: 310px 310px;
      animation: sparkleMove 14s linear infinite;
    }
    .sparkle-bg > * { position: relative; z-index: 1; }
    @keyframes sparkleMove {
      from { transform: translateY(0); }
      to { transform: translateY(-310px); }
    }
    @media(max-width: 768px) { .desktop-only { display: none !important; } }
    @media(min-width: 769px) { .mobile-only { display: none !important; } }
  `;

  if (!token) {
    return (
      <>
        <style>{globalStyles}</style>
        <CursorBee />
        <LoginPage
          email={email}
          setEmail={setEmail}
          password={password}
          setPassword={setPassword}
          isRegister={isRegister}
          setIsRegister={setIsRegister}
          login={login}
          register={register}
        />
      </>
    );
  }

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <>
      <style>{globalStyles}</style>
      <CursorBee />
      <main style={{ background: "#000" }}>
        {/* ================= HERO ================= */}
        <section
          style={{ minHeight: "100vh", padding: 16, position: "relative" }}
        >
          <div
            style={{
              position: "relative",
              minHeight: "calc(100vh - 32px)",
              overflow: "hidden",
              borderRadius: 32,
              backgroundImage:
                "linear-gradient(90deg, rgba(0,0,0,.9) 0%, rgba(0,0,0,.45) 45%, rgba(0,0,0,.15) 100%), url('/nexus-hero.jpg')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            <div className="grain" />

            <nav
              className="desktop-only"
              style={{
                position: "absolute",
                top: 0,
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 10,
                background: "#000",
                padding: "14px 28px",
                borderRadius: "0 0 24px 24px",
                display: "flex",
                gap: 30,
                alignItems: "center",
                whiteSpace: "nowrap",
              }}
            >
              <a href="#workspace" style={navLink}>
                Home
              </a>
              <a href="#how" style={navLink}>
                How it Works
              </a>
              <a href="#workspace" style={navLink}>
                AI Features
              </a>
              <a href="#" style={navLink}>
                Docs
              </a>
              <a href="#" style={navLink}>
                Pricing
              </a>
              <a href="#" style={navLink}>
                Contact
              </a>
            </nav>

            <button
              onClick={() => setMobileMenu(!mobileMenu)}
              className="mobile-only"
              style={{
                position: "absolute",
                right: 18,
                top: 18,
                zIndex: 20,
                border: "1px solid rgba(255,255,255,.15)",
                background: "rgba(0,0,0,.7)",
                color: cream,
                borderRadius: 999,
                width: 44,
                height: 44,
              }}
            >
              {mobileMenu ? <X size={20} /> : <Menu size={20} />}
            </button>

            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                bottom: 0,
                padding: "clamp(30px, 6vw, 80px)",
                display: "grid",
                gridTemplateColumns: "minmax(0, 2fr) minmax(280px, 1fr)",
                gap: 40,
                alignItems: "end",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: "clamp(70px, 18vw, 260px)",
                    lineHeight: ".75",
                    letterSpacing: "-.08em",
                    fontWeight: 400,
                  }}
                >
                  NEXUS<span className="serif">*</span>
                </div>
              </div>
              <div style={{ maxWidth: 440 }}>
                <p
                  style={{
                    fontSize: "clamp(14px, 1.5vw, 18px)",
                    lineHeight: 1.35,
                    color: "rgba(225,224,204,.72)",
                    marginBottom: 24,
                  }}
                >
                  Your intelligent document workspace.
                  <br />
                  Understand more. Create better.
                </p>
                <a
                  href="#workspace"
                  style={{ ...primaryButton, textDecoration: "none" }}
                >
                  Enter Workspace
                  <span style={buttonCircle}>
                    <ArrowRight size={18} />
                  </span>
                </a>
              </div>
            </div>

            <div
              className="glass desktop-only"
              style={{
                position: "absolute",
                right: "clamp(24px,5vw,70px)",
                bottom: 200,
                borderRadius: 18,
                padding: "16px 20px",
                maxWidth: 260,
                fontSize: 13,
                lineHeight: 1.6,
              }}
            >
              Ask anything.
              <br />
              Get grounded answers.
              <br />
              From your documents.
            </div>
          </div>
        </section>

        {/* ================= HOW IT WORKS ================= */}
        <section
          id="how"
          className="sparkle-bg"
          style={{
            padding: "100px 6vw",
            background: "#000",
            textAlign: "center",
          }}
        >
          <div style={smallLabel}>HOW NEXUS WORKS</div>
          <h2
            style={{
              fontSize: "clamp(32px, 5vw, 56px)",
              fontWeight: 400,
              letterSpacing: "-.05em",
              margin: "16px 0 60px",
            }}
          >
            How Nexus Works
          </h2>
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "flex-start",
              flexWrap: "wrap",
              gap: 6,
            }}
          >
            {[
              [
                Upload,
                "Upload",
                "Upload your PDFs and other documents to get started.",
              ],
              [
                FileText,
                "Extract",
                "We extract text and split it into manageable chunks.",
              ],
              [
                Database,
                "Embed",
                "Chunks are converted into embeddings and stored in a vector DB.",
              ],
              [
                Search,
                "Search",
                "We find the most relevant chunks for your question.",
              ],
              [
                Brain,
                "Answer",
                "AI generates accurate, grounded answers with sources.",
              ],
            ].map(([Icon, title, desc]: any, i) => (
              <React.Fragment key={title}>
                <div style={{ maxWidth: 160, textAlign: "center" }}>
                  <div style={stepCircle}>
                    <Icon size={22} strokeWidth={1.4} />
                  </div>
                  <h4
                    style={{ fontSize: 16, fontWeight: 500, margin: "0 0 6px" }}
                  >
                    {title}
                  </h4>
                  <p
                    style={{
                      fontSize: 12,
                      color: "rgba(225,224,204,.45)",
                      lineHeight: 1.5,
                    }}
                  >
                    {desc}
                  </p>
                </div>
                {i < 4 && (
                  <ChevronRight style={{ marginTop: 20, opacity: 0.25 }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </section>

        {/* ================= WORKSPACE ================= */}
        <section
          id="workspace"
          style={{ padding: "0 6vw 60px", display: "flex", gap: 15 }}
        >
          <aside
            className="desktop-only"
            style={{
              width: 250,
              background: "#070707",
              border: `1px solid ${border}`,
              borderRadius: 24,
              padding: 22,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div
              style={{
                fontSize: 24,
                letterSpacing: "-.06em",
                marginBottom: 30,
              }}
            >
              NEXUS<span className="serif">*</span>
            </div>
            <button
              onClick={() => {
                setAnswer(null);
                setQuery("");
              }}
              style={sidebarButton(true)}
            >
              <Plus size={17} />
              New Chat
            </button>

            <div style={sideTitle}>CONVERSATIONS</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {convs.slice(0, 6).map((c) => (
                <div key={c.id} style={conversationItem}>
                  <MessageSquare size={14} />
                  <span>{c.title || `Conversation ${c.id}`}</span>
                </div>
              ))}
              {convs.length === 0 && (
                <div style={emptySide}>No conversations yet</div>
              )}
            </div>

            <div style={sideTitle}>DOCUMENTS</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {docs.slice(0, 5).map((d) => (
                <div key={d.id} style={conversationItem}>
                  <FileText size={14} />
                  <span>{d.filename}</span>
                </div>
              ))}
              {docs.length === 0 && (
                <div style={emptySide}>No documents yet</div>
              )}
            </div>

            <div style={sideTitle}>SETTINGS</div>
            <div style={conversationItem}>
              <Settings size={14} />
              Settings
            </div>
            <div
              style={{ ...conversationItem, cursor: "pointer" }}
              onClick={logout}
            >
              <LogOut size={14} />
              Log out
            </div>

            <div
              style={{
                marginTop: "auto",
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "12px 8px",
                borderTop: `1px solid ${border}`,
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  background: cream,
                  color: "#000",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 13,
                  fontWeight: 700,
                  flexShrink: 0,
                }}
              >
                {(email || "U")[0].toUpperCase()}
              </div>
              <div style={{ fontSize: 11, overflow: "hidden" }}>
                <div
                  style={{
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                    overflow: "hidden",
                  }}
                >
                  {email ? email.split("@")[0] : "User"}
                </div>
                <div
                  style={{
                    opacity: 0.4,
                    fontSize: 9,
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                    overflow: "hidden",
                  }}
                >
                  {email}
                </div>
              </div>
            </div>
          </aside>

          <div
            className="mobile-only"
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              height: 68,
              zIndex: 30,
              background: "rgba(0,0,0,.88)",
              backdropFilter: "blur(20px)",
              borderBottom: `1px solid ${border}`,
              padding: "0 18px",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ fontSize: 24 }}>
              NEXUS<span className="serif">*</span>
            </div>
            <button
              onClick={logout}
              style={{ background: "transparent", border: 0, color: cream }}
            >
              <LogOut size={18} />
            </button>
          </div>

          <section
            style={{
              flex: 1,
              minWidth: 0,
              display: "grid",
              gridTemplateColumns: "minmax(0, 1fr) 300px",
              gap: 15,
            }}
          >
            <div
              style={{
                minWidth: 0,
                minHeight: 560,
                background: darkCard,
                border: `1px solid ${border}`,
                borderRadius: 28,
                padding: "clamp(20px, 3vw, 30px)",
                display: "flex",
                flexDirection: "column",
              }}
            >
              {answer && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 20,
                    borderBottom: `1px solid ${border}`,
                    paddingBottom: 16,
                  }}
                >
                  <ArrowLeft
                    size={16}
                    style={{ cursor: "pointer", opacity: 0.6 }}
                    onClick={() => {
                      setAnswer(null);
                      setQuery("");
                    }}
                  />
                  <span style={{ fontSize: 14, flex: 1 }}>{query}</span>
                  <MoreHorizontal size={16} style={{ opacity: 0.5 }} />
                </div>
              )}

              {!answer && (
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    padding: 30,
                  }}
                >
                  <div>
                    <div
                      style={{
                        width: 65,
                        height: 65,
                        borderRadius: "50%",
                        margin: "0 auto 25px",
                        border: "1px solid rgba(225,224,204,.18)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        background:
                          "radial-gradient(circle, rgba(225,224,204,.14), transparent)",
                      }}
                    >
                      <Sparkles size={24} />
                    </div>
                    <h2 style={{ fontWeight: 400, fontSize: 25, margin: 0 }}>
                      Ask anything.
                    </h2>
                    <p
                      style={{
                        color: "rgba(225,224,204,.4)",
                        fontSize: 13,
                        maxWidth: 390,
                        lineHeight: 1.5,
                      }}
                    >
                      Ask a question about the information contained in your
                      uploaded documents.
                    </p>
                  </div>
                </div>
              )}

              {answer && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{
                    flex: 1,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: 22,
                  }}
                >
                  <div style={{ alignSelf: "flex-end", maxWidth: "75%" }}>
                    <div
                      style={{
                        background: cream,
                        color: "#000",
                        padding: "12px 16px",
                        borderRadius: "16px 16px 4px 16px",
                        fontSize: 13,
                      }}
                    >
                      {query}
                    </div>
                    <div
                      style={{
                        textAlign: "right",
                        fontSize: 9,
                        opacity: 0.35,
                        marginTop: 4,
                      }}
                    >
                      {time}
                    </div>
                  </div>
                  <div style={{ maxWidth: "88%" }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        marginBottom: 8,
                      }}
                    >
                      <div
                        style={{
                          width: 26,
                          height: 26,
                          borderRadius: "50%",
                          border: `1px solid ${border}`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <Sparkles size={13} />
                      </div>
                      <span style={{ fontSize: 11, opacity: 0.6 }}>
                        Nexus AI
                      </span>
                      <span style={{ fontSize: 9, opacity: 0.3 }}>{time}</span>
                    </div>
                    <div
                      style={{
                        background: lighterCard,
                        border: `1px solid ${border}`,
                        borderRadius: "4px 16px 16px 16px",
                        padding: "16px 18px",
                        fontSize: 14,
                        lineHeight: 1.6,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {answer.answer || "No answer returned."}
                    </div>
                    <div
                      style={{
                        display: "flex",
                        gap: 14,
                        marginTop: 10,
                        opacity: 0.4,
                      }}
                    >
                      <Copy
                        size={14}
                        style={{ cursor: "pointer" }}
                        onClick={() =>
                          navigator.clipboard.writeText(answer.answer || "")
                        }
                      />
                      <ThumbsUp size={14} />
                      <ThumbsDown size={14} />
                      <RotateCcw size={14} />
                    </div>
                  </div>
                </motion.div>
              )}

              <div
                style={{
                  marginTop: 24,
                  display: "flex",
                  gap: 8,
                  padding: 7,
                  borderRadius: 999,
                  background: "#212121",
                  border: `1px solid ${border}`,
                }}
              >
                <input
                  id="pdf-input-hidden"
                  type="file"
                  accept="application/pdf"
                  style={{ display: "none" }}
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <button
                  onClick={() =>
                    (
                      document.getElementById(
                        "pdf-input-hidden",
                      ) as HTMLInputElement
                    )?.click()
                  }
                  style={{
                    width: 43,
                    height: 43,
                    borderRadius: "50%",
                    background: "transparent",
                    color: "rgba(225,224,204,.6)",
                    border: 0,
                    cursor: "pointer",
                    flexShrink: 0,
                  }}
                >
                  <Paperclip size={18} />
                </button>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") ask();
                  }}
                  placeholder="Ask anything about your documents..."
                  style={{
                    flex: 1,
                    minWidth: 0,
                    border: 0,
                    outline: 0,
                    background: "transparent",
                    color: cream,
                    fontSize: 13,
                  }}
                />
                <button
                  onClick={() => ask()}
                  disabled={loading}
                  style={{
                    width: 43,
                    height: 43,
                    borderRadius: "50%",
                    border: 0,
                    background: cream,
                    color: "#000",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    flexShrink: 0,
                    opacity: loading ? 0.5 : 1,
                  }}
                >
                  {loading ? (
                    <span style={{ fontSize: 10 }}>...</span>
                  ) : (
                    <Send size={17} />
                  )}
                </button>
              </div>
            </div>

            <aside
              className="desktop-only"
              style={{
                background: darkCard,
                border: `1px solid ${border}`,
                borderRadius: 28,
                padding: 24,
                minHeight: 560,
              }}
            >
              <div style={smallLabel}>SOURCES</div>
              {!answer?.sources?.length ? (
                <div
                  style={{
                    color: "rgba(225,224,204,.35)",
                    fontSize: 12,
                    lineHeight: 1.5,
                    marginTop: 30,
                  }}
                >
                  Sources used to answer your questions will appear here.
                </div>
              ) : (
                <div
                  style={{
                    marginTop: 22,
                    display: "flex",
                    flexDirection: "column",
                    gap: 10,
                  }}
                >
                  {answer.sources.map((source: any, index: number) => (
                    <motion.div
                      key={`${source.chunk_id}-${index}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.07, ease }}
                      style={{
                        background: lighterCard,
                        border: `1px solid ${border}`,
                        borderRadius: 16,
                        padding: 14,
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          gap: 9,
                          alignItems: "center",
                        }}
                      >
                        <FileText size={16} />
                        <div
                          style={{
                            fontSize: 11,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          Document {source.document_id}
                        </div>
                      </div>
                      <div
                        style={{
                          color: "rgba(225,224,204,.4)",
                          fontSize: 9,
                          marginTop: 8,
                        }}
                      >
                        Chunk {source.chunk_id}
                        {source.page_number
                          ? ` · Page ${source.page_number}`
                          : ""}
                      </div>
                      <p
                        style={{
                          fontSize: 10,
                          color: "rgba(225,224,204,.55)",
                          lineHeight: 1.45,
                          margin: "10px 0",
                        }}
                      >
                        {source.content?.slice(0, 130)}
                        {source.content?.length > 130 ? "..." : ""}
                      </p>
                      <div
                        style={{
                          color: "#9fbe8d",
                          fontSize: 9,
                          marginBottom: 5,
                        }}
                      >
                        {source.similarity
                          ? `${(source.similarity * 100).toFixed(1)}% match`
                          : "Source"}
                      </div>
                      <div
                        style={{
                          height: 3,
                          borderRadius: 2,
                          background: "rgba(225,224,204,.1)",
                        }}
                      >
                        <div
                          style={{
                            height: "100%",
                            width: `${Math.min(100, (source.similarity || 0) * 100)}%`,
                            borderRadius: 2,
                            background: "#9fbe8d",
                          }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </aside>
          </section>
        </section>

        {/* ================= DOCUMENTS ================= */}
        <section style={{ padding: "0 6vw 100px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 20,
            }}
          >
            <div>
              <div style={smallLabel}>MY DOCUMENTS</div>
              <h2 style={{ fontSize: 28, fontWeight: 400, margin: "8px 0 0" }}>
                Your knowledge base
              </h2>
            </div>
            <button
              onClick={() =>
                (
                  document.getElementById(
                    "pdf-input-hidden",
                  ) as HTMLInputElement
                )?.click()
              }
              style={{ ...primaryButton, padding: "9px 16px" }}
            >
              <Upload size={15} />
              Upload Document
            </button>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 10,
            }}
          >
            <div
              onClick={() =>
                (
                  document.getElementById(
                    "pdf-input-hidden",
                  ) as HTMLInputElement
                )?.click()
              }
              style={{
                border: `1px dashed rgba(225,224,204,.25)`,
                borderRadius: 20,
                padding: 20,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                cursor: "pointer",
                minHeight: 150,
              }}
            >
              <Upload size={20} style={{ opacity: 0.5, marginBottom: 10 }} />
              <div style={{ fontSize: 13 }}>Add a document</div>
              <div
                style={{
                  fontSize: 10,
                  color: "rgba(225,224,204,.4)",
                  marginTop: 4,
                }}
              >
                Drop your PDF here or browse
              </div>
              {file && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    upload();
                  }}
                  disabled={uploading}
                  style={{
                    ...primaryButton,
                    marginTop: 12,
                    padding: "6px 14px",
                    fontSize: 11,
                  }}
                >
                  {uploading ? "Uploading..." : `Upload ${file.name}`}
                </button>
              )}
            </div>

            {docs.map((doc) => (
              <motion.div
                key={doc.id}
                whileHover={{ y: -4 }}
                style={{
                  background: darkCard,
                  border: `1px solid ${border}`,
                  borderRadius: 20,
                  padding: 20,
                  position: "relative",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <span
                    style={{
                      background: "#7a2a2a",
                      color: cream,
                      fontSize: 9,
                      fontWeight: 700,
                      padding: "3px 7px",
                      borderRadius: 5,
                    }}
                  >
                    PDF
                  </span>
                  <FileText size={18} style={{ opacity: 0.6 }} />
                </div>
                <div
                  style={{
                    marginTop: 30,
                    fontSize: 13,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {doc.filename}
                </div>
                <div style={{ marginTop: 5, fontSize: 10, color: "#9fbe8d" }}>
                  Processed
                </div>
                <div
                  style={{
                    display: "flex",
                    gap: 12,
                    marginTop: 14,
                    opacity: 0.4,
                  }}
                >
                  <Eye size={13} />
                  <MoreHorizontal size={13} />
                  <Trash2 size={13} />
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}

/* ================= STYLES ================= */

const navLink: React.CSSProperties = {
  color: "rgba(225,224,204,.75)",
  textDecoration: "none",
  fontSize: 11,
};
const primaryButton: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 12,
  padding: "7px 7px 7px 18px",
  borderRadius: 999,
  border: 0,
  background: cream,
  color: "#000",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
};
const buttonCircle: React.CSSProperties = {
  width: 37,
  height: 37,
  borderRadius: "50%",
  background: "#000",
  color: cream,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};
const smallLabel: React.CSSProperties = {
  fontSize: 10,
  letterSpacing: ".16em",
  color: cream,
  fontWeight: 700,
};
const fieldLabel: React.CSSProperties = {
  fontSize: 10,
  letterSpacing: ".12em",
  color: "rgba(225,224,204,.45)",
  marginBottom: 7,
};
const sideTitle: React.CSSProperties = {
  marginTop: 28,
  marginBottom: 10,
  fontSize: 9,
  letterSpacing: ".15em",
  color: "rgba(225,224,204,.28)",
};
const conversationItem: React.CSSProperties = {
  display: "flex",
  gap: 9,
  alignItems: "center",
  padding: "9px 8px",
  borderRadius: 8,
  color: "rgba(225,224,204,.5)",
  fontSize: 11,
  overflow: "hidden",
};
const emptySide: React.CSSProperties = {
  color: "rgba(225,224,204,.22)",
  fontSize: 10,
  padding: "5px 8px",
};
const sidebarButton = (active: boolean): React.CSSProperties => ({
  display: "flex",
  alignItems: "center",
  gap: 10,
  width: "100%",
  padding: "11px 12px",
  borderRadius: 10,
  border: active ? `1px solid ${border}` : "1px solid transparent",
  background: active ? "#171717" : "transparent",
  color: active ? cream : "rgba(225,224,204,.45)",
  cursor: "pointer",
  textAlign: "left",
  fontSize: 11,
});
const authInput: React.CSSProperties = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: 13,
  border: `1px solid ${border}`,
  background: "#171717",
  color: cream,
  outline: "none",
  fontSize: 12,
};
const stepCircle: React.CSSProperties = {
  width: 64,
  height: 64,
  borderRadius: "50%",
  border: `1px solid ${border}`,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  margin: "0 auto 16px",
  background: "radial-gradient(circle, rgba(225,224,204,.08), transparent)",
};

createRoot(document.getElementById("root")!).render(<App />);