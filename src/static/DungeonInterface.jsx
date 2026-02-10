import React, { useState, useEffect, useRef } from 'react';
import {
  Mic, Send, Shield, Heart, Backpack, Map as MapIcon,
  Scroll, Activity, Sword, Skull, Menu, Volume2,
  User, BookOpen, X, ChevronRight
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [activePanel, setActivePanel] = useState(null);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const [playerStats, setPlayerStats] = useState({
    hp: 20, maxHp: 20, ac: 15, name: "Kaelen"
  });

  const [logs, setLogs] = useState([]);
  const [currentScene, setCurrentScene] = useState({
    title: "Adventure Awaits", imageType: "default", description: "Start a session to begin."
  });

  const logEndRef = useRef(null);
  const audioRef = useRef(new Audio());

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  // Handle Audio Cues (Sound Effects)
  const playCues = (cues) => {
    cues.forEach(cue => {
      if (cue.type === 'sfx') {
        console.log(`Playing SFX: ${cue.resource_id}`);
        // In a real app, these would be real MP3 URLs
        // const sfx = new Audio(`/static/assets/audio/${cue.resource_id}`);
        // sfx.play();
      }
    });
  };

  const startSession = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_BASE}/session/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ campaign_type: "Dark Crypt" })
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setCurrentScene({ ...currentScene, description: data.intro_narrative });
      setLogs([{ type: 'dm', text: data.intro_narrative }]);
      setPlayerStats(prev => ({ ...prev, ...data.party_state }));
    } catch (err) {
      alert("Backend offline. Make sure server.py is running!");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    const text = input;
    setInput("");
    setLogs(prev => [...prev, { type: 'player', text }]);
    setIsProcessing(true);

    try {
      const res = await fetch(`${API_BASE}/interact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "u1", character_id: "c1", session_id: sessionId, input_text: text
        })
      });
      const data = await res.json();

      playCues(data.audio_cues);

      const newLogs = [];
      if (data.dice_roll) newLogs.push({ type: 'roll', ...data.dice_roll });
      newLogs.push({ type: 'dm', text: data.narrative });

      setLogs(prev => [...prev, ...newLogs]);
      setCurrentScene(prev => ({
        ...prev,
        description: data.narrative,
        imageType: data.visual_cue.prompt.includes("combat") ? "combat" : "default"
      }));

      if (data.state_update.hp_change) {
        setPlayerStats(prev => ({ ...prev, hp: prev.hp + data.state_update.hp_change }));
      }
    } catch (err) {
      setLogs(prev => [...prev, { type: 'system', text: "Connection error." }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-slate-200 font-sans overflow-hidden">
      <div className="w-16 bg-slate-900 border-r border-slate-800 flex flex-col items-center py-6 z-30">
        <button onClick={() => setActivePanel('hero')} className="p-3 text-slate-500 hover:text-white"><User /></button>
        <button onClick={() => setActivePanel('bag')} className="p-3 text-slate-500 hover:text-white"><Backpack /></button>
      </div>

      <div className="flex-1 flex flex-col min-w-0 bg-slate-950">
        <div className="h-14 border-b border-slate-800 flex items-center justify-between px-6">
           <span className="font-bold text-xs uppercase tracking-widest text-slate-400">
             {sessionId ? "SESSION ACTIVE" : "READY"}
           </span>
           <div className="flex items-center space-x-4">
              <Heart className="text-red-500" size={16} />
              <span className="text-sm font-bold">{playerStats.hp}/{playerStats.maxHp}</span>
           </div>
        </div>

        <div className="flex-1 relative bg-black flex flex-col items-center justify-center p-12">
            <div className={`absolute inset-0 opacity-20 ${currentScene.imageType === 'combat' ? 'bg-red-900' : 'bg-slate-900'}`}></div>
            {currentScene.imageType === 'combat' ? <Skull size={80} className="text-red-500 animate-pulse z-10" /> : <MapIcon size={80} className="text-slate-800 z-10" />}

            <div className="z-20 bg-slate-900/90 border border-slate-800 p-8 rounded-2xl max-w-2xl shadow-2xl mt-8">
               <p className="text-lg font-serif leading-relaxed text-slate-300 italic">
                 "{currentScene.description}"
               </p>
            </div>

            {!sessionId && (
              <button onClick={startSession} className="z-30 mt-8 px-8 py-3 bg-indigo-600 rounded-full font-bold hover:bg-indigo-500 shadow-xl shadow-indigo-900/20">
                START CAMPAIGN
              </button>
            )}
        </div>

        <div className="p-6 bg-slate-900 border-t border-slate-800">
          <div className="max-w-4xl mx-auto flex space-x-4">
            <input
              type="text"
              value={input}
              disabled={!sessionId || isProcessing}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="What do you do?"
              className="flex-1 bg-black border border-slate-700 rounded-lg px-4 py-3 text-white focus:border-indigo-500 outline-none"
            />
            <button onClick={handleSend} className="p-3 bg-indigo-600 rounded-lg"><Send size={20} /></button>
          </div>
        </div>
      </div>

      <div className="w-80 bg-slate-950 border-l border-slate-800 flex flex-col hidden lg:flex">
         <div className="p-3 border-b border-slate-800 text-[10px] font-bold text-slate-500 uppercase">Log</div>
         <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
           {logs.map((log, i) => (
             <div key={i} className={`flex flex-col ${log.type === 'player' ? 'items-end' : 'items-start'}`}>
                {log.type === 'roll' ? (
                  <div className="w-full bg-slate-900 border border-slate-800 p-2 rounded text-center my-2">
                    <div className="text-[10px] text-slate-500">{log.label}</div>
                    <div className="text-lg font-bold text-white">{log.val}</div>
                  </div>
                ) : (
                  <div className={`p-3 rounded-lg ${log.type === 'player' ? 'bg-indigo-900/30 text-indigo-200' : 'text-slate-400'}`}>
                    {log.text}
                  </div>
                )}
             </div>
           ))}
           <div ref={logEndRef} />
         </div>
      </div>
    </div>
  );
}