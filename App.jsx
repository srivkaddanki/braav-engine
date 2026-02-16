import React, { useState } from 'react';
import { Settings, BookOpen, CheckSquare, Zap, Terminal } from 'lucide-react';

export default function OrbCommandCenter() {
  const [showThoughtLog, setShowThoughtLog] = useState(false);
  
  // --- STEP 3: THE NERVOUS SYSTEM (STATE) ---
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // --- STEP 3: THE MESSENGER (LOGIC) ---
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      console.error("Brain connection lost:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Kernel unreachable. Is bridge_api.py running?" }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#09090b] text-zinc-100 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR: CORTEX (Notes) */}
      <aside className="w-1/5 border-r border-zinc-800 flex flex-col bg-zinc-950/50">
        <div className="p-4 border-b border-zinc-800 flex items-center gap-2">
          <BookOpen size={16} className="text-blue-400" />
          <span className="text-xs font-bold uppercase tracking-widest text-zinc-500">Cortex Notes</span>
        </div>
        <textarea 
          className="flex-1 p-4 bg-transparent resize-none focus:outline-none text-sm leading-relaxed"
          placeholder="Log what you learn..."
        />
        <div className="p-4 border-t border-zinc-800">
          <button className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 rounded text-xs font-medium transition-colors">
            SAVE TO VOID
          </button>
        </div>
      </aside>

      {/* CENTER: THE AGENTIC BRAIN (Chat) */}
      <main className="flex-1 flex flex-col relative bg-[#09090b]">
        {/* Header */}
        <header className="h-14 border-b border-zinc-800 flex justify-between items-center px-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-sm font-mono tracking-tighter">ORB_KERNEL_V1</span>
          </div>
          <button 
            onClick={() => setShowThoughtLog(!showThoughtLog)}
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold transition-all ${
              showThoughtLog ? 'bg-blue-500/10 text-blue-400 border border-blue-500/50' : 'bg-zinc-800 text-zinc-500 border border-transparent'
            }`}
          >
            <Terminal size={12} />
            THOUGHT_LOGGER: {showThoughtLog ? 'ACTIVE' : 'OFF'}
          </button>
        </header>

        {/* Chat Feed */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-sm text-zinc-400 leading-relaxed italic border-l-2 border-zinc-800 pl-4">
              "Structural Chaos detected. Loading 75-day longitudinal context..."
            </div>
            
            {/* --- RENDERING MESSAGES --- */}
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <span className="text-[10px] uppercase text-zinc-500 mb-1">{msg.role}</span>
                <div className={`p-4 rounded-2xl max-w-[80%] text-sm ${
                  msg.role === 'user' 
                  ? 'bg-blue-600/10 text-blue-100 border border-blue-500/20' 
                  : 'bg-zinc-900 text-zinc-100 border border-zinc-800'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="text-[10px] text-blue-400 animate-pulse uppercase font-bold tracking-widest">
                Kernel Processing...
              </div>
            )}
          </div>
        </div>

        {/* Input Section */}
        <div className="p-6">
          <div className="max-w-2xl mx-auto relative">
            <input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="w-full bg-zinc-900 border border-zinc-800 p-4 pr-12 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm"
              placeholder="Query the kernel..."
            />
            <Zap 
              onClick={handleSend}
              size={16} 
              className={`absolute right-4 top-4 cursor-pointer transition-colors ${input.trim() ? 'text-blue-400' : 'text-zinc-500'}`} 
            />
          </div>
        </div>
      </main>

      {/* RIGHT SIDEBAR: IDENTITY & OPS */}
      <aside className="w-1/5 border-l border-zinc-800 flex flex-col bg-zinc-950/50">
        <div className="p-4 border-b border-zinc-800 flex items-center gap-2">
          <CheckSquare size={16} className="text-blue-400" />
          <span className="text-xs font-bold uppercase tracking-widest text-zinc-500">Identity Ops</span>
        </div>
        
        <div className="p-4 space-y-6 overflow-y-auto">
          <section>
            <h4 className="text-[10px] text-zinc-500 font-bold mb-3 uppercase">Active Projects</h4>
            <div className="space-y-2">
              <div className="text-xs p-2 bg-zinc-900 rounded border border-zinc-800">
                <div className="flex justify-between mb-1">
                  <span>UTSA Research</span>
                  <span className="text-blue-400">65%</span>
                </div>
                <div className="w-full h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full w-[65%]" />
                </div>
              </div>
            </div>
          </section>

          <section>
            <h4 className="text-[10px] text-zinc-500 font-bold mb-3 uppercase">Dynamic To-Do</h4>
            <ul className="text-xs space-y-3">
              <li className="flex items-center gap-2 text-zinc-400">
                <input type="checkbox" className="w-3 h-3 bg-zinc-900 border-zinc-700 rounded" />
                Audit 75-day Vision Logs
              </li>
            </ul>
          </section>
        </div>
      </aside>
    </div>
  );
}