# app.py
import os
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any

# Ensure environmental variables are loaded
from dotenv import load_dotenv
load_dotenv()

from graph.main_graph import compiled_main_graph, memory_store
from graph.auto_graph import compiled_auto_graph
from storage_utils import load_state, save_state, get_default_state
from scripts.run_midnight_loop import run_smart_scheduler

app = FastAPI(
    title="Co-Founder Memory Cockpit",
    description="A deployment-ready web service and control center for Co-Founder Memory.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str

# Startup background scheduler
@app.on_event("startup")
def start_scheduler():
    if os.getenv("RUN_BACKGROUND_SCHEDULER", "true").lower() == "true":
        print("🚀 Web Cockpit: Launching background scheduler daemon...")
        thread = threading.Thread(target=run_smart_scheduler, daemon=True)
        thread.start()

@app.get("/api/state")
def get_state():
    try:
        return load_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile")
def get_profile():
    try:
        namespace = ("memory", "profile")
        key = "co_founder_profile"
        profile_item = memory_store.get(namespace, key)
        if profile_item and profile_item.value:
            return profile_item.value
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def run_chat(req: ChatRequest):
    try:
        state = load_state()
        state["user_query"] = req.message
        
        # Invoke Main Graph
        result = compiled_main_graph.invoke(state)
        
        # Extract updates
        updated_state = {
            "temporary_memory": result.get("temporary_memory", state.get("temporary_memory", [])),
            "chunk_memory": result.get("chunk_memory", state.get("chunk_memory", [])),
            "extracted_memories": result.get("extracted_memories", state.get("extracted_memories", [])),
            "retrieved_context": result.get("retrieved_context", state.get("retrieved_context", [])),
            "final_response": result.get("final_response", "")
        }
        
        # Sync state
        state.update(updated_state)
        save_state(state)
        
        return {
            "response": state["final_response"],
            "state": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auto-run")
def force_auto_run():
    try:
        print("🌙 API Triggered: Running automated daily loop...")
        state = load_state()
        
        # Invoke Auto Graph
        result = compiled_auto_graph.invoke(state)
        
        if result:
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if "date_memory" not in result:
                result["date_memory"] = {}
            result["date_memory"][today_str] = "Completed"
            
            save_state(result)
            return {
                "dossier": result.get("final_response"),
                "state": result
            }
        raise HTTPException(status_code=500, detail="Automated graph returned empty results.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
def reset_state():
    try:
        default_state = get_default_state()
        save_state(default_state)
        return {"message": "System state reset successful.", "state": default_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    # Premium UI Cockpit in Dark Mode with Glassmorphism and responsive design
    supabase_configured = "true" if (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")) else "false"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Co-Founder Memory | Cockpit</title>
        <meta name="description" content="AI Companion memory dashboard and real-time controller.">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            :root {{
                --bg-primary: #0a0b10;
                --bg-card: rgba(20, 22, 34, 0.6);
                --bg-card-hover: rgba(30, 33, 50, 0.7);
                --border-color: rgba(255, 255, 255, 0.08);
                --accent-primary: #8a7dfa;
                --accent-primary-glow: rgba(138, 125, 250, 0.4);
                --accent-emerald: #10b981;
                --accent-emerald-glow: rgba(16, 185, 129, 0.4);
                --text-primary: #f3f4f6;
                --text-secondary: #9ca3af;
                --text-muted: #6b7280;
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Outfit', sans-serif;
            }}

            body {{
                background-color: var(--bg-primary);
                color: var(--text-primary);
                overflow-x: hidden;
                background-image: 
                    radial-gradient(at 0% 0%, rgba(138, 125, 250, 0.08) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
                background-attachment: fixed;
                min-height: 100vh;
            }}

            .cockpit-container {{
                display: flex;
                min-height: 100vh;
                position: relative;
            }}

            /* Sidebar */
            .sidebar {{
                width: 280px;
                background: rgba(10, 11, 16, 0.85);
                border-right: 1px solid var(--border-color);
                backdrop-filter: blur(16px);
                padding: 2.5rem 1.5rem;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                position: fixed;
                height: 100vh;
                z-index: 10;
            }}

            .logo-area {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 3rem;
            }}

            .logo-circle {{
                width: 40px;
                height: 40px;
                border-radius: 12px;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-emerald));
                box-shadow: 0 4px 15px var(--accent-primary-glow);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 700;
                font-size: 1.25rem;
            }}

            .logo-text h1 {{
                font-size: 1.2rem;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 700;
                letter-spacing: -0.02em;
            }}

            .logo-text p {{
                font-size: 0.75rem;
                color: var(--text-muted);
            }}

            .nav-menu {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                flex-grow: 1;
            }}

            .nav-item {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                border-radius: 10px;
                color: var(--text-secondary);
                text-decoration: none;
                font-size: 0.95rem;
                font-weight: 500;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
            }}

            .nav-item:hover, .nav-item.active {{
                color: var(--text-primary);
                background: rgba(255, 255, 255, 0.05);
            }}

            .nav-item.active {{
                border-left: 3px solid var(--accent-primary);
                background: rgba(138, 125, 250, 0.08);
            }}

            .status-panel {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 1rem;
                margin-top: auto;
            }}

            .status-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 0.85rem;
                margin-bottom: 8px;
            }}

            .status-row:last-child {{
                margin-bottom: 0;
            }}

            .status-indicator {{
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }}

            .status-green {{
                background-color: var(--accent-emerald);
                box-shadow: 0 0 8px var(--accent-emerald-glow);
            }}

            .status-gray {{
                background-color: var(--text-muted);
            }}

            /* Main Content */
            .main-content {{
                margin-left: 280px;
                padding: 2.5rem 3rem;
                width: calc(100% - 280px);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}

            header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 3rem;
            }}

            header h2 {{
                font-size: 1.75rem;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 700;
            }}

            /* Tab Content Views */
            .tab-view {{
                display: none;
                flex-direction: column;
                gap: 2rem;
                animation: fadeIn 0.4s ease-out;
            }}

            .tab-view.active {{
                display: flex;
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            /* Grid Layouts */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1.5rem;
            }}

            .card {{
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 1.5rem;
                backdrop-filter: blur(12px);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}

            .card:hover {{
                background: var(--bg-card-hover);
                border-color: rgba(255, 255, 255, 0.12);
                transform: translateY(-2px);
            }}

            .stat-card h4 {{
                font-size: 0.85rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }}

            .stat-card .value {{
                font-size: 2rem;
                font-weight: 700;
                font-family: 'Space Grotesk', sans-serif;
            }}

            .section-title {{
                font-size: 1.25rem;
                font-weight: 600;
                font-family: 'Space Grotesk', sans-serif;
                margin-bottom: 1.25rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            /* Profile grid */
            .profile-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1.5rem;
            }}

            .full-width {{
                grid-column: span 2;
            }}

            .profile-list {{
                list-style: none;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .profile-list li {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.04);
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 0.95rem;
                line-height: 1.4;
            }}

            .tag-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}

            .tag {{
                background: rgba(138, 125, 250, 0.12);
                border: 1px solid rgba(138, 125, 250, 0.25);
                color: #b4aeff;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 0.85rem;
                font-weight: 500;
            }}

            /* Chat Interface */
            .chat-container {{
                display: flex;
                flex-direction: column;
                height: 580px;
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 20px;
                overflow: hidden;
            }}

            .chat-messages {{
                flex-grow: 1;
                padding: 1.5rem;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 1.25rem;
            }}

            .message-bubble {{
                max-width: 80%;
                padding: 14px 18px;
                border-radius: 16px;
                font-size: 0.95rem;
                line-height: 1.5;
            }}

            .message-bubble.user {{
                background: var(--accent-primary);
                color: white;
                align-self: flex-end;
                border-bottom-right-radius: 4px;
                box-shadow: 0 4px 15px rgba(138, 125, 250, 0.2);
            }}

            .message-bubble.ai {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--border-color);
                align-self: flex-start;
                border-bottom-left-radius: 4px;
            }}

            .chat-input-area {{
                padding: 1.25rem;
                background: rgba(10, 11, 16, 0.5);
                border-top: 1px solid var(--border-color);
                display: flex;
                gap: 12px;
            }}

            .chat-input {{
                flex-grow: 1;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 14px 18px;
                color: var(--text-primary);
                font-size: 0.95rem;
                outline: none;
                transition: all 0.3s;
            }}

            .chat-input:focus {{
                border-color: var(--accent-primary);
                box-shadow: 0 0 10px rgba(138, 125, 250, 0.15);
            }}

            button {{
                background: linear-gradient(135deg, var(--accent-primary), rgba(138, 125, 250, 0.8));
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            button:hover {{
                box-shadow: 0 4px 15px var(--accent-primary-glow);
                transform: translateY(-1px);
            }}

            button.secondary {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid var(--border-color);
                color: var(--text-primary);
            }}

            button.secondary:hover {{
                background: rgba(255, 255, 255, 0.08);
                box-shadow: none;
            }}

            /* Markdown rendering */
            .dossier-view {{
                background: rgba(10, 11, 16, 0.4);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 2.5rem;
                line-height: 1.6;
                overflow-y: auto;
                max-height: 700px;
                font-size: 1rem;
            }}

            .dossier-view h1, .dossier-view h2, .dossier-view h3 {{
                font-family: 'Space Grotesk', sans-serif;
                margin-top: 1.5rem;
                margin-bottom: 1rem;
                font-weight: 700;
            }}

            .dossier-view h1 {{ font-size: 1.75rem; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }}
            .dossier-view h2 {{ font-size: 1.4rem; }}
            .dossier-view h3 {{ font-size: 1.15rem; }}
            
            .dossier-view p {{ margin-bottom: 1.25rem; color: #d1d5db; }}
            .dossier-view ul, .dossier-view ol {{ margin-left: 1.5rem; margin-bottom: 1.25rem; }}
            .dossier-view li {{ margin-bottom: 6px; color: #d1d5db; }}
            
            .dossier-view blockquote {{
                border-left: 4px solid var(--accent-primary);
                padding-left: 1.25rem;
                margin: 1.5rem 0;
                font-style: italic;
                color: #9ca3af;
            }}

            .dossier-view code {{
                background: rgba(255, 255, 255, 0.06);
                padding: 3px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.9rem;
            }}
            
            /* Responsive Utilities */
            @media (max-width: 968px) {{
                .cockpit-container {{
                    flex-direction: column;
                }}
                .sidebar {{
                    width: 100%;
                    height: auto;
                    position: relative;
                    padding: 1.5rem;
                }}
                .main-content {{
                    margin-left: 0;
                    width: 100%;
                    padding: 1.5rem;
                }}
                .profile-grid {{
                    grid-template-columns: 1fr;
                }}
                .full-width {{
                    grid-column: span 1;
                }}
            }}
            
            /* Loading Spinner */
            .spinner {{
                border: 3px solid rgba(255,255,255,0.1);
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border-left-color: white;
                animation: spin 1s linear infinite;
                display: none;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="cockpit-container">
            <!-- Sidebar Navigation -->
            <div class="sidebar">
                <div>
                    <div class="logo-area">
                        <div class="logo-circle">Ω</div>
                        <div class="logo-text">
                            <h1>Co-Founder</h1>
                            <p>Memory Engine v2</p>
                        </div>
                    </div>
                    <div class="nav-menu">
                        <div class="nav-item active" onclick="switchTab('dashboard', this)">Dashboard</div>
                        <div class="nav-item" onclick="switchTab('chat', this)">Co-Founder Chat</div>
                        <div class="nav-item" onclick="switchTab('profile', this)">Permanent Memory</div>
                        <div class="nav-item" onclick="switchTab('dossier', this)">Dossier Loop</div>
                    </div>
                </div>

                <div class="status-panel">
                    <div class="status-row">
                        <span>Supabase DB</span>
                        <span class="status-indicator {'status-green' if supabase_configured == 'true' else 'status-gray'}"></span>
                    </div>
                    <div class="status-row">
                        <span>Auto Daemon</span>
                        <span class="status-indicator status-green"></span>
                    </div>
                </div>
            </div>

            <!-- Main Interactive Display -->
            <div class="main-content">
                <header>
                    <h2 id="view-title">System Dashboard</h2>
                    <button class="secondary" onclick="resetSystem()">Reset State</button>
                </header>

                <!-- 1. DASHBOARD VIEW -->
                <div id="view-dashboard" class="tab-view active">
                    <div class="stats-grid">
                        <div class="card stat-card">
                            <h4>Session Messages</h4>
                            <div id="stat-messages" class="value">0</div>
                        </div>
                        <div class="card stat-card">
                            <h4>Extracted Facts</h4>
                            <div id="stat-facts" class="value">0</div>
                        </div>
                        <div class="card stat-card">
                            <h4>Tracked Timeline Runs</h4>
                            <div id="stat-timelines" class="value">0</div>
                        </div>
                    </div>

                    <div class="card">
                        <h3 class="section-title">Operational Summary</h3>
                        <p id="dashboard-summary" style="color: var(--text-secondary); line-height: 1.6;">
                            No daily catchups processed yet. Go to the "Dossier Loop" section to force trigger today's timeline summary compilation.
                        </p>
                    </div>
                </div>

                <!-- 2. CO-FOUNDER CHAT VIEW -->
                <div id="view-chat" class="tab-view">
                    <div class="chat-container">
                        <div id="chat-box" class="chat-messages">
                            <div class="message-bubble ai">
                                Hello, builder. I'm connected to your developer profile store and local workspace context. How can I help you organize your next steps today?
                            </div>
                        </div>
                        <div class="chat-input-area">
                            <input type="text" id="chat-input-field" class="chat-input" placeholder="Ask about past projects, stack rules, or add new milestones..." onkeypress="handleChatEnter(event)">
                            <button onclick="sendChatMessage()">
                                <span>Send</span>
                                <div id="chat-spinner" class="spinner"></div>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 3. PERMANENT PROFILE VIEW -->
                <div id="view-profile" class="tab-view">
                    <div class="profile-grid">
                        <!-- Preferences Card -->
                        <div class="card">
                            <h3 class="section-title">⚙️ Preferences</h3>
                            <div id="profile-pref-stack" class="tag-container" style="margin-bottom: 12px;"></div>
                            <ul id="profile-pref-list" class="profile-list"></ul>
                        </div>

                        <!-- Core Principles Card -->
                        <div class="card">
                            <h3 class="section-title">🕯️ Core Principles</h3>
                            <ul id="profile-principles-list" class="profile-list"></ul>
                        </div>

                        <!-- Tracked Projects Card -->
                        <div class="card full-width">
                            <h3 class="section-title">📂 Tracked Projects & Milestones</h3>
                            <div id="profile-projects-container" style="display: flex; flex-direction: column; gap: 1rem;"></div>
                        </div>

                        <!-- Decisions Log Card -->
                        <div class="card full-width">
                            <h3 class="section-title">⚖️ Historic Decisions Log</h3>
                            <ul id="profile-decisions-list" class="profile-list"></ul>
                        </div>
                    </div>
                </div>

                <!-- 4. DOSSIER VIEW -->
                <div id="view-dossier" class="tab-view">
                    <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 1rem;">
                        <button onclick="triggerAutoRun()">
                            <span>Force Compile Daily Dossier</span>
                            <div id="dossier-spinner" class="spinner"></div>
                        </button>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">
                            Compiles all developer files, resolves memory anomalies, and writes the finalized dossier to the profile.
                        </p>
                    </div>
                    <div id="dossier-container" class="dossier-view">
                        <p style="color: var(--text-muted); text-align: center; margin-top: 4rem;">
                            No dossier generated yet. Press the button above to run the compilation pipeline.
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Tab switcher
            function switchTab(tabName, element) {{
                document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                document.querySelectorAll('.tab-view').forEach(view => view.classList.remove('active'));
                
                element.classList.add('active');
                document.getElementById('view-' + tabName).classList.add('active');
                
                // Set Header title
                const titles = {{
                    'dashboard': 'System Dashboard',
                    'chat': 'Co-Founder Assistant',
                    'profile': 'Permanent Developer Profile',
                    'dossier': 'Timeline Dossier Compiler'
                }};
                document.getElementById('view-title').innerText = titles[tabName];
                
                if (tabName === 'profile') {{
                    loadProfileData();
                }} else if (tabName === 'dashboard') {{
                    refreshStats();
                }}
            }}

            // System actions
            async function refreshStats() {{
                try {{
                    const res = await fetch('/api/state');
                    const state = await res.json();
                    
                    const messagesCount = state.temporary_memory ? state.temporary_memory.length : 0;
                    const factsCount = state.extracted_memories ? state.extracted_memories.length : 0;
                    const runsCount = state.date_memory ? Object.keys(state.date_memory).length : 0;
                    
                    document.getElementById('stat-messages').innerText = messagesCount;
                    document.getElementById('stat-facts').innerText = factsCount;
                    document.getElementById('stat-timelines').innerText = runsCount;
                    
                    if (state.final_response && state.final_response.includes('#')) {{
                        document.getElementById('dashboard-summary').innerHTML = marked.parse(state.final_response);
                    }} else if (state.final_response) {{
                        document.getElementById('dashboard-summary').innerText = state.final_response;
                    }}
                }} catch (err) {{
                    console.error("Error fetching stats:", err);
                }}
            }}

            async function loadProfileData() {{
                try {{
                    const res = await fetch('/api/profile');
                    const profile = await res.json();
                    
                    // Render Stack Tags
                    const prefStack = document.getElementById('profile-pref-stack');
                    prefStack.innerHTML = '';
                    if (profile.preferences && profile.preferences.tech_stack) {{
                        profile.preferences.tech_stack.forEach(tech => {{
                            prefStack.innerHTML += `<span class="tag">${{tech}}</span>`;
                        }});
                    }}
                    
                    // Render preferences list
                    const prefList = document.getElementById('profile-pref-list');
                    prefList.innerHTML = '';
                    if (profile.preferences) {{
                        if (profile.preferences.coding_style) {{
                            profile.preferences.coding_style.forEach(style => {{
                                prefList.innerHTML += `<li>⚡ <strong>Coding Style:</strong> ${{style}}</li>`;
                            }});
                        }}
                        if (profile.preferences.workflows) {{
                            profile.preferences.workflows.forEach(flow => {{
                                prefList.innerHTML += `<li>🔄 <strong>Workflow:</strong> ${{flow}}</li>`;
                            }});
                        }}
                    }}
                    
                    // Render principles
                    const princList = document.getElementById('profile-principles-list');
                    princList.innerHTML = '';
                    if (profile.principles) {{
                        if (profile.principles.ideologies) {{
                            profile.principles.ideologies.forEach(ideo => {{
                                princList.innerHTML += `<li>⚖️ ${{ideo}}</li>`;
                            }});
                        }}
                        if (profile.principles.anti_goals) {{
                            profile.principles.anti_goals.forEach(anti => {{
                                princList.innerHTML += `<li style="border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.04);">🚫 <strong>Anti-Goal:</strong> ${{anti}}</li>`;
                            }});
                        }}
                        if (profile.principles.lessons_learned) {{
                            profile.principles.lessons_learned.forEach(lesson => {{
                                princList.innerHTML += `<li>💡 ${{lesson}}</li>`;
                            }});
                        }}
                    }}
                    
                    // Render projects
                    const projContainer = document.getElementById('profile-projects-container');
                    projContainer.innerHTML = '';
                    if (profile.projects && profile.projects.length > 0) {{
                        profile.projects.forEach(project => {{
                            let updatesHtml = project.updates.map(u => `
                                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px; border-left: 2px solid var(--accent-primary); padding-left: 8px;">
                                    <strong>${{new Date(u.timestamp).toLocaleDateString()}}:</strong> ${{u.summary}}
                                </div>
                            `).join('');
                            
                            projContainer.innerHTML += `
                                <div class="card" style="background: rgba(255,255,255,0.01);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <h4 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; color: #b4aeff;">${{project.name}}</h4>
                                        <span class="tag" style="background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.25); color: #34d399;">${{project.status}}</span>
                                    </div>
                                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 8px;">${{project.vision_goal}}</p>
                                    ${{updatesHtml}}
                                </div>
                            `;
                        }});
                    }} else {{
                        projContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No active projects recorded yet.</p>`;
                    }}

                    // Render Decisions
                    const decList = document.getElementById('profile-decisions-list');
                    decList.innerHTML = '';
                    if (profile.decisions && profile.decisions.length > 0) {{
                        profile.decisions.forEach(dec => {{
                            decList.innerHTML += `
                                <li>
                                    <strong style="color: #b4aeff;">${{dec.title}}</strong> 
                                    <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 8px;">${{new Date(dec.timestamp).toLocaleDateString()}}</span>
                                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;">${{dec.context_why}}</p>
                                </li>
                            `;
                        }});
                    }} else {{
                        decList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No critical architectural decisions saved.</p>`;
                    }}
                }} catch (err) {{
                    console.error("Error loading profile:", err);
                }}
            }}

            async function sendChatMessage() {{
                const input = document.getElementById('chat-input-field');
                const text = input.value.strip ? input.value.strip() : input.value.trim();
                if (!text) return;
                
                input.value = '';
                
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML += `<div class="message-bubble user">${{text}}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
                
                const spinner = document.getElementById('chat-spinner');
                spinner.style.display = 'inline-block';
                
                try {{
                    const res = await fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message: text }})
                    }});
                    const data = await res.json();
                    
                    const responseHtml = marked.parse(data.response);
                    chatBox.innerHTML += `<div class="message-bubble ai">${{responseHtml}}</div>`;
                }} catch (err) {{
                    chatBox.innerHTML += `<div class="message-bubble ai" style="color: #ef4444;">Error contacting memory graph node. Ensure the server is online.</div>`;
                }} finally {{
                    spinner.style.display = 'none';
                    chatBox.scrollTop = chatBox.scrollHeight;
                }}
            }}

            function handleChatEnter(event) {{
                if (event.key === 'Enter') {{
                    sendChatMessage();
                }}
            }}

            async function triggerAutoRun() {{
                const spinner = document.getElementById('dossier-spinner');
                spinner.style.display = 'inline-block';
                
                try {{
                    const res = await fetch('/api/auto-run', {{ method: 'POST' }});
                    const data = await res.json();
                    
                    const container = document.getElementById('dossier-container');
                    container.innerHTML = marked.parse(data.dossier);
                }} catch (err) {{
                    alert("Auto pipeline compilation run failed. Check console logs.");
                }} finally {{
                    spinner.style.display = 'none';
                }}
            }}

            async function resetSystem() {{
                if (confirm("Are you sure you want to purge the live system state? This does not delete vector databases, but will wipe active session chat history.")) {{
                    try {{
                        await fetch('/api/reset', {{ method: 'POST' }});
                        alert("System state reset completed.");
                        window.location.reload();
                    }} catch (err) {{
                        alert("Reset operation failed.");
                    }}
                }}
            }}

            // Initial startup refresh
            refreshStats();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Launching Co-Founder Memory Cockpit on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
