// frontend/src/App.jsx
import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;


function App() {
  const [page, setPage] = useState("auth"); // 'auth' | 'dashboard' | 'project' | 'editor'
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);

  const [authForm, setAuthForm] = useState({
    email: "",
    password: "",
    full_name: "",
  });

  const [projects, setProjects] = useState([]);
  const [projectForm, setProjectForm] = useState({
    title: "",
    topic: "",
    doc_type: "docx",
    sections: [{ title: "Introduction", order: 1 }],
  });

  const [currentProject, setCurrentProject] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refinePrompt, setRefinePrompt] = useState({}); // sectionId -> string
  const [commentText, setCommentText] = useState({}); // sectionId -> string

  // ---- Helper: API call with Authorization header ----
  async function apiFetch(path, options = {}) {
    const headers = options.headers || {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `Request failed: ${res.status}`);
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return res.json();
    }
    return res;
  }

  // ---- On startup: if token exists, load user & projects ----
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const me = await apiFetch("/auth/me");
        setUser(me);
        const list = await apiFetch("/projects");
        setProjects(list);
        setPage("dashboard");
      } catch (e) {
        console.error(e);
        localStorage.removeItem("token");
        setToken("");
        setUser(null);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---- AUTH HANDLERS ----

  async function handleRegister() {
    try {
      setIsLoading(true);
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: authForm.email,
          password: authForm.password,
          full_name: authForm.full_name,
        }),
      });
      alert("Registered! Now log in.");
      setMode("login");
    } catch (e) {
      alert("Register error: " + e.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleLogin() {
    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append("username", authForm.email);
      formData.append("password", authForm.password);

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem("token", data.access_token);

      const me = await apiFetch("/auth/me");
      setUser(me);
      const list = await apiFetch("/projects");
      setProjects(list);
      setPage("dashboard");
    } catch (e) {
      alert("Login error: " + e.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    setToken("");
    localStorage.removeItem("token");
    setUser(null);
    setProjects([]);
    setCurrentProject(null);
    setPage("auth");
  }

  // ---- PROJECT HANDLERS ----

  function addSectionRow() {
    setProjectForm((prev) => ({
      ...prev,
      sections: [
        ...prev.sections,
        { title: `Section ${prev.sections.length + 1}`, order: prev.sections.length + 1 },
      ],
    }));
  }

  function updateSectionRow(index, field, value) {
    setProjectForm((prev) => {
      const newSecs = [...prev.sections];
      newSecs[index] = { ...newSecs[index], [field]: value };
      return { ...prev, sections: newSecs };
    });
  }

  async function handleCreateProject() {
    try {
      setIsLoading(true);
      const body = {
        title: projectForm.title,
        topic: projectForm.topic,
        doc_type: projectForm.doc_type,
        sections: projectForm.sections.map((s, idx) => ({
          title: s.title,
          order: idx + 1,
        })),
      };

      const proj = await apiFetch("/projects", {
        method: "POST",
        body: JSON.stringify(body),
      });

      setProjects((prev) => [...prev, proj]);
      setCurrentProject(proj);
      setPage("editor");

      // Immediately generate AI content
      const gen = await apiFetch(`/projects/${proj.id}/generate`, {
        method: "POST",
      });
      setCurrentProject(gen);
      alert("Initial AI content generated!");
    } catch (e) {
      alert("Create project error: " + e.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function openProject(projectId) {
    try {
      setIsLoading(true);
      const proj = await apiFetch(`/projects/${projectId}`);
      setCurrentProject(proj);
      setPage("editor");
    } catch (e) {
      alert("Open project error: " + e.message);
    } finally {
      setIsLoading(false);
    }
  }


  async function handleDeleteProject(projectId) {
  const confirmDelete = window.confirm("Are you sure you want to delete this project?");
  if (!confirmDelete) return;

  try {
    setIsLoading(true);

    await apiFetch(`/projects/${projectId}`, {
      method: "DELETE",
    });

    // Update UI instantly
    setProjects((prev) => prev.filter((p) => p.id !== projectId));

    // If currently viewing deleted project, go back to dashboard
    if (currentProject && currentProject.id === projectId) {
      setCurrentProject(null);
      setPage("dashboard");
    }

    alert("Project deleted successfully!");
  } catch (e) {
    alert("Delete error: " + e.message);
  } finally {
    setIsLoading(false);
  }
}

  // ---- REFINEMENT HANDLERS ----

  async function handleRefine(section) {
    const prompt = refinePrompt[section.id] || "";
    if (!prompt.trim()) {
      alert("Enter a refinement prompt.");
      return;
    }
    try {
      setIsLoading(true);
      const updatedSection = await apiFetch(`/sections/${section.id}/refine`, {
        method: "POST",
        body: JSON.stringify({ prompt }),
      });
      setCurrentProject((prev) => ({
        ...prev,
        sections: prev.sections.map((s) =>
          s.id === section.id ? updatedSection : s
        ),
      }));
      alert("Section refined.");
    } catch (e) {
      alert("Refine error: " + e.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFeedback(section, liked) {
    try {
      await apiFetch(`/sections/${section.id}/feedback`, {
        method: "POST",
        body: JSON.stringify({ liked }),
      });
      alert("Feedback saved.");
    } catch (e) {
      alert("Feedback error: " + e.message);
    }
  }

  async function handleComment(section) {
    const text = commentText[section.id] || "";
    if (!text.trim()) {
      alert("Enter a comment.");
      return;
    }
    try {
      await apiFetch(`/sections/${section.id}/comment`, {
        method: "POST",
        body: JSON.stringify({ text }),
      });
      alert("Comment added.");
      setCommentText((prev) => ({ ...prev, [section.id]: "" }));
    } catch (e) {
      alert("Comment error: " + e.message);
    }
  }

  // ---- EXPORT HANDLERS ----

  async function handleExport(format) {
    if (!currentProject) return;
    const projectId = currentProject.id;
    const path =
      format === "docx"
        ? `/projects/${projectId}/export/docx`
        : `/projects/${projectId}/export/pptx`;

    try {
      const res = await apiFetch(path, { method: "GET" });
      // res here is a Response object (not JSON)
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${currentProject.title}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert("Export error: " + e.message);
    }
  }

  // ---- UI RENDER HELPERS ----

  function renderAuth() {
    return (
      <div className="card">
        <h2>{mode === "login" ? "Login" : "Register"}</h2>

        <label>
          Email
          <input
            type="email"
            value={authForm.email}
            onChange={(e) =>
              setAuthForm((f) => ({ ...f, email: e.target.value }))
            }
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={authForm.password}
            onChange={(e) =>
              setAuthForm((f) => ({ ...f, password: e.target.value }))
            }
          />
        </label>

        {mode === "register" && (
          <label>
            Full Name
            <input
              type="text"
              value={authForm.full_name}
              onChange={(e) =>
                setAuthForm((f) => ({ ...f, full_name: e.target.value }))
              }
            />
          </label>
        )}

        {mode === "login" ? (
          <button onClick={handleLogin} disabled={isLoading}>
            Login
          </button>
        ) : (
          <button onClick={handleRegister} disabled={isLoading}>
            Register
          </button>
        )}

        <p>
          {mode === "login" ? "No account?" : "Already have an account?"}{" "}
          <button
            type="button"
            className="secondary small"
            onClick={() =>
              setMode((m) => (m === "login" ? "register" : "login"))
            }
          >
            {mode === "login" ? "Register" : "Login"}
          </button>
        </p>
      </div>
    );
  }

  function renderDashboard() {
    return (
      <>
        <div className="card">
          <h2>Your Projects</h2>
          {projects.length === 0 && <p>No projects yet.</p>}
          {projects.map((p) => (
            <div key={p.id} className="section-box">
              <strong>{p.title}</strong> ({p.doc_type})<br />
              <small>{p.topic}</small>
              <br />
              <button
                className="small"
                style={{ marginTop: "0.5rem" }}
                onClick={() => openProject(p.id)}
              >
                Open
              </button>
              <button
  className="small"
  style={{ marginTop: "0.5rem", marginLeft: "0.5rem", backgroundColor: "red", color: "white" }}
  onClick={() => handleDeleteProject(p.id)}
>
  Delete
</button>

            </div>
          ))}
        </div>

        <div className="card">
          <h2>Create New Project</h2>
          <label>
            Title
            <input
              value={projectForm.title}
              onChange={(e) =>
                setProjectForm((f) => ({ ...f, title: e.target.value }))
              }
            />
          </label>

          <label>
            Topic / Main Prompt
            <textarea
              rows={3}
              value={projectForm.topic}
              onChange={(e) =>
                setProjectForm((f) => ({ ...f, topic: e.target.value }))
              }
            />
          </label>

          <label>
            Document Type
            <select
              value={projectForm.doc_type}
              onChange={(e) =>
                setProjectForm((f) => ({ ...f, doc_type: e.target.value }))
              }
            >
              <option value="docx">Word (.docx)</option>
              <option value="pptx">PowerPoint (.pptx)</option>
            </select>
          </label>

          <h3>
            {projectForm.doc_type === "docx"
              ? "Section Headers (Outline)"
              : "Slide Titles"}
          </h3>

          {projectForm.sections.map((s, idx) => (
            <div key={idx} className="section-box">
              <label>
                Title
                <input
                  value={s.title}
                  onChange={(e) => updateSectionRow(idx, "title", e.target.value)}
                />
              </label>
            </div>
          ))}

          <button
            type="button"
            className="secondary small"
            onClick={addSectionRow}
            style={{ marginBottom: "1rem" }}
          >
            + Add Section/Slide
          </button>

          <br />
          <button onClick={handleCreateProject} disabled={isLoading}>
            Create & Generate AI Content
          </button>
        </div>
      </>
    );
  }

  function renderEditor() {
    if (!currentProject) return null;
    return (
      <div className="card">
        <h2>Editing: {currentProject.title}</h2>
        <p>
          Type: <strong>{currentProject.doc_type}</strong> | Topic:{" "}
          <em>{currentProject.topic}</em>
        </p>
        <button
          type="button"
          className="secondary small"
          onClick={() => setPage("dashboard")}
          style={{ marginBottom: "1rem" }}
        >
          ← Back to Dashboard
        </button>

        <div style={{ marginBottom: "1rem" }}>
          {currentProject.doc_type === "docx" && (
            <button
              type="button"
              onClick={() => handleExport("docx")}
              style={{ marginRight: "0.5rem" }}
            >
              Export .docx
            </button>
          )}
          {currentProject.doc_type === "pptx" && (
            <button type="button" onClick={() => handleExport("pptx")}>
              Export .pptx
            </button>
          )}
        </div>

        <h3>Sections / Slides</h3>
        {currentProject.sections.map((s) => (
          <div key={s.id} className="section-box">
            <h4>
              #{s.order} - {s.title}
            </h4>
            <label>
              Content
              <textarea
                rows={6}
                value={s.content || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setCurrentProject((prev) => ({
                    ...prev,
                    sections: prev.sections.map((sec) =>
                      sec.id === s.id ? { ...sec, content: value } : sec
                    ),
                  }));
                }}
              />
            </label>

            <label>
              AI Refinement Prompt
              <input
                placeholder="e.g. Make this more formal, shorten to 100 words..."
                value={refinePrompt[s.id] || ""}
                onChange={(e) =>
                  setRefinePrompt((prev) => ({
                    ...prev,
                    [s.id]: e.target.value,
                  }))
                }
              />
            </label>
            <button
              type="button"
              className="small"
              onClick={() => handleRefine(s)}
              disabled={isLoading}
            >
              Refine with AI
            </button>

            <div style={{ marginTop: "0.5rem" }}>
              <span>Feedback: </span>
              <button
                type="button"
                className="small"
                onClick={() => handleFeedback(s, true)}
              >
                👍 Like
              </button>
              <button
                type="button"
                className="small"
                onClick={() => handleFeedback(s, false)}
              >
                👎 Dislike
              </button>
            </div>

            <div style={{ marginTop: "0.5rem" }}>
              <label>
                Comment
                <textarea
                  rows={2}
                  placeholder="Your notes about this section..."
                  value={commentText[s.id] || ""}
                  onChange={(e) =>
                    setCommentText((prev) => ({
                      ...prev,
                      [s.id]: e.target.value,
                    }))
                  }
                />
              </label>
              <button
                type="button"
                className="small"
                onClick={() => handleComment(s)}
              >
                Save Comment
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // ---- MAIN RENDER ----
  return (
    <div className="app-container">
      <div className="navbar">
        <div className="navbar-title">AI Doc Generator</div>
        <div>
          {user && (
            <>
              <span style={{ marginRight: "1rem" }}>
                {user.full_name || user.email}
              </span>
              <button className="secondary small" onClick={handleLogout}>
                Logout
              </button>
            </>
          )}
        </div>
      </div>

      {page === "auth" && renderAuth()}
      {page === "dashboard" && renderDashboard()}
      {page === "editor" && renderEditor()}

      {isLoading && <p>Loading...</p>}
    </div>
  );
}

export default App;
