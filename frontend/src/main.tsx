import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";

// Backend API URL
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

  // -------------------------
  // REGISTER
  // -------------------------
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

  // -------------------------
  // LOGIN
  // -------------------------
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
    } else {
      alert(r.body.detail || "Login failed");
    }
  }

  // -------------------------
  // FETCH DOCUMENTS
  // -------------------------
  async function fetchDocs() {
    const r = await API("/documents/", {
      method: "GET",
      headers,
    });

    if (r.status === 200) {
      setDocs(r.body);
    } else {
      console.error("Failed to fetch documents:", r.body);
    }
  }

  // -------------------------
  // UPLOAD PDF
  // -------------------------
  async function upload() {
    if (!file) {
      alert("Please choose a PDF file");
      return;
    }

    const form = new FormData();
    form.append("file", file, file.name);

    const url = API_URL ? `${API_URL}/documents/upload` : "/documents/upload";

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
        alert("PDF uploaded successfully");
        setFile(null);
        fetchDocs();
      } else {
        console.error("Upload error:", body);
        alert(body.detail || "Upload failed");
      }
    } catch (error) {
      console.error("Upload request failed:", error);
      alert("Unable to connect to backend");
    }
  }

  // -------------------------
  // ASK RAG QUESTION
  // -------------------------
  async function ask(docId?: number) {
    const cleanQuery = query.trim();

    // Prevent empty query
    if (!cleanQuery) {
      alert("Please enter a question");
      return;
    }

    const payload: any = {
      query: cleanQuery,
      top_k: 5,
    };

    if (docId !== undefined) {
      payload.document_id = docId;
    }

    console.log("Sending chat request:", payload);

    const r = await API("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    console.log("Chat response:", r);

    if (r.status === 200) {
      setAnswer(r.body);
    } else {
      // Show actual backend error
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
  }

  // -------------------------
  // FETCH CONVERSATIONS
  // -------------------------
  async function fetchConvs() {
    const r = await API("/conversations", {
      method: "GET",
      headers,
    });

    if (r.status === 200) {
      setConvs(r.body);
    } else {
      console.error("Failed to fetch conversations:", r.body);
    }
  }

  // -------------------------
  // LOGOUT
  // -------------------------
  function logout() {
    localStorage.removeItem("token");
    setToken(null);

    setDocs([]);
    setConvs([]);
    setAnswer(null);
    setQuery("");
  }

  return (
    <div
      style={{
        fontFamily: "sans-serif",
        padding: 20,
      }}
    >
      {/* =========================
          LOGIN / REGISTER
      ========================== */}

      {!token && (
        <div>
          <h2>Login / Register</h2>

          <input
            placeholder="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <br />
          <br />

          <input
            placeholder="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <br />
          <br />

          <button onClick={login}>Login</button>

          <button onClick={register} style={{ marginLeft: 10 }}>
            Register
          </button>
        </div>
      )}

      {/* =========================
          DASHBOARD
      ========================== */}

      {token && (
        <div>
          <h2>Dashboard</h2>

          <button onClick={logout}>Logout</button>

          <hr />

          {/* =========================
              UPLOAD
          ========================== */}

          <h3>Upload PDF</h3>

          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          <button onClick={upload} style={{ marginLeft: 10 }}>
            Upload
          </button>

          {/* =========================
              DOCUMENTS
          ========================== */}

          <h3>Your Documents</h3>

          {docs.length === 0 ? (
            <p>No documents uploaded yet.</p>
          ) : (
            <ul>
              {docs.map((d) => (
                <li key={d.id}>
                  {d.filename} - User {d.user_id}
                </li>
              ))}
            </ul>
          )}

          <hr />

          {/* =========================
              RAG CHAT
          ========================== */}

          <h3>Ask a question</h3>

          <input
            style={{
              width: "60%",
              padding: 8,
            }}
            placeholder="Ask something about your documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                ask();
              }
            }}
          />

          <button onClick={() => ask()} style={{ marginLeft: 10 }}>
            Ask Global
          </button>

          {/* =========================
              ANSWER
          ========================== */}

          <div style={{ marginTop: 20 }}>
            <h4>Answer</h4>

            {answer ? (
              <div>
                <p>{answer.answer || "No answer returned."}</p>

                <h5>Sources</h5>

                <pre>{JSON.stringify(answer.sources || [], null, 2)}</pre>
              </div>
            ) : (
              <p>No question asked yet.</p>
            )}
          </div>

          <hr />

          {/* =========================
              CONVERSATIONS
          ========================== */}

          <h3>Conversations</h3>

          <button onClick={fetchConvs}>Refresh</button>

          {convs.length === 0 ? (
            <p>No conversations yet.</p>
          ) : (
            <ul>
              {convs.map((c) => (
                <li key={c.id}>
                  {c.title} ({c.id})
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
