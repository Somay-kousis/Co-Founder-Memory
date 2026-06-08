// frontend/script.js

// Log helper to standard console
const logPrefix = "[Cockpit Mind]";
function systemLog(msg, data = "") {
    console.log(`${logPrefix} ${msg}`, data);
}

// System State Variables
let systemState = {};
let profileData = {};
let graphNodes = [];
let graphLinks = [];
let isDragging = false;
let draggedNode = null;

// Clock updates
function updateSystemClock() {
    const clock = document.getElementById("system-time");
    if (!clock) return;
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    const dateStr = now.toISOString().split('T')[0];
    clock.textContent = `${timeStr} // ${dateStr}`;
}
setInterval(updateSystemClock, 1000);
updateSystemClock();

// Initial Fetch & Render API calls
async function fetchSystemState() {
    try {
        const res = await fetch("/api/state");
        systemState = await res.json();
        systemLog("Loaded system state.", systemState);
        renderTimelineLogs();
        renderDialogue();
    } catch (err) {
        systemLog("Error loading state:", err);
    }
}

async function fetchProfileData() {
    try {
        const res = await fetch("/api/profile");
        profileData = await res.json();
        systemLog("Loaded memory profile.", profileData);
        renderDecisionsVault();
        initKnowledgeGraph();
    } catch (err) {
        systemLog("Error loading profile:", err);
    }
}

// Render left column: Timeline / Date memory runs
function renderTimelineLogs() {
    const list = document.getElementById("timeline-log-list");
    if (!list) return;
    list.innerHTML = "";

    const dateMem = systemState.date_memory || {};
    const dates = Object.keys(dateMem).sort().reverse();

    if (dates.length === 0) {
        list.innerHTML = `
            <div class="timeline-item">
                <div class="timeline-date">[no_runs]</div>
                <div class="timeline-desc">Workspace timeline compilation waiting to run.</div>
            </div>
        `;
        return;
    }

    dates.forEach((date, index) => {
        const item = document.createElement("div");
        item.className = "timeline-item";
        item.innerHTML = `
            <div class="timeline-date">[log_${String(index+1).padStart(2, '0')}] – ${date}</div>
            <div class="timeline-desc">Automatic timeline verification and context distillation: ${dateMem[date]}.</div>
        `;
        list.appendChild(item);
    });
}

