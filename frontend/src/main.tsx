import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  ArrowUpRight,
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
  Check,
  ChevronRight,
  Database,
  Brain,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "";

const API = async (path: string, opts: any = {}) => {
  const url = API_URL ? `${API_URL}${path}` : path;

  try {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(opts.headers || {}),
      },
      ...opts,
    });

    const body = await response.json().catch(() => ({}));

    return {
      status: response.status,
      body,
    };
  } catch (error) {
    console.error("API request failed:", error);

    return {
      status: 0,
      body: {
        detail: "Unable to connect to backend server",
      },
    };
  }
};

const cream = "#E1E0CC";
const darkCard = "#101010";
const lighterCard = "#171717";
const border = "rgba(225,224,204,0.10)";

const ease = [0.16, 1, 0.3, 1] as const;

function Reveal({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 25 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.8, delay, ease }}
    >
      {children}
    </motion.div>
  );
}

function App() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token"),
  );

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [docs, setDocs] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);

  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<any>(null);

  const [convs, setConvs] = useState<any[]>([]);

  const [showWorkspace, setShowWorkspace] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (token) {
      fetchDocs();
      fetchConvs();
    }
  }, [token]);

  const headers = token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};

  async function register() {
    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password");
      return;
    }

    const r = await API("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: email.trim(),
        password,
      }),
    });

    if (r.status === 200) {
      alert("Registered successfully. You can now login.");
    } else {
      alert(r.body.detail || "Registration failed");
    }
  }

  async function login() {
    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password");
      return;
    }

    const r = await API("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: email.trim(),
        password,
      }),
    });

    if (r.status === 200 && r.body.access_token) {
      localStorage.setItem("token", r.body.access_token);
      setToken(r.body.access_token);
      setShowAuth(false);
      setShowWorkspace(true);
    } else {
      alert(r.body.detail || "Login failed");
    }
  }

  async function fetchDocs() {
    const r = await API("/documents/", {
      method: "GET",
      headers,
    });

    if (r.status === 200) {
      setDocs(r.body);
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

    const url = API_URL
      ? `${API_URL}/documents/upload`
      : "/documents/upload";

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: form,
      });

      const body = await response.json().catch(() => ({}));

      if (response.status === 200) {
        setFile(null);
        await fetchDocs();
      } else {
        alert(body.detail || "Upload failed");
      }
    } catch (error) {
      console.error(error);
      alert("Unable to connect to backend");
    } finally {
      setUploading(false);
    }
  }

  async function ask(docId?: number) {
    const cleanQuery = query.trim();

    if (!cleanQuery) {
      return;
    }

    setLoading(true);

    const payload: any = {
      query: cleanQuery,
      top_k: 5,
    };

    if (docId !== undefined) {
      payload.document_id = docId;
    }

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

      if (Array.isArray(detail)) {
        alert(
          detail
            .map((error: any) => error.msg || JSON.stringify(error))
            .join("\n"),
        );
      } else {
        alert(detail || `Request failed with status ${r.status}`);
      }
    }

    setLoading(false);
  }

  async function fetchConvs() {
    const r = await API("/conversations", {
      method: "GET",
      headers,
    });

    if (r.status === 200) {
      setConvs(r.body);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setDocs([]);
    setConvs([]);
    setAnswer(null);
    setQuery("");
    setShowWorkspace(false);
  }

  /* =========================================================
     GLOBAL STYLES
  ========================================================= */

  const globalStyles = `
    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      background: #000;
      color: ${cream};
      font-family: Almarai, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button, input {
      font-family: inherit;
    }

    ::selection {
      background: ${cream};
      color: #000;
    }

    .grain {
      position: absolute;
      inset: 0;
      pointer-events: none;
      opacity: .08;
      background-image:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.8'/%3E%3C/svg%3E");
      mix-blend-mode: overlay;
    }

    .serif {
      font-family: "Instrument Serif", Georgia, serif;
      font-style: italic;
    }

    .cream {
      color: ${cream};
    }

    .muted {
      color: rgba(225,224,204,.55);
    }

    .glass {
      background: rgba(16,16,16,.72);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid ${border};
    }

    .hover-card {
      transition: transform .35s ease, border-color .35s ease, background .35s ease;
    }

    .hover-card:hover {
      transform: translateY(-5px);
      border-color: rgba(225,224,204,.22);
      background: #171717;
    }

    @media(max-width: 768px) {
      .desktop-only {
        display: none !important;
      }
    }

    @media(min-width: 769px) {
      .mobile-only {
        display: none !important;
      }
    }
  `;

  /* =========================================================
     LANDING PAGE
  ========================================================= */

  if (!showWorkspace && !token) {
    return (
      <>
        <style>{globalStyles}</style>

        <main style={{ background: "#000" }}>
          {/* ================= HERO ================= */}

          <section
            style={{
              minHeight: "100vh",
              padding: "16px",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "relative",
                minHeight: "calc(100vh - 32px)",
                overflow: "hidden",
                borderRadius: 32,
                background:
                  "radial-gradient(circle at 70% 30%, #4a4131 0%, #16130f 40%, #050505 80%)",
              }}
            >
              {/* cinematic abstract background */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "linear-gradient(135deg, #17130e 0%, #493a28 35%, #100f0c 70%, #000 100%)",
                }}
              />

              <div
                style={{
                  position: "absolute",
                  width: 600,
                  height: 600,
                  borderRadius: "50%",
                  right: "-10%",
                  top: "10%",
                  background:
                    "radial-gradient(circle, rgba(190,145,78,.34), transparent 65%)",
                  filter: "blur(20px)",
                }}
              />

              <div
                style={{
                  position: "absolute",
                  width: 400,
                  height: 400,
                  borderRadius: "50%",
                  left: "-10%",
                  bottom: "-10%",
                  background:
                    "radial-gradient(circle, rgba(100,85,60,.25), transparent 65%)",
                  filter: "blur(30px)",
                }}
              />

              <div className="grain" />

              {/* NAVBAR */}

              <nav
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
                className="desktop-only"
              >
                <a href="#about" style={navLink}>
                  How it works
                </a>
                <a href="#features" style={navLink}>
                  AI features
                </a>
                <a href="#workspace" style={navLink}>
                  Workspace
                </a>
                <button
                  onClick={() => setShowAuth(true)}
                  style={{
                    ...navLink,
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                  }}
                >
                  Login
                </button>
              </nav>

              {/* mobile nav */}

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

              {/* HERO CONTENT */}

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
                  <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, ease }}
                  >
                    <div
                      style={{
                        fontSize: "clamp(70px, 18vw, 260px)",
                        lineHeight: ".75",
                        letterSpacing: "-.08em",
                        fontWeight: 400,
                        color: cream,
                      }}
                    >
                      NEXUS<span className="serif">*</span>
                    </div>
                  </motion.div>
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 25 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: .8, delay: .4, ease }}
                  style={{ maxWidth: 440 }}
                >
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

                  <button
                    onClick={() => setShowAuth(true)}
                    style={primaryButton}
                  >
                    Enter Workspace
                    <span style={buttonCircle}>
                      <ArrowRight size={18} />
                    </span>
                  </button>
                </motion.div>
              </div>
            </div>
          </section>

          {/* ================= HOW IT WORKS ================= */}

          <section
            id="about"
            style={{
              padding: "140px 6vw",
              background: "#000",
            }}
          >
            <Reveal>
              <div style={smallLabel}>HOW NEXUS WORKS</div>

              <h2
                style={{
                  fontSize: "clamp(42px, 7vw, 100px)",
                  fontWeight: 400,
                  letterSpacing: "-.06em",
                  lineHeight: .9,
                  maxWidth: 900,
                  margin: "20px 0 25px",
                }}
              >
                From documents
                <br />
                <span className="serif">to answers.</span>
              </h2>

              <p
                style={{
                  maxWidth: 560,
                  color: "rgba(225,224,204,.55)",
                  fontSize: 16,
                  lineHeight: 1.5,
                }}
              >
                A simple pipeline transforms your PDFs into searchable
                knowledge and gives you grounded answers using AI.
              </p>
            </Reveal>

            <div
              style={{
                marginTop: 80,
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
                gap: 1,
                background: border,
              }}
            >
              {[
                [Upload, "01", "Upload", "Add your PDF documents."],
                [FileText, "02", "Extract", "Read and process document text."],
                [Database, "03", "Embed", "Convert content into vectors."],
                [Search, "04", "Search", "Find the most relevant chunks."],
                [Brain, "05", "Answer", "Generate a grounded response."],
              ].map(([Icon, number, title, description]: any, index) => (
                <Reveal key={title} delay={index * .08}>
                  <div
                    className="hover-card"
                    style={{
                      minHeight: 250,
                      background: darkCard,
                      padding: 28,
                      border: `1px solid ${border}`,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        color: "rgba(225,224,204,.35)",
                        fontSize: 12,
                      }}
                    >
                      <span>{number}</span>
                      <Icon size={20} color={cream} strokeWidth={1.4} />
                    </div>

                    <div style={{ marginTop: 80 }}>
                      <h3
                        style={{
                          fontSize: 22,
                          fontWeight: 400,
                          margin: 0,
                        }}
                      >
                        {title}
                      </h3>

                      <p
                        style={{
                          color: "rgba(225,224,204,.45)",
                          fontSize: 13,
                          lineHeight: 1.5,
                        }}
                      >
                        {description}
                      </p>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </section>

          {/* ================= FEATURES ================= */}

          <section
            id="features"
            style={{
              minHeight: "100vh",
              padding: "100px 6vw 140px",
              background: "#050505",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div className="grain" />

            <Reveal>
              <div style={smallLabel}>AI FEATURES</div>

              <h2
                style={{
                  fontSize: "clamp(42px, 7vw, 100px)",
                  fontWeight: 400,
                  letterSpacing: "-.06em",
                  lineHeight: .9,
                  margin: "20px 0 80px",
                }}
              >
                Intelligent.
                <br />
                <span style={{ color: "rgba(225,224,204,.35)" }}>
                  Grounded. Personal.
                </span>
              </h2>
            </Reveal>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: 12,
              }}
            >
              {/* SOURCE GROUNDING */}

              <Reveal>
                <FeatureCard
                  number="01"
                  icon={<Search size={23} />}
                  title="Source Grounding"
                  description="Every answer is backed by relevant document sources so you can verify the information."
                >
                  <div style={miniSource}>
                    <div style={{ display: "flex", gap: 10 }}>
                      <FileText size={18} />
                      <div>
                        <div style={{ fontSize: 13 }}>Komal Resume</div>
                        <div style={{ fontSize: 10, opacity: .4 }}>
                          Chunk 92 · Source
                        </div>
                      </div>
                    </div>

                    <div
                      style={{
                        marginTop: 18,
                        fontSize: 11,
                        lineHeight: 1.5,
                        opacity: .55,
                      }}
                    >
                      "React, Node.js, MongoDB, Socket.io..."
                    </div>

                    <div
                      style={{
                        marginTop: 15,
                        fontSize: 11,
                        color: "#9fbe8d",
                      }}
                    >
                      75.9% similarity
                    </div>
                  </div>
                </FeatureCard>
              </Reveal>

              {/* CONVERSATION HISTORY */}

              <Reveal delay={.1}>
                <FeatureCard
                  number="02"
                  icon={<MessageSquare size={23} />}
                  title="Conversation History"
                  description="Keep your previous conversations organized and return to questions you've already explored."
                >
                  <div style={miniConversation}>
                    <div style={conversationRow}>
                      <span>Resume projects</span>
                      <ChevronRight size={14} />
                    </div>

                    <div style={conversationRow}>
                      <span>Technical skills</span>
                      <ChevronRight size={14} />
                    </div>

                    <div style={conversationRow}>
                      <span>My experience</span>
                      <ChevronRight size={14} />
                    </div>
                  </div>
                </FeatureCard>
              </Reveal>

              {/* PRIVATE */}

              <Reveal delay={.2}>
                <FeatureCard
                  number="03"
                  icon={<Lock size={23} />}
                  title="Secure & Private"
                  description="Documents and conversations are tied to authenticated users and protected by ownership checks."
                >
                  <div
                    style={{
                      height: 145,
                      borderRadius: 16,
                      background:
                        "radial-gradient(circle at 50% 45%, rgba(225,224,204,.15), transparent 55%)",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <div
                      style={{
                        width: 70,
                        height: 70,
                        borderRadius: "50%",
                        border: "1px solid rgba(225,224,204,.25)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Lock size={27} strokeWidth={1.3} />
                    </div>
                  </div>
                </FeatureCard>
              </Reveal>
            </div>
          </section>

          {/* AUTH MODAL */}

          <AnimatePresence>
            {showAuth && (
              <AuthModal
                email={email}
                password={password}
                setEmail={setEmail}
                setPassword={setPassword}
                login={login}
                register={register}
                close={() => setShowAuth(false)}
              />
            )}
          </AnimatePresence>
        </main>
      </>
    );
  }

  /* =========================================================
     WORKSPACE
  ========================================================= */

  return (
    <>
      <style>{globalStyles}</style>

      <div
        style={{
          minHeight: "100vh",
          background: "#000",
          display: "flex",
          color: cream,
        }}
      >
        {/* SIDEBAR */}

        <aside
          className="desktop-only"
          style={{
            width: 260,
            minHeight: "100vh",
            padding: 24,
            borderRight: `1px solid ${border}`,
            background: "#070707",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              fontSize: 27,
              letterSpacing: "-.07em",
              marginBottom: 55,
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

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 3,
            }}
          >
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

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 3,
            }}
          >
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

          <div style={{ marginTop: "auto" }}>
            <button
              onClick={logout}
              style={{
                ...sidebarButton(false),
                color: "rgba(225,224,204,.55)",
              }}
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </aside>

        {/* MOBILE TOP BAR */}

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
            style={{
              background: "transparent",
              border: 0,
              color: cream,
            }}
          >
            <LogOut size={18} />
          </button>
        </div>

        {/* MAIN */}

        <main
          style={{
            flex: 1,
            minWidth: 0,
            padding: "clamp(90px, 7vw, 70px) clamp(18px, 5vw, 70px) 50px",
          }}
        >
          {/* HEADER */}

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              gap: 20,
              marginBottom: 50,
            }}
          >
            <div>
              <div style={smallLabel}>YOUR WORKSPACE</div>

              <h1
                style={{
                  fontSize: "clamp(42px, 6vw, 82px)",
                  fontWeight: 400,
                  letterSpacing: "-.06em",
                  lineHeight: .9,
                  margin: "12px 0 0",
                }}
              >
                Ask your
                <br />
                <span className="serif">documents.</span>
              </h1>
            </div>

            <button
              onClick={() => {
                const input = document.getElementById(
                  "pdf-input",
                ) as HTMLInputElement | null;

                input?.click();
              }}
              style={primaryButton}
            >
              <Upload size={17} />
              Add Document
            </button>
          </div>

          {/* UPLOAD AREA */}

          <div
            className="glass"
            style={{
              borderRadius: 24,
              padding: 24,
              marginBottom: 35,
            }}
          >
            <input
              id="pdf-input"
              type="file"
              accept="application/pdf"
              style={{ display: "none" }}
              onChange={(e) =>
                setFile(e.target.files?.[0] || null)
              }
            />

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 15,
                flexWrap: "wrap",
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 14,
                  background: "#212121",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <Paperclip size={20} />
              </div>

              <div style={{ flex: 1, minWidth: 180 }}>
                <div style={{ fontSize: 14 }}>
                  {file ? file.name : "Add a PDF to your workspace"}
                </div>

                <div
                  style={{
                    color: "rgba(225,224,204,.4)",
                    fontSize: 11,
                    marginTop: 4,
                  }}
                >
                  {file
                    ? "Ready to upload"
                    : "Upload documents to ask questions about them"}
                </div>
              </div>

              {file && (
                <button
                  onClick={upload}
                  disabled={uploading}
                  style={{
                    ...primaryButton,
                    opacity: uploading ? .5 : 1,
                  }}
                >
                  {uploading ? "Uploading..." : "Upload"}
                  {!uploading && <ArrowRight size={16} />}
                </button>
              )}
            </div>
          </div>

          {/* CHAT */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(0, 1fr) 300px",
              gap: 15,
            }}
          >
            <section
              style={{
                minWidth: 0,
                minHeight: 560,
                background: darkCard,
                border: `1px solid ${border}`,
                borderRadius: 28,
                padding: "clamp(20px, 3vw, 35px)",
                display: "flex",
                flexDirection: "column",
              }}
            >
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

                    <h2
                      style={{
                        fontWeight: 400,
                        fontSize: 25,
                        margin: 0,
                      }}
                    >
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
                      Ask a question about the information contained in
                      your uploaded documents.
                    </p>
                  </div>
                </div>
              )}

              {answer && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ flex: 1 }}
                >
                  <div style={smallLabel}>AI RESPONSE</div>

                  <div
                    style={{
                      marginTop: 20,
                      fontSize: "clamp(17px, 2vw, 22px)",
                      lineHeight: 1.5,
                      color: cream,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {answer.answer || "No answer returned."}
                  </div>
                </motion.div>
              )}

              {/* INPUT */}

              <div
                style={{
                  marginTop: 30,
                  display: "flex",
                  gap: 8,
                  padding: 7,
                  borderRadius: 999,
                  background: "#212121",
                  border: `1px solid ${border}`,
                }}
              >
                <button
                  onClick={() => {
                    const input = document.getElementById(
                      "pdf-input",
                    ) as HTMLInputElement | null;

                    input?.click();
                  }}
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
                    opacity: loading ? .5 : 1,
                  }}
                >
                  {loading ? (
                    <span style={{ fontSize: 10 }}>...</span>
                  ) : (
                    <Send size={17} />
                  )}
                </button>
              </div>
            </section>

            {/* SOURCES */}

            <aside
              style={{
                background: darkCard,
                border: `1px solid ${border}`,
                borderRadius: 28,
                padding: 24,
                minHeight: 560,
              }}
              className="desktop-only"
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
                      transition={{
                        delay: index * .07,
                        ease,
                      }}
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
                        }}
                      >
                        {source.similarity
                          ? `${(source.similarity * 100).toFixed(1)}% match`
                          : "Source"}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </aside>
          </div>

          {/* DOCUMENTS */}

          <section
            style={{
              marginTop: 60,
            }}
          >
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

                <h2
                  style={{
                    fontSize: 28,
                    fontWeight: 400,
                    margin: "8px 0 0",
                  }}
                >
                  Your knowledge base
                </h2>
              </div>

              <span
                style={{
                  fontSize: 11,
                  color: "rgba(225,224,204,.35)",
                }}
              >
                {docs.length} documents
              </span>
            </div>

            {docs.length === 0 ? (
              <div
                className="glass"
                style={{
                  borderRadius: 22,
                  padding: 40,
                  textAlign: "center",
                }}
              >
                <FileText
                  size={28}
                  style={{ opacity: .5, marginBottom: 10 }}
                />

                <div style={{ fontSize: 14 }}>
                  No documents uploaded yet.
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 10,
                }}
              >
                {docs.map((doc) => (
                  <motion.div
                    key={doc.id}
                    whileHover={{ y: -4 }}
                    style={{
                      background: darkCard,
                      border: `1px solid ${border}`,
                      borderRadius: 20,
                      padding: 20,
                    }}
                  >
                    <FileText size={22} />

                    <div
                      style={{
                        marginTop: 40,
                        fontSize: 13,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {doc.filename}
                    </div>

                    <div
                      style={{
                        marginTop: 7,
                        fontSize: 10,
                        color: "rgba(225,224,204,.35)",
                      }}
                    >
                      Document #{doc.id}
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
    </>
  );
}

/* =========================================================
   FEATURE CARD
========================================================= */

function FeatureCard({
  number,
  icon,
  title,
  description,
  children,
}: {
  number: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="hover-card"
      style={{
        background: "#101010",
        border: `1px solid ${border}`,
        borderRadius: 24,
        padding: 25,
        minHeight: 430,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 13,
            background: "#212121",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {icon}
        </div>

        <span
          style={{
            fontSize: 11,
            color: "rgba(225,224,204,.35)",
          }}
        >
          {number}
        </span>
      </div>

      <div style={{ marginTop: 45 }}>
        <h3
          style={{
            fontSize: 25,
            fontWeight: 400,
            margin: 0,
          }}
        >
          {title}
        </h3>

        <p
          style={{
            color: "rgba(225,224,204,.48)",
            fontSize: 12,
            lineHeight: 1.55,
            maxWidth: 300,
          }}
        >
          {description}
        </p>
      </div>

      <div style={{ marginTop: 30 }}>{children}</div>

      <div
        style={{
          position: "absolute",
          bottom: 20,
          right: 22,
          color: "rgba(225,224,204,.3)",
        }}
      >
        <ArrowUpRight size={17} />
      </div>
    </div>
  );
}

/* =========================================================
   AUTH MODAL
========================================================= */

function AuthModal({
  email,
  password,
  setEmail,
  setPassword,
  login,
  register,
  close,
}: any) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        background: "rgba(0,0,0,.75)",
        backdropFilter: "blur(15px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <motion.div
        initial={{ opacity: 0, scale: .95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: .45, ease }}
        style={{
          width: "100%",
          maxWidth: 430,
          background: "#101010",
          border: `1px solid ${border}`,
          borderRadius: 28,
          padding: 30,
          position: "relative",
        }}
      >
        <button
          onClick={close}
          style={{
            position: "absolute",
            right: 18,
            top: 18,
            background: "transparent",
            border: 0,
            color: "rgba(225,224,204,.5)",
            cursor: "pointer",
          }}
        >
          <X size={18} />
        </button>

        <div style={smallLabel}>NEXUS*</div>

        <h2
          style={{
            fontSize: 42,
            fontWeight: 400,
            letterSpacing: "-.06em",
            margin: "20px 0 8px",
          }}
        >
          Enter the
          <br />
          <span className="serif">workspace.</span>
        </h2>

        <p
          style={{
            color: "rgba(225,224,204,.4)",
            fontSize: 12,
            marginBottom: 25,
          }}
        >
          Login or create an account to continue.
        </p>

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={authInput}
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ ...authInput, marginTop: 9 }}
        />

        <button
          onClick={login}
          style={{
            ...primaryButton,
            width: "100%",
            justifyContent: "space-between",
            marginTop: 15,
          }}
        >
          Login
          <span style={buttonCircle}>
            <ArrowRight size={16} />
          </span>
        </button>

        <button
          onClick={register}
          style={{
            width: "100%",
            marginTop: 10,
            padding: "14px 18px",
            borderRadius: 999,
            background: "transparent",
            color: cream,
            border: `1px solid ${border}`,
            cursor: "pointer",
          }}
        >
          Create account
        </button>
      </motion.div>
    </motion.div>
  );
}

/* =========================================================
   STYLES
========================================================= */

const navLink: React.CSSProperties = {
  color: "rgba(225,224,204,.75)",
  textDecoration: "none",
  fontSize: 11,
  transition: "color .2s",
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

const sideTitle: React.CSSProperties = {
  marginTop: 35,
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

const miniSource: React.CSSProperties = {
  padding: 16,
  borderRadius: 16,
  background: "#212121",
  border: `1px solid ${border}`,
};

const miniConversation: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
};

const conversationRow: React.CSSProperties = {
  padding: "14px",
  background: "#212121",
  borderRadius: 12,
  border: `1px solid ${border}`,
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  fontSize: 11,
  color: "rgba(225,224,204,.7)",
};

createRoot(document.getElementById("root")!).render(<App />);