import React, { useState } from 'react';
import './index.css';

export default function App() {
  // Thoughts (left panel)
  const [thoughts, setThoughts] = useState([]);
  const [newThought, setNewThought] = useState('');

  // Chat / Notebook (center)
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Projects / Todos (right)
  const [projects, setProjects] = useState([]);
  const [newProject, setNewProject] = useState('');
  const [newTodo, setNewTodo] = useState('');
  const [toolsOpen, setToolsOpen] = useState(false);
  const [savingThought, setSavingThought] = useState(false);
  const [thoughtError, setThoughtError] = useState('');

  async function saveThought() {
    if (!newThought.trim()) return;
    const item = { text: newThought.trim(), created_at: Date.now() };
    // Optimistic UI update (matches orbcore -> brain.log_stream behavior)
    setThoughts((s) => [item, ...s]);
    setNewThought('');
    setThoughtError('');
    setSavingThought(true);

    try {
      const res = await fetch('http://localhost:8000/thoughts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: item.text }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.status || `HTTP ${res.status}`);
      }

      // If backend reports no brain configured, leave local only.
      if (data?.status === 'no-brain-configured') {
        // optional: inform user that thought is only local
        setThoughtError('Saved locally (backend not configured).');
      }
    } catch (e) {
      // on error, keep the optimistic UI but show error
      setThoughtError(String(e));
    } finally {
      setSavingThought(false);
    }
  }

  function addProject() {
    if (!newProject.trim()) return;
    setProjects((p) => [{ name: newProject.trim(), todos: [] }, ...p]);
    setNewProject('');
  }

  function addTodoToProject(idx) {
    if (!newTodo.trim()) return;
    setProjects((p) => {
      const copy = JSON.parse(JSON.stringify(p));
      copy[idx].todos.push({ text: newTodo.trim(), done: false });
      return copy;
    });
    setNewTodo('');
  }

  async function handleSend() {
    if (!input.trim()) return;
    const user = { role: 'user', content: input };
    setMessages((m) => [...m, user]);
    setInput('');
    setIsTyping(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: 'assistant', content: data.reply || data.message || 'No reply' }]);
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: 'Error: Kernel unreachable.' }]);
    } finally { setIsTyping(false); }
  }

  return (
    <div className="notebook-root">
      <div className="panel panel-left">
        <div className="tools">
          <div className="tools-header">
            <strong>Tools</strong>
            <button className="tools-toggle" onClick={() => setToolsOpen(!toolsOpen)} aria-expanded={toolsOpen}>
              {toolsOpen ? '▾' : '▸'}
            </button>
          </div>
          <div className={`tools-ribbon ${toolsOpen ? 'open' : 'closed'}`}>
            <button className="tool-btn">Command Palette</button>
            <button className="tool-btn">Quick Search</button>
            <button className="tool-btn">Vision</button>
            <button className="tool-btn">Ingest</button>
          </div>
        </div>
        <h3>Thoughts</h3>
        <textarea value={newThought} onChange={(e) => setNewThought(e.target.value)} placeholder="Write a quick thought..." />
        <button className="btn" onClick={saveThought}>Save Thought</button>
        <div className="list">
          {thoughts.map((t, i) => (
            <div className="thought" key={i}>
              <div className="meta">{new Date(t.created_at).toLocaleString()}</div>
              <div>{t.text}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel panel-center">
        <h3>LLM Notebook</h3>
        <div className="chat">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="role">{m.role}</div>
              <div className="content">{m.content}</div>
            </div>
          ))}
          {isTyping && <div className="msg assistant">Kernel Processing...</div>}
        </div>
        <div className="chat-input">
          <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} placeholder="Ask the kernel or add a notebook prompt..." />
          <button className="btn" onClick={handleSend}>Send</button>
        </div>
      </div>

      <div className="panel panel-right">
        <h3>Projects & Todos</h3>
        <div className="new-row">
          <input value={newProject} onChange={(e) => setNewProject(e.target.value)} placeholder="New project name" />
          <button className="btn" onClick={addProject}>Add</button>
        </div>
        <div className="projects">
          {projects.map((p, idx) => (
            <div className="project" key={idx}>
              <div className="project-name">{p.name}</div>
              <div className="todos">
                {p.todos.map((t, j) => (
                  <label key={j} className="todo"><input type="checkbox" checked={t.done} readOnly /> {t.text}</label>
                ))}
              </div>
              <div className="new-todo">
                <input value={newTodo} onChange={(e) => setNewTodo(e.target.value)} placeholder="New todo for project" />
                <button className="btn" onClick={() => addTodoToProject(idx)}>Add</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