// Render middle column: Dialogue
function renderDialogue() {
    const chatBox = document.getElementById("chat-box");
    if (!chatBox) return;
    
    // Clear default logs except initial log_00 system briefing
    chatBox.innerHTML = `
        <div class="log-entry system">
            <span class="log-meta">[log_00] – system</span>
            <p class="log-text">Journal stream active. Seeking context from the vault.</p>
        </div>
    `;

    const chatHistory = systemState.temporary_memory || [];
    chatHistory.forEach((msg, idx) => {
        const entry = document.createElement("div");
        // Distinguish AI and User entries by scanning prefixes
        const isAI = msg.startsWith("AI:") || msg.startsWith("mind:");
        entry.className = `log-entry ${isAI ? 'mind' : 'user'}`;
        
        const cleanMsg = msg.replace(/^(AI:|User:|mind:)\s*/i, "");
        const logId = `log_${String(idx + 1).padStart(2, '0')}`;
        const sourceName = isAI ? "mind" : "user";

        entry.innerHTML = `
            <span class="log-meta">[${logId}] – ${sourceName}</span>
            <p class="log-text">${cleanMsg}</p>
        `;
        chatBox.appendChild(entry);
    });

    // Auto scroll to bottom of the ledger
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Render decisions vault
function renderDecisionsVault() {
    const vault = document.getElementById("decisions-vault");
    if (!vault) return;
    vault.innerHTML = "";

    const decisions = profileData.decisions || [];
    const principles = profileData.principles?.ideologies || [];
    const antiGoals = profileData.principles?.anti_goals || [];

    if (decisions.length === 0 && principles.length === 0 && antiGoals.length === 0) {
        vault.innerHTML = `<p class="empty-vault-msg">No active guidelines or strategic choices saved in the vault.</p>`;
        return;
    }

    // Render principles first
    principles.forEach(princ => {
        const item = document.createElement("div");
        item.className = "vault-item";
        item.innerHTML = `
            <div class="vault-item-title">[principle]</div>
            <div>${princ}</div>
        `;
        vault.appendChild(item);
    });

    // Render anti-goals
    antiGoals.forEach(anti => {
        const item = document.createElement("div");
        item.className = "vault-item";
        item.style.borderLeftColor = "var(--color-accent)";
        item.innerHTML = `
            <div class="vault-item-title" style="color: var(--color-accent);">[anti-goal]</div>
            <div>${anti}</div>
        `;
        vault.appendChild(item);
    });

    // Render decisions
    decisions.forEach(dec => {
        const item = document.createElement("div");
        item.className = "vault-item";
        item.innerHTML = `
            <div class="vault-item-title">[decision // ${dec.id || 'arch'}]</div>
            <strong>${dec.title}</strong>
            <div style="font-size: 0.75rem; color: var(--color-text-muted); margin-top: 4px;">${dec.context_why}</div>
        `;
        vault.appendChild(item);
    });
}

// Send dialogue response
async function recordResponse() {
    const input = document.getElementById("chat-input");
    const val = input.value.trim();
    if (!val) return;

    input.value = "";
    
    // Append user message immediately locally for visual responsiveness
    const chatBox = document.getElementById("chat-box");
    const nextLogIdx = (systemState.temporary_memory || []).length + 1;
    const userLogId = `log_${String(nextLogIdx).padStart(2, '0')}`;
    
    const userEntry = document.createElement("div");
    userEntry.className = "log-entry user";
    userEntry.innerHTML = `
        <span class="log-meta">[${userLogId}] – user</span>
        <p class="log-text">${val}</p>
    `;
    chatBox.appendChild(userEntry);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show temporary typing status
    const loadingEntry = document.createElement("div");
    loadingEntry.className = "log-entry mind typing";
    loadingEntry.innerHTML = `
        <span class="log-meta">[log_${String(nextLogIdx + 1).padStart(2, '0')}] – mind</span>
        <p class="log-text" style="font-style: italic; opacity: 0.6;">writing annotations...</p>
    `;
    chatBox.appendChild(loadingEntry);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: val })
        });
        const data = await res.json();
        
        // Remove typing entry and refresh state/dialogue fully
        const typingEl = chatBox.querySelector(".typing");
        if (typingEl) typingEl.remove();

        systemState = data.state;
        renderDialogue();
        
        // Reload profile in case memory extraction ran on the background thread
        fetchProfileData();
    } catch (err) {
        systemLog("Failed to push dialogue recording:", err);
        const typingEl = chatBox.querySelector(".typing");
        if (typingEl) {
            typingEl.querySelector(".log-text").textContent = "Vault synchronization error. Retrying...";
            typingEl.querySelector(".log-text").style.color = "var(--color-accent)";
        }
    }
}

// Reset session state
async function purgeState() {
    if (!confirm("Wipe conversation logs? Pinned profile vault rules will remain intact.")) return;
    try {
        const res = await fetch("/api/reset", { method: "POST" });
        const data = await res.json();
        systemState = data.state;
        renderDialogue();
        systemLog("Purged session state.");
    } catch (err) {
        systemLog("Reset operation failed:", err);
    }
}

// Compile daily dossier
async function compileDossier() {
    const btn = document.getElementById("compile-btn");
    const originalText = btn.textContent;
    btn.textContent = "Compiling Dossier...";
    btn.disabled = true;

    try {
        const res = await fetch("/api/auto-run", { method: "POST" });
        const data = await res.json();
        
        if (data.dossier) {
            // Render compiled report inside typewriter modal
            const modal = document.getElementById("dossier-modal");
            const content = document.getElementById("dossier-content-area");
            
            // Format markdown correctly
            content.innerHTML = marked.parse(data.dossier);
            modal.classList.add("active");
            
            // Reload logs/states updated by auto pipeline run
            fetchSystemState();
        }
    } catch (err) {
        alert("Compilation failed. Ensure backend database server is fully loaded.");
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Wire up events
document.getElementById("send-btn").addEventListener("click", recordResponse);
document.getElementById("chat-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") recordResponse();
});
document.getElementById("purge-btn").addEventListener("click", (e) => {
    e.preventDefault();
    purgeState();
});
document.getElementById("compile-btn").addEventListener("click", compileDossier);
document.getElementById("close-modal-btn").addEventListener("click", () => {
    document.getElementById("dossier-modal").classList.remove("active");
});

