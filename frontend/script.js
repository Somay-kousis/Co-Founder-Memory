const appState = {
    system: {},
    profile: {},
    graphAnimation: null,
};

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value = "") {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderMarkdown(markdown = "") {
    const escaped = escapeHtml(markdown);
    return escaped
        .replace(/^### (.*)$/gm, "<h3>$1</h3>")
        .replace(/^## (.*)$/gm, "<h2>$1</h2>")
        .replace(/^# (.*)$/gm, "<h1>$1</h1>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/^\s*[-*] (.*)$/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
        .replace(/\n{2,}/g, "</p><p>")
        .replace(/\n/g, "<br>");
}

function setStatus(label, mode = "loading") {
    const pill = $("#system-status");
    if (!pill) return;
    pill.className = `status-pill ${mode}`;
    pill.querySelector("span:last-child").textContent = label;
}

function updateClock() {
    const clock = $("#system-time");
    if (!clock) return;
    const now = new Date();
    clock.textContent = `${now.toLocaleTimeString([], { hour12: false })} // ${now.toISOString().slice(0, 10)}`;
}

async function api(path, options = {}) {
    const res = await fetch(path, options);
    const contentType = res.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await res.json() : await res.text();
    if (!res.ok) {
        const message = payload?.detail || payload || `Request failed: ${res.status}`;
        throw new Error(message);
    }
    return payload;
}

async function loadAll() {
    try {
        setStatus("syncing", "loading");
        const [health, state, profile] = await Promise.all([
            api("/healthz"),
            api("/api/state"),
            api("/api/profile"),
        ]);

        appState.system = state || {};
        appState.profile = profile || {};
        setStatus(`${health.storage} memory`, "ok");
        renderEverything();
    } catch (error) {
        console.error("[Co-Founder Memory] load failed", error);
        setStatus("backend offline", "error");
        $("#chat-box").innerHTML = `<div class="empty-state error">${escapeHtml(error.message)}</div>`;
    }
}

function renderEverything() {
    renderMetrics();
    renderTimeline();
    renderChat();
    renderVault();
    renderGraph();
}

function renderMetrics() {
    $("#metric-memories").textContent = (appState.system.temporary_memory || []).length;
    $("#metric-projects").textContent = (appState.profile.projects || []).length;
    $("#metric-decisions").textContent = (appState.profile.decisions || []).length;
}

function renderTimeline() {
    const list = $("#timeline-log-list");
    const dateMemory = appState.system.date_memory || {};
    const dates = Object.keys(dateMemory).sort().reverse();

    if (!dates.length) {
        list.innerHTML = `<div class="empty-state">No dossier runs yet. Compile one when you want a fresh continuity report.</div>`;
        return;
    }

    list.innerHTML = dates.map((date, index) => `
        <article class="timeline-item">
            <span>${String(index + 1).padStart(2, "0")}</span>
            <div>
                <strong>${escapeHtml(date)}</strong>
                <p>${escapeHtml(dateMemory[date])}</p>
            </div>
        </article>
    `).join("");
}

function normalizeMessage(message = "") {
    const isMind = /^(AI:|mind:)/i.test(message);
    const isUser = /^User:/i.test(message);
    return {
        role: isMind ? "mind" : isUser ? "user" : "note",
        text: message.replace(/^(AI:|User:|mind:)\s*/i, ""),
    };
}

function renderChat() {
    const chatBox = $("#chat-box");
    const history = appState.system.temporary_memory || [];
    const entries = [
        { role: "system", text: "Memory stream active. Ask for strategy, retrieval, planning, or a profile update." },
        ...history.map(normalizeMessage),
    ];

    chatBox.innerHTML = entries.map((entry, index) => `
        <article class="chat-entry ${entry.role}">
            <div class="chat-meta">log_${String(index).padStart(2, "0")} / ${entry.role}</div>
            <p>${escapeHtml(entry.text)}</p>
        </article>
    `).join("");
    chatBox.scrollTop = chatBox.scrollHeight;
}

function renderVault() {
    const vault = $("#decisions-vault");
    const profile = appState.profile || {};
    const principles = profile.principles?.ideologies || [];
    const antiGoals = profile.principles?.anti_goals || [];
    const decisions = profile.decisions || [];
    const planning = profile.planning || [];

    const items = [
        ...principles.map((text) => ({ type: "principle", title: "Operating principle", body: text })),
        ...antiGoals.map((text) => ({ type: "anti", title: "Anti-goal", body: text })),
        ...decisions.map((item) => ({ type: "decision", title: item.title, body: item.context_why })),
        ...planning.map((item) => ({ type: "plan", title: item.goal, body: item.context || item.horizon })),
    ];

    if (!items.length) {
        vault.innerHTML = `<div class="empty-state">Permanent profile is empty. Tell the system what to remember and it will start building this vault.</div>`;
        return;
    }

    vault.innerHTML = items.slice(0, 12).map((item) => `
        <article class="vault-item ${item.type}">
            <span>${escapeHtml(item.type)}</span>
            <strong>${escapeHtml(item.title || "Untitled")}</strong>
            <p>${escapeHtml(item.body || "")}</p>
        </article>
    `).join("");
}

function collectGraphNodes() {
    const profile = appState.profile || {};
    const nodes = [{ id: "core", label: "Memory", group: "core", radius: 18 }];
    const push = (id, label, group, radius = 10) => {
        if (label && !nodes.some((node) => node.id === id)) nodes.push({ id, label, group, radius });
    };

    (profile.preferences?.tech_stack || ["LangGraph", "FastAPI", "Supabase"]).forEach((item) => {
        push(`stack-${item}`, item, "stack", 9);
    });
    (profile.projects || []).forEach((item) => push(`project-${item.name}`, item.name, "project", 12));
    (profile.decisions || []).forEach((item) => push(`decision-${item.id}`, item.title, "decision", 8));
    (profile.planning || []).forEach((item, index) => push(`plan-${index}`, item.goal, "plan", 8));

    return nodes.slice(0, 18);
}

function renderGraph() {
    const svg = $("#knowledge-graph");
    if (!svg) return;
    if (appState.graphAnimation) cancelAnimationFrame(appState.graphAnimation);

    const width = svg.clientWidth || 420;
    const height = svg.clientHeight || 280;
    const nodes = collectGraphNodes().map((node, index) => ({
        ...node,
        x: width / 2 + Math.cos(index) * 70,
        y: height / 2 + Math.sin(index) * 55,
        vx: 0,
        vy: 0,
    }));
    const links = nodes.filter((node) => node.id !== "core").map((node) => ({ source: "core", target: node.id }));

    svg.innerHTML = "";
    const lineLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const nodeLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.append(lineLayer, nodeLayer);

    const lineEls = links.map((link) => {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.classList.add("graph-link");
        lineLayer.appendChild(line);
        return { link, line };
    });

    const nodeEls = nodes.map((node) => {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.classList.add("graph-node", node.group);
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("r", node.radius);
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.textContent = node.label.length > 18 ? `${node.label.slice(0, 16)}...` : node.label;
        text.setAttribute("dy", node.radius + 16);
        group.append(circle, text);
        group.addEventListener("click", () => {
            $("#chat-input").value = `Recall details about ${node.label}`;
            $("#chat-input").focus();
        });
        nodeLayer.appendChild(group);
        return { node, group };
    });

    function findNode(id) {
        return nodes.find((node) => node.id === id);
    }

    function tick() {
        nodes.forEach((node) => {
            const dx = width / 2 - node.x;
            const dy = height / 2 - node.y;
            node.vx += dx * 0.002;
            node.vy += dy * 0.002;
        });

        for (let i = 0; i < nodes.length; i += 1) {
            for (let j = i + 1; j < nodes.length; j += 1) {
                const a = nodes[i];
                const b = nodes[j];
                const dx = b.x - a.x || 0.01;
                const dy = b.y - a.y || 0.01;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const force = 520 / (distance * distance);
                a.vx -= (dx / distance) * force;
                a.vy -= (dy / distance) * force;
                b.vx += (dx / distance) * force;
                b.vy += (dy / distance) * force;
            }
        }

        links.forEach((link) => {
            const source = findNode(link.source);
            const target = findNode(link.target);
            const dx = target.x - source.x;
            const dy = target.y - source.y;
            const distance = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = (distance - 90) * 0.015;
            source.vx += (dx / distance) * force;
            source.vy += (dy / distance) * force;
            target.vx -= (dx / distance) * force;
            target.vy -= (dy / distance) * force;
        });

        nodes.forEach((node) => {
            node.vx *= 0.86;
            node.vy *= 0.86;
            node.x = Math.max(28, Math.min(width - 28, node.x + node.vx));
            node.y = Math.max(28, Math.min(height - 32, node.y + node.vy));
        });

        lineEls.forEach(({ link, line }) => {
            const source = findNode(link.source);
            const target = findNode(link.target);
            line.setAttribute("x1", source.x);
            line.setAttribute("y1", source.y);
            line.setAttribute("x2", target.x);
            line.setAttribute("y2", target.y);
        });
        nodeEls.forEach(({ node, group }) => {
            group.setAttribute("transform", `translate(${node.x}, ${node.y})`);
        });

        appState.graphAnimation = requestAnimationFrame(tick);
    }
    tick();
}

async function recordResponse(event) {
    event.preventDefault();
    const input = $("#chat-input");
    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    $("#send-btn").disabled = true;
    appState.system.temporary_memory = [...(appState.system.temporary_memory || []), `User: ${message}`, "AI: thinking..."];
    renderChat();

    try {
        const data = await api("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        appState.system = data.state || appState.system;
        appState.profile = await api("/api/profile");
        renderEverything();
    } catch (error) {
        appState.system.temporary_memory = (appState.system.temporary_memory || []).filter((item) => item !== "AI: thinking...");
        appState.system.temporary_memory.push(`AI: Sync failed: ${error.message}`);
        renderChat();
    } finally {
        $("#send-btn").disabled = false;
    }
}

async function purgeState() {
    if (!confirm("Reset the live session state? Permanent Supabase profile memory remains untouched.")) return;
    try {
        const data = await api("/api/reset", { method: "POST" });
        appState.system = data.state || {};
        renderEverything();
    } catch (error) {
        alert(error.message);
    }
}

async function compileDossier() {
    const button = $("#compile-btn");
    button.disabled = true;
    button.textContent = "Compiling...";

    try {
        const data = await api("/api/auto-run", { method: "POST" });
        $("#dossier-content-area").innerHTML = `<p>${renderMarkdown(data.dossier || "No dossier returned.")}</p>`;
        $("#dossier-modal").classList.add("active");
        $("#dossier-modal").setAttribute("aria-hidden", "false");
        appState.system = data.state || appState.system;
        renderEverything();
    } catch (error) {
        alert(`Dossier failed: ${error.message}`);
    } finally {
        button.disabled = false;
        button.textContent = "Compile dossier";
    }
}

function bindEvents() {
    $("#chat-form").addEventListener("submit", recordResponse);
    $("#purge-btn").addEventListener("click", purgeState);
    $("#refresh-btn").addEventListener("click", loadAll);
    $("#compile-btn").addEventListener("click", compileDossier);
    $("#close-modal-btn").addEventListener("click", () => {
        $("#dossier-modal").classList.remove("active");
        $("#dossier-modal").setAttribute("aria-hidden", "true");
    });
}

setInterval(updateClock, 1000);
updateClock();
bindEvents();
loadAll();