// ====================================================================
// Obsidian-Style Knowledge Graph force-directed simulation
// ====================================================================
function initKnowledgeGraph() {
    const svg = document.getElementById("knowledge-graph");
    if (!svg) return;
    svg.innerHTML = ""; // Clear old graphics

    const width = svg.clientWidth || 300;
    const height = svg.clientHeight || 220;

    // Generate graph nodes based on actual profile parameters
    const nodesMap = new Map();
    
    // Core hub node
    nodesMap.set("mind", { id: "mind", label: "Mind", r: 8, group: "hub", x: width/2, y: height/2 });

    // Ingest Tech Stack items
    const stack = profileData.preferences?.tech_stack || ["LangGraph", "FastAPI", "Supabase"];
    stack.forEach((item, idx) => {
        nodesMap.set(`stack_${item}`, {
            id: `stack_${item}`,
            label: item,
            r: 5,
            group: "stack",
            x: width/2 + 60 * Math.cos(idx * 1.5),
            y: height/2 + 60 * Math.sin(idx * 1.5)
        });
    });

    // Ingest Projects
    const projects = profileData.projects || [];
    projects.forEach((proj, idx) => {
        nodesMap.set(`proj_${proj.name}`, {
            id: `proj_${proj.name}`,
            label: proj.name,
            r: 6,
            group: "project",
            x: width/2 + 80 * Math.cos((idx + 2) * 1.2),
            y: height/2 + 80 * Math.sin((idx + 2) * 1.2)
        });
    });

    // Ingest Decisions
    const decisions = profileData.decisions || [];
    decisions.forEach((dec, idx) => {
        nodesMap.set(`dec_${dec.id}`, {
            id: `dec_${dec.id}`,
            label: dec.title.substring(0, 12) + "...",
            r: 4,
            group: "decision",
            x: width/2 + 50 * Math.cos(idx * 2.2 + 0.5),
            y: height/2 + 50 * Math.sin(idx * 2.2 + 0.5)
        });
    });

    graphNodes = Array.from(nodesMap.values());
    graphLinks = [];

    // Create connections from group items back to the center hub
    graphNodes.forEach(node => {
        if (node.id !== "mind") {
            graphLinks.push({ source: "mind", target: node.id });
        }
    });

    // Append link groups
    const linksGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    linksGroup.setAttribute("class", "links-group");
    svg.appendChild(linksGroup);

    // Append node groups
    const nodesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    nodesGroup.setAttribute("class", "nodes-group");
    svg.appendChild(nodesGroup);

    // Draw lines
    const linkElements = graphLinks.map(link => {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("class", "graph-link");
        linksGroup.appendChild(line);
        return { data: link, element: line };
    });

    // Draw circles and text labels
    const nodeElements = graphNodes.map(node => {
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "graph-node");
        g.setAttribute("id", `node-${node.id}`);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("class", "graph-node-circle");
        circle.setAttribute("r", node.r);
        
        // Style node color by group type (graphite and charcoal accents)
        if (node.group === "hub") {
            circle.style.fill = "var(--color-accent)";
        } else if (node.group === "project") {
            circle.style.fill = "#404144";
        } else {
            circle.style.fill = "var(--color-text-muted)";
        }

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("class", "graph-node-text");
        text.setAttribute("dy", -node.r - 4);
        text.textContent = node.label;

        g.appendChild(circle);
        g.appendChild(text);
        nodesGroup.appendChild(g);

        // Add mouse dragging physics events
        g.addEventListener("mousedown", (e) => {
            isDragging = true;
            draggedNode = node;
            node.fx = node.x;
            node.fy = node.y;
        });

        g.addEventListener("click", () => {
            // Clicking node triggers a quick ledger search preview
            document.querySelectorAll(".graph-node").forEach(el => el.classList.remove("active"));
            g.classList.add("active");
            
            const input = document.getElementById("chat-input");
            if (input) {
                input.value = `Recall details about: ${node.label}`;
                input.focus();
            }
        });

        return { data: node, element: g };
    });

    // SVG Drag listener
    svg.addEventListener("mousemove", (e) => {
        if (!isDragging || !draggedNode) return;
        const rect = svg.getBoundingClientRect();
        draggedNode.x = e.clientX - rect.left;
        draggedNode.y = e.clientY - rect.top;
        draggedNode.fx = draggedNode.x;
        draggedNode.fy = draggedNode.y;
    });

    svg.addEventListener("mouseup", () => {
        if (draggedNode) {
            draggedNode.fx = null;
            draggedNode.fy = null;
        }
        isDragging = false;
        draggedNode = null;
    });

    // Force Directed Spring-Mass Simulation loop
    function updatePhysics() {
        const kSpring = 0.04;
        const lengthRest = 55;
        const kRepulsion = 1200;
        const damping = 0.85;

        // Reset velocities in every frame
        graphNodes.forEach(node => {
            node.vx = node.vx || 0;
            node.vy = node.vy || 0;
        });

        // 1. Repulsive forces between all node pairs
        for (let i = 0; i < graphNodes.length; i++) {
            for (let j = i + 1; j < graphNodes.length; j++) {
                const n1 = graphNodes[i];
                const n2 = graphNodes[j];
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const distSqr = dx * dx + dy * dy || 1;
                const dist = Math.sqrt(distSqr);
                
                const f = kRepulsion / distSqr;
                const fx = (dx / dist) * f;
                const fy = (dy / dist) * f;

                if (n1.fx === undefined || n1.fx === null) { n1.vx -= fx; n1.vy -= fy; }
                if (n2.fx === undefined || n2.fx === null) { n2.vx += fx; n2.vy += fy; }
            }
        }

        // 2. Spring forces along link edges
        graphLinks.forEach(link => {
            const sourceNode = graphNodes.find(n => n.id === link.source);
            const targetNode = graphNodes.find(n => n.id === link.target);
            if (!sourceNode || !targetNode) return;

            const dx = targetNode.x - sourceNode.x;
            const dy = targetNode.y - sourceNode.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;

            const f = kSpring * (dist - lengthRest);
            const fx = (dx / dist) * f;
            const fy = (dy / dist) * f;

            if (sourceNode.fx === undefined || sourceNode.fx === null) { sourceNode.vx += fx; sourceNode.vy += fy; }
            if (targetNode.fx === undefined || targetNode.fx === null) { targetNode.vx -= fx; targetNode.vy -= fy; }
        });

        // 3. Gravity pulling toward center viewport
        const centerX = width / 2;
        const centerY = height / 2;
        const kGravity = 0.01;
        graphNodes.forEach(node => {
            const dx = centerX - node.x;
            const dy = centerY - node.y;
            node.vx += dx * kGravity;
            node.vy += dy * kGravity;
        });

        // 4. Update coordinates & apply damping velocity
        graphNodes.forEach(node => {
            if (node.fx !== undefined && node.fx !== null) {
                node.x = node.fx;
                node.y = node.fy;
                node.vx = 0;
                node.vy = 0;
            } else {
                node.vx *= damping;
                node.vy *= damping;
                node.x += node.vx;
                node.y += node.vy;
            }

            // Keep nodes within canvas viewport borders
            node.x = Math.max(node.r + 10, Math.min(width - node.r - 10, node.x));
            node.y = Math.max(node.r + 10, Math.min(height - node.r - 10, node.y));
        });

        // 5. Update SVG elements layout
        linkElements.forEach(le => {
            const s = graphNodes.find(n => n.id === le.data.source);
            const t = graphNodes.find(n => n.id === le.data.target);
            if (s && t) {
                le.element.setAttribute("x1", s.x);
                le.element.setAttribute("y1", s.y);
                le.element.setAttribute("x2", t.x);
                le.element.setAttribute("y2", t.y);
            }
        });

        nodeElements.forEach(ne => {
            ne.element.setAttribute("transform", `translate(${ne.data.x}, ${ne.data.y})`);
        });

        requestAnimationFrame(updatePhysics);
    }

    // Launch Spring Simulation Loop
    requestAnimationFrame(updatePhysics);
}

// Boot operations
async function initSystem() {
    await fetchSystemState();
    await fetchProfileData();
}

window.onload = initSystem;
