// API Base URL - automatically detects environment
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000' 
    : '';

// Global state for chat and milestones
let conversationHistory = [];
let currentMilestones = [];
let currentProjectId = null;
let estimatedPrice = 0;
let currentProjectDeadline = null; // project-level deadline from architect chat

// Role state
let currentRole = null;

// Current logged-in user
let currentUser = null;

// Selected developer (set from Vendors tab)
let selectedDeveloperId = null;
let selectedDeveloperRate = 4200; // default, updated when developer is selected

// ============================================
// AUTH FUNCTIONS
// ============================================

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.querySelector(`[onclick="switchAuthTab('${tab}')"]`).classList.add('active');
    document.getElementById(`${tab}-form`).classList.add('active');
}

function selectRegRole(role) {
    document.getElementById('reg-role').value = role;
    document.getElementById('reg-role-client').classList.toggle('active', role === 'client');
    document.getElementById('reg-role-developer').classList.toggle('active', role === 'developer');
    const devGroup = document.getElementById('dev-threshold-group');
    devGroup.style.display = role === 'developer' ? 'block' : 'none';
    if (role === 'developer') updateThresholdHint();
}

function updateThresholdHint() {
    const val = parseFloat(document.getElementById('reg-threshold').value);
    const hint = document.getElementById('threshold-hint');
    if (val > 0) {
        const rate = (val / 160).toFixed(0);
        hint.textContent = `Equivalent hourly rate: ₹${Number(rate).toLocaleString('en-IN')}/hr (threshold ÷ 160 working hours)`;
    } else {
        hint.textContent = '';
    }
}

async function doRegister() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const threshold = parseFloat(document.getElementById('reg-threshold').value) || null;

    if (!name || !email || !password) { showToast('Missing Fields', 'Please fill in all fields', 'warning'); return; }
    if (password.length < 6) { showToast('Weak Password', 'Password must be at least 6 characters', 'warning'); return; }
    if (role === 'developer' && !threshold) { showToast('Missing Threshold', 'Please enter a payment threshold', 'warning'); return; }

    showLoading();
    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, role, payment_threshold: threshold })
        });
        const data = await safeJsonParse(res);
        if (!res.ok) throw new Error(data.detail || 'Registration failed');
        localStorage.setItem('pillar_user', JSON.stringify(data));
        currentUser = data;
        showToast('Welcome!', `Account created. Welcome, ${data.name}!`, 'success');
        enterApp(data);
    } catch (e) {
        showToast('Error', e.message, 'error');
    } finally {
        hideLoading();
    }
}

async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) { showToast('Missing Fields', 'Please enter email and password', 'warning'); return; }

    showLoading();
    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await safeJsonParse(res);
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        localStorage.setItem('pillar_user', JSON.stringify(data));
        currentUser = data;
        showToast('Welcome back!', `Hello, ${data.name}!`, 'success');
        enterApp(data);
    } catch (e) {
        showToast('Error', e.message, 'error');
    } finally {
        hideLoading();
    }
}

function enterApp(user) {
    document.getElementById('auth-screen').style.display = 'none';
    currentRole = user.role;

    if (user.role === 'client') {
        document.getElementById('client-user-id').value = user.user_id;
        document.getElementById('client-display-name').textContent = user.name;
        document.getElementById('client-display-email').textContent = user.email;
        document.getElementById('client-avatar-initials').textContent = user.name.charAt(0).toUpperCase();
        // Profile tab
        document.getElementById('profile-client-name').textContent = user.name;
        document.getElementById('profile-client-email').textContent = user.email;
        document.getElementById('profile-client-id').textContent = user.user_id;
        document.getElementById('client-profile-avatar').textContent = user.name.charAt(0).toUpperCase();
        document.getElementById('client-app').style.display = 'flex';
        setupNavForApp('client-app');
        loadClientDashboard();
        loadVendors();
        startNewConversation();
    } else {
        document.getElementById('dev-user-id').value = user.user_id;
        document.getElementById('dev-display-name').textContent = user.name;
        document.getElementById('dev-display-email').textContent = user.email;
        document.getElementById('dev-avatar-initials').textContent = user.name.charAt(0).toUpperCase();
        document.getElementById('reputation-user-id').value = user.user_id;
        // Profile tab
        document.getElementById('profile-dev-name').textContent = user.name;
        document.getElementById('profile-dev-email').textContent = user.email;
        document.getElementById('profile-dev-id').textContent = user.user_id;
        document.getElementById('dev-profile-avatar').textContent = user.name.charAt(0).toUpperCase();
        if (user.payment_threshold) {
            document.getElementById('profile-dev-threshold').textContent = `₹${Number(user.payment_threshold).toLocaleString('en-IN')} INR/month`;
            document.getElementById('profile-dev-rate').textContent = `₹${Number(user.hourly_rate).toLocaleString('en-IN')}/hr`;
        }
        document.getElementById('developer-app').style.display = 'flex';
        setupNavForApp('developer-app');
        loadDevDashboard();
        loadPayoutPage();
    }
}

function logout() {
    localStorage.removeItem('pillar_user');
    currentUser = null;
    currentRole = null;
    document.getElementById('client-app').style.display = 'none';
    document.getElementById('developer-app').style.display = 'none';
    document.getElementById('auth-screen').style.display = 'flex';
    // Clear login form
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
    showToast('Logged out', 'See you next time!', 'info');
}

function devSwitchTab(tabName) {
    const app = document.getElementById('developer-app');
    app.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    app.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const btn = app.querySelector(`[data-tab="${tabName}"]`);
    if (btn) btn.classList.add('active');
    const tabEl = document.getElementById(`${tabName}-tab`);
    if (tabEl) tabEl.classList.add('active');
}




function enterAs(role) { /* legacy stub — use enterApp() */ }

function switchRole() { logout(); }

function setupNavForApp(appId) {
    const app = document.getElementById(appId);
    app.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            app.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            app.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tabEl = document.getElementById(`${tabName}-tab`);
            if (tabEl) tabEl.classList.add('active');

            // Lazy-load on tab switch
            if (tabName === 'c-dashboard') loadClientDashboard();
            if (tabName === 'c-vendors') loadVendors();
            if (tabName === 'd-dashboard') loadDevDashboard();
            if (tabName === 'd-payout') loadPayoutPage();
        });
    });
}

function clientSwitchTab(tabName) {
    const app = document.getElementById('client-app');
    app.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    app.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const btn = app.querySelector(`[data-tab="${tabName}"]`);
    if (btn) btn.classList.add('active');
    const tabEl = document.getElementById(`${tabName}-tab`);
    if (tabEl) tabEl.classList.add('active');
}

function getUserId() {
    if (currentRole === 'client') return document.getElementById('client-user-id').value.trim();
    if (currentRole === 'developer') return document.getElementById('dev-user-id').value.trim();
    return document.getElementById('client-user-id')?.value.trim() || '';
}

// ============================================
// CLIENT DASHBOARD
// ============================================

async function loadClientDashboard() {
    const userId = document.getElementById('client-user-id').value.trim();
    const container = document.getElementById('client-orders-list');
    if (!container) return;

    if (!userId) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-user"></i><p>Enter your User ID in the sidebar to load your projects.</p></div>`;
        return;
    }

    container.innerHTML = `<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading projects...</p></div>`;

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${userId}`);
        if (!response.ok) throw new Error('Failed to load projects');
        const projects = await safeJsonParse(response);

        if (!projects || projects.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects yet. Start by creating a plan.</p>
                    <button class="btn btn-primary" onclick="clientSwitchTab('c-plan')">Create Project</button>
                </div>`;
            return;
        }

        let html = `<div class="orders-table-wrap"><table class="orders-table">
            <thead><tr>
                <th>Project</th><th>Milestone</th><th>Status</th><th>Deadline</th><th>Cost</th><th>Deliverable</th>
            </tr></thead><tbody>`;

        projects.forEach(project => {
            const milestones = project.milestones || [];
            if (milestones.length === 0) {
                html += `<tr>
                    <td>${escapeHtml(project.title)}</td>
                    <td colspan="5" style="color:var(--text-muted)">No milestones</td>
                </tr>`;
            } else {
                const rate = project.developer_hourly_rate || 4200;
                milestones.forEach((m, i) => {
                    const statusClass = `status-${(m.status || 'pending').toLowerCase()}`;
                    const deadline = m.deadline ? new Date(m.deadline).toLocaleDateString() : '\u2014';
                    const cost = m.estimated_hours ? `₹${(m.estimated_hours * rate).toLocaleString('en-IN')}` : '\u2014';
                    let deliverableHtml = '<span style="color:var(--text-muted)">\u2014</span>';
                    if (m.status === 'RELEASED') {
                        if (m.submission_source === 'github' && m.submission_github_url) {
                            deliverableHtml = `<a href="${escapeHtml(m.submission_github_url)}" target="_blank" class="btn btn-primary" style="padding:4px 10px;font-size:12px;"><i class="fab fa-github"></i> View Repo</a>`;
                        } else {
                            deliverableHtml = `<button class="btn btn-primary" style="padding:4px 10px;font-size:12px;" onclick="downloadMilestoneFiles('${m.id}')"><i class="fas fa-download"></i> Download</button>`;
                        }
                    }
                    html += `<tr>
                        ${i === 0 ? `<td rowspan="${milestones.length}" style="font-weight:600">${escapeHtml(project.title)}<br><small style="color:var(--text-muted)">${project.id}</small></td>` : ''}
                        <td>${escapeHtml(m.title)}</td>
                        <td><span class="status-badge ${statusClass}">${m.status || 'PENDING'}</span></td>
                        <td>${deadline}</td>
                        <td>${cost}</td>
                        <td>${deliverableHtml}</td>
                    </tr>`;
                });
            }
        });

        html += `</tbody></table></div>`;
        container.innerHTML = html;

    } catch (e) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Could not load projects: ${e.message}</p></div>`;
    }
}

async function downloadMilestoneFiles(milestoneId) {
    try {
        const response = await fetch(`${API_BASE_URL}/milestone/${milestoneId}/download`);
        if (!response.ok) {
            const err = await safeJsonParse(response);
            throw new Error(err.detail || 'Failed to download files');
        }
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            const data = await response.json();
            if (data.type === 'github') {
                window.open(data.url, '_blank');
                return;
            }
        }
        // Zip download
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `milestone_${milestoneId.slice(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (e) {
        showToast('Download Failed', e.message, 'error');
    }
}

// ============================================
// DEVELOPER DASHBOARD
// ============================================

async function loadDevDashboard() {
    const container = document.getElementById('dev-work-list');
    if (!container) return;

    const devId = currentUser && currentUser.user_id;
    if (!devId) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-user"></i><p>Please log in to see your work.</p></div>`;
        return;
    }

    container.innerHTML = `<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading your assigned projects...</p></div>`;

    try {
        const response = await fetch(`${API_BASE_URL}/projects/developer/${devId}`);
        if (!response.ok) throw new Error('Failed to load projects');
        const projects = await safeJsonParse(response);

        if (!projects || projects.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-tasks"></i><p>No projects assigned to you yet. Clients will hire you from the Vendors tab.</p></div>`;
            return;
        }

        checkProjectCompletionNotifications(projects);

        const hourlyRate = currentUser.hourly_rate || 4200;

        let html = '';
        projects.forEach(project => {
            const milestones = project.milestones || [];
            const clientName = project.client_name || project.user_id;
            html += `<div class="milestone-card" style="margin-bottom:16px;">
                <div class="milestone-header">
                    <div class="milestone-title">${escapeHtml(project.title)}</div>
                    <div style="text-align:right">
                        <small style="color:var(--text-muted);display:block">ID: ${project.id.slice(0,8)}…</small>
                        <small style="color:var(--accent-primary)">Client: ${escapeHtml(clientName)}</small>
                    </div>
                </div>`;
            milestones.forEach((m, i) => {
                const statusClass = `status-${(m.status || 'pending').toLowerCase()}`;
                const canSubmit = m.status === 'PENDING';
                const payment = m.estimated_hours ? `₹${(m.estimated_hours * hourlyRate).toLocaleString('en-IN')}` : '—';
                const deadline = m.deadline ? new Date(m.deadline).toLocaleDateString() : '—';
                html += `<div style="padding:10px 0; border-top:1px solid rgba(255,255,255,0.05);">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                        <span style="font-weight:500">${i + 1}. ${escapeHtml(m.title)}</span>
                        <div style="display:flex;gap:8px;align-items:center;">
                            <span class="status-badge ${statusClass}">${m.status || 'PENDING'}</span>
                            ${canSubmit ? `<button class="btn btn-primary" style="padding:4px 12px;font-size:12px;" onclick="quickSubmit('${project.id}','${m.id}')">Submit</button>` : ''}
                        </div>
                    </div>
                    <div style="display:flex;gap:16px;margin-top:4px;font-size:12px;color:var(--text-muted);">
                        <span><i class="fas fa-calendar"></i> ${deadline}</span>
                        <span><i class="fas fa-indian-rupee-sign"></i> ${payment}</span>
                        ${m.estimated_hours ? `<span><i class="fas fa-clock"></i> ${m.estimated_hours}h</span>` : ''}
                    </div>
                </div>`;
            });
            html += `</div>`;
        });

        container.innerHTML = html;

    } catch (e) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Could not load work: ${e.message}</p></div>`;
    }
}

function quickSubmit(projectId, milestoneId) {
    // Pre-fill submit tab and switch to it
    document.getElementById('submit-project-id').value = projectId;
    document.getElementById('submit-milestone-id').value = milestoneId;
    const app = document.getElementById('developer-app');
    app.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    app.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const btn = app.querySelector('[data-tab="d-submit"]');
    if (btn) btn.classList.add('active');
    const tabEl = document.getElementById('d-submit-tab');
    if (tabEl) tabEl.classList.add('active');
    showToast('Ready', 'Project and milestone pre-filled. Upload or fetch your files.', 'info');
}

// ============================================
// VENDORS TAB
// ============================================

async function loadVendors() {
    const container = document.getElementById('vendors-list');
    if (!container) return;

    container.innerHTML = `<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading developers...</p></div>`;

    try {
        const res = await fetch(`${API_BASE_URL}/users/developers`);
        if (!res.ok) throw new Error('Failed to load developers');
        const developers = await safeJsonParse(res);

        if (!developers || developers.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-users"></i><p>No developers registered yet.</p></div>`;
            return;
        }

        const colors = ['#6366f1','#1dbf73','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#14b8a6'];

        container.innerHTML = developers.map((dev, i) => {
            const initials = dev.name.split(' ').map(n => n[0]).join('').toUpperCase();
            const rate = dev.hourly_rate ? `₹${Number(dev.hourly_rate).toLocaleString('en-IN')}/hr` : 'Rate TBD';
            const isSelected = selectedDeveloperId === dev.id;
            return `
            <div class="vendor-card ${isSelected ? 'vendor-selected' : ''}" id="vendor-card-${dev.id}">
                <div class="vendor-avatar" style="background:${colors[i % colors.length]}">${initials}</div>
                <div class="vendor-name">${escapeHtml(dev.name)}</div>
                <div class="vendor-meta">
                    <span><i class="fas fa-indian-rupee-sign"></i> ${rate}</span>
                    ${dev.payment_threshold ? `<span><i class="fas fa-bullseye"></i> ₹${Number(dev.payment_threshold).toLocaleString('en-IN')}/mo</span>` : ''}
                </div>
                <button class="btn ${isSelected ? 'btn-success' : 'btn-primary'}" style="margin-top:12px;width:100%;"
                    onclick="selectDeveloper('${dev.id}', '${escapeHtml(dev.name)}', ${dev.hourly_rate || 4200})">
                    <i class="fas ${isSelected ? 'fa-check' : 'fa-handshake'}"></i>
                    ${isSelected ? 'Selected' : 'Select Developer'}
                </button>
            </div>`;
        }).join('');

    } catch (e) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Could not load developers: ${e.message}</p></div>`;
    }
}

function selectDeveloper(devId, devName, devRate) {
    // Toggle: clicking the already-selected developer deselects them
    if (selectedDeveloperId === devId) {
        selectedDeveloperId = null;
        selectedDeveloperRate = 4200;
        const card = document.getElementById(`vendor-card-${devId}`);
        if (card) {
            card.classList.remove('vendor-selected');
            const btn = card.querySelector('button');
            if (btn) { btn.className = 'btn btn-primary'; btn.innerHTML = '<i class="fas fa-handshake"></i> Select Developer'; }
        }
        showToast('Developer Deselected', `${devName} removed from project`, 'info');
        return;
    }

    // Deselect any previously selected developer
    if (selectedDeveloperId) {
        const prevCard = document.getElementById(`vendor-card-${selectedDeveloperId}`);
        if (prevCard) {
            prevCard.classList.remove('vendor-selected');
            const btn = prevCard.querySelector('button');
            if (btn) { btn.className = 'btn btn-primary'; btn.innerHTML = '<i class="fas fa-handshake"></i> Select Developer'; }
        }
    }

    selectedDeveloperId = devId;
    selectedDeveloperRate = devRate || 4200;
    const card = document.getElementById(`vendor-card-${devId}`);
    if (card) {
        card.classList.add('vendor-selected');
        const btn = card.querySelector('button');
        if (btn) { btn.className = 'btn btn-success'; btn.innerHTML = '<i class="fas fa-check"></i> Selected'; }
    }
    showToast('Developer Selected', `${devName} — ₹${Number(selectedDeveloperRate).toLocaleString('en-IN')}/hr`, 'success');
}


// Helper function to safely parse JSON responses
async function safeJsonParse(response) {
    const text = await response.text();
    if (!text || text.trim() === '') {
        throw new Error('Server returned empty response. Make sure the backend is running.');
    }
    try {
        return JSON.parse(text);
    } catch (e) {
        console.error('Failed to parse JSON:', text);
        throw new Error('Server returned invalid response. Check if backend is running correctly.');
    }
}

// Tab switching functionality
document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Remove active class from all nav items and tabs
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        btn.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// File input handler
document.getElementById('code-files')?.addEventListener('change', (e) => {
    const fileList = document.getElementById('file-list');
    const files = Array.from(e.target.files);
    
    if (files.length > 0) {
        fileList.innerHTML = '<p>Selected files:</p>' + 
            files.map(f => `<div>📄 ${f.name}</div>`).join('');
    } else {
        fileList.innerHTML = '';
    }
});

// Show/hide loading spinner
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Show/hide typing indicator
function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'flex';
        const chatArea = document.querySelector('.chat-area');
        if (chatArea) {
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// Toast Notification System
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ============================================
// INTERACTIVE CHAT WITH ARCHITECT AGENT
// ============================================

function addChatMessage(role, content, milestones = null) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-header">You</div>
            <div class="message-content">${escapeHtml(content)}</div>
        `;
    } else {
        let messageContent = `<div class="message-content">${escapeHtml(content)}</div>`;
        
        if (milestones && milestones.length > 0) {
            messageContent += '<div class="milestones-preview">';
            milestones.forEach((m, idx) => {
                messageContent += `
                    <div class="milestone-preview">
                        <strong>${idx + 1}. ${escapeHtml(m.title)}</strong>
                        <p>${escapeHtml(m.description)}</p>
                        <small>Est. ${m.estimated_hours} hours</small>
                    </div>
                `;
            });
            messageContent += '</div>';
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">Architect Agent</div>
            ${messageContent}
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const userMessage = chatInput.value.trim();
    
    if (!userMessage) {
        showToast('Input Required', 'Please enter a message', 'warning');
        return;
    }
    
    // Add user message to chat
    addChatMessage('user', userMessage);
    conversationHistory.push({ role: 'user', content: userMessage });
    
    chatInput.value = '';
    showTypingIndicator();
    
    try {
        // Build conversation context
        const conversationContext = conversationHistory.map(msg => 
            `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`
        ).join('\n\n');
        
        const response = await fetch(`${API_BASE_URL}/chat/architect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userMessage,
                conversation_history: conversationContext,
                current_milestones: currentMilestones
            })
        });
        
        hideTypingIndicator();
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to get response');
        }
        
        const data = await safeJsonParse(response);
        
        // Add AI response to chat
        addChatMessage('assistant', data.response, data.milestones);
        conversationHistory.push({ role: 'assistant', content: data.response });
        
        // Update current milestones if provided
        if (data.milestones && data.milestones.length > 0) {
            currentMilestones = data.milestones;
            updateCurrentMilestonesDisplay();
            document.getElementById('action-buttons').style.display = 'flex';
        }

        // Capture project deadline if architect extracted one
        if (data.project_deadline) {
            currentProjectDeadline = data.project_deadline;
        }
        
    } catch (error) {
        hideTypingIndicator();
        addChatMessage('assistant', `Error: ${error.message}`);
        showToast('Error', error.message, 'error');
    }
}

function updateCurrentMilestonesDisplay() {
    const container = document.getElementById('current-milestones');
    
    if (currentMilestones.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<h3>Current Milestones</h3>';
    currentMilestones.forEach((milestone, index) => {
        html += `
            <div class="milestone-card">
                <div class="milestone-header">
                    <div class="milestone-title">${index + 1}. ${escapeHtml(milestone.title)}</div>
                    <div class="status-badge status-draft">DRAFT</div>
                </div>
                <div class="milestone-description">${escapeHtml(milestone.description)}</div>
                <p style="font-size: 13px; color: var(--text-muted); margin-top: 8px;">
                    <strong>Estimated Hours:</strong> ${milestone.estimated_hours}
                </p>
                <p style="font-size: 13px; color: var(--text-primary); margin-top: 12px;">
                    <strong>Requirements:</strong>
                </p>
                <ul class="requirements-list">
                    ${milestone.requirements.map(req => `<li>${escapeHtml(req)}</li>`).join('')}
                </ul>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function startNewConversation() {
    if (conversationHistory.length > 0) {
        showToast('New Conversation', 'Starting fresh conversation', 'info');
    }
    
    conversationHistory = [];
    currentMilestones = [];
    currentProjectId = null;
    currentProjectDeadline = null;
    
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('current-milestones').innerHTML = '';
    document.getElementById('action-buttons').style.display = 'none';
    document.getElementById('chat-input').value = '';
    
    addChatMessage('assistant', "Hi! I'm the Architect Agent. Before I can build your project plan, I need to understand exactly what you're building.\n\nDescribe your project idea and I'll ask the right questions to turn it into a precise technical checklist.");
}

async function finalizeChecklist() {
    if (currentMilestones.length === 0) {
        showToast('No Milestones', 'Please generate milestones first', 'warning');
        return;
    }
    
    const userId = getUserId();
    if (!userId) {
        showToast('User ID Required', 'Please enter a User ID in the sidebar', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/plan/finalize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                milestones: currentMilestones,
                developer_id: selectedDeveloperId || null,
                project_deadline: currentProjectDeadline || null
            })
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to finalize checklist');
        }
        
        const data = await safeJsonParse(response);
        currentProjectId = data.project_id;
        
        addChatMessage('assistant', `✅ Checklist finalized! Project ID: ${data.project_id}`);
        showToast('Success', 'Checklist finalized successfully!', 'success');
        
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function showEstimatedPrice() {
    if (!currentProjectId) {
        showToast('Finalize First', 'Please finalize the checklist first', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/estimate/${currentProjectId}`);
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to get estimate');
        }
        
        const data = await safeJsonParse(response);
        estimatedPrice = data.total_price;
        
        const priceMessage = `
💰 Estimated Price Breakdown:
- Total Hours: ${data.total_hours}
- Rate: ₹${Number(data.hourly_rate).toLocaleString('en-IN')}/hr
- Total Price: ₹${Number(data.total_price).toLocaleString('en-IN')} INR

Ready to proceed to payment?
        `;
        
        addChatMessage('assistant', priceMessage);
        showToast('Price Calculated', `Total: $${data.total_price}`, 'success');
        
        // Automatically go to payment
        setTimeout(() => goToPayment(), 1000);
        
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

function goToPayment() {
    clientSwitchTab('c-payment');
    displayPaymentSummary();
}

function displayPaymentSummary() {
    const summaryDiv = document.getElementById('payment-summary');
    const gatewayDiv = document.getElementById('payment-gateway');
    
    let html = `
        <h3>Payment Summary</h3>
        <div class="payment-details">
            <p><strong>Project ID:</strong> <code>${currentProjectId}</code></p>
            <p><strong>Total Milestones:</strong> ${currentMilestones.length}</p>
            <p><strong>Estimated Price:</strong> <span class="price-highlight">$${estimatedPrice}</span></p>
        </div>
        
        <h4>Milestones Breakdown:</h4>
    `;
    
    currentMilestones.forEach((milestone, index) => {
        const hourlyRate = selectedDeveloperRate || 4200;
        const milestonePrice = milestone.estimated_hours * hourlyRate;
        html += `
            <div class="payment-milestone">
                <div>${index + 1}. ${escapeHtml(milestone.title)}</div>
                <div>${milestone.estimated_hours} hrs × ₹${Number(hourlyRate).toLocaleString('en-IN')} = ₹${Number(milestonePrice).toLocaleString('en-IN')}</div>
            </div>
        `;
    });
    
    summaryDiv.innerHTML = html;
    gatewayDiv.style.display = 'block';
    
    // Auto-fill mock card details
    document.getElementById('card-number').value = '4532 1234 5678 9010';
    document.getElementById('card-expiry').value = '12/25';
    document.getElementById('card-cvv').value = '123';
    document.getElementById('card-name').value = 'John Doe';
}

async function confirmPayment() {
    if (!currentProjectId) {
        showToast('No Project', 'No project to pay for', 'error');
        return;
    }
    
    // Validate card details
    const cardNumber = document.getElementById('card-number').value.trim();
    const cardExpiry = document.getElementById('card-expiry').value.trim();
    const cardCvv = document.getElementById('card-cvv').value.trim();
    const cardName = document.getElementById('card-name').value.trim();
    
    if (!cardNumber || !cardExpiry || !cardCvv || !cardName) {
        showToast('Incomplete Details', 'Please fill in all card details', 'warning');
        return;
    }
    
    showLoading();
    
    // Simulate payment processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
        const response = await fetch(`${API_BASE_URL}/payment/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_id: currentProjectId,
                amount: estimatedPrice,
                card_last4: cardNumber.slice(-4)
            })
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Payment failed');
        }
        
        const data = await safeJsonParse(response);
        
        document.getElementById('payment-result').innerHTML = `
            <div class="success-message">
                <i class="fas fa-check-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                <h3>Payment Successful!</h3>
                <p>Transaction ID: <code>${data.transaction_id}</code></p>
                <p>Amount: <strong>$${data.amount}</strong></p>
                <p style="margin-top: 16px;">All milestones are now locked and ready for code submission.</p>
                <p style="margin-top: 12px; padding: 12px; background: rgba(29, 191, 115, 0.1); border-radius: 8px;">
                    <strong>Next Step:</strong> Go to the Submit tab to upload your code or fetch from GitHub.
                </p>
            </div>
        `;
        
        // Auto-fill project ID and first milestone ID in submit tab
        document.getElementById('submit-project-id').value = currentProjectId;
        if (currentMilestones.length > 0) {
            const firstMilestoneId = currentMilestones[0].id;
            document.getElementById('submit-milestone-id').value = firstMilestoneId;
            
            // Show helpful info
            showToast('Ready to Submit', `Project ID and Milestone ID auto-filled in Submit tab`, 'info');
            
            console.log('Payment successful - IDs auto-filled:');
            console.log('Project ID:', currentProjectId);
            console.log('First Milestone ID:', firstMilestoneId);
            console.log('All Milestones:', currentMilestones.map(m => ({ id: m.id, title: m.title })));
        }
        
        showToast('Payment Successful', `Transaction ID: ${data.transaction_id}`, 'success');
        
        // Hide payment gateway after success
        document.getElementById('payment-gateway').style.display = 'none';
        
    } catch (error) {
        document.getElementById('payment-result').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                <h3>Payment Failed</h3>
                <p>${error.message}</p>
            </div>
        `;
        showToast('Payment Failed', error.message, 'error');
    } finally {
        hideLoading();
    }
}

function goBackToEdit() {
    clientSwitchTab('c-plan');
    addChatMessage('assistant', 'You\'re back in edit mode. What changes would you like to make?');
}

// Initialize on page load
// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Check for saved session
    const saved = localStorage.getItem('pillar_user');
    if (saved) {
        try {
            const user = JSON.parse(saved);
            currentUser = user;
            enterApp(user);
        } catch (e) {
            localStorage.removeItem('pillar_user');
        }
    }

    // Threshold hint live update
    const thresholdInput = document.getElementById('reg-threshold');
    if (thresholdInput) thresholdInput.addEventListener('input', updateThresholdHint);

    // Submit sub-tab switching
    document.querySelectorAll('.submit-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.submitTab;
            document.querySelectorAll('.submit-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.submit-section').forEach(s => s.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`${tabName}-section`).classList.add('active');
        });
    });
});

// ============================================
// MILESTONE SELECTOR FOR SUBMIT TAB
// ============================================

async function loadProjectMilestones() {
    const projectId = document.getElementById('submit-project-id').value.trim();
    
    if (!projectId) {
        showToast('Project ID Required', 'Please enter a project ID first', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/project/${projectId}`);
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to load project');
        }
        
        const project = await safeJsonParse(response);
        
        if (!project.milestones || project.milestones.length === 0) {
            showToast('No Milestones', 'This project has no milestones', 'warning');
            return;
        }
        
        // Display milestone selector
        const selectorDiv = document.getElementById('milestone-selector');
        const listDiv = document.getElementById('milestone-list');
        
        listDiv.innerHTML = '';
        
        // Status descriptions
        const statusDescriptions = {
            'PENDING': 'Ready for submission',
            'LOCKED': 'Under review',
            'RELEASED': 'Completed',
            'DISPUTED': 'Disputed'
        };
        
        project.milestones.forEach((milestone, index) => {
            const item = document.createElement('div');
            item.className = 'milestone-selector-item';
            const canSubmit = milestone.status === 'PENDING';
            
            if (canSubmit) {
                item.onclick = () => selectMilestone(milestone.id, item);
            } else {
                item.style.opacity = '0.6';
                item.style.cursor = 'not-allowed';
                item.title = `Cannot submit - milestone is ${milestone.status}`;
            }
            
            const statusDesc = statusDescriptions[milestone.status] || milestone.status;
            
            item.innerHTML = `
                <div>
                    <div class="milestone-selector-title">${index + 1}. ${escapeHtml(milestone.title)}</div>
                    <div class="milestone-selector-id">ID: ${milestone.id}</div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">${statusDesc}</div>
                </div>
                <div class="status-badge status-${milestone.status.toLowerCase()}">${milestone.status}</div>
            `;
            
            listDiv.appendChild(item);
        });
        
        selectorDiv.style.display = 'block';
        showToast('Milestones Loaded', `Found ${project.milestones.length} milestones`, 'success');
        
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

function selectMilestone(milestoneId, element) {
    // Update input field
    document.getElementById('submit-milestone-id').value = milestoneId;
    
    // Update visual selection
    document.querySelectorAll('.milestone-selector-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    
    showToast('Milestone Selected', 'Milestone ID filled in', 'success');
}

// ============================================
// GITHUB FETCH FUNCTIONALITY
// ============================================

let fetchedFiles = [];

async function fetchFromGitHub() {
    const repoUrl = document.getElementById('github-repo').value.trim();
    const branch = document.getElementById('github-branch').value.trim() || 'main';
    const path = document.getElementById('github-path').value.trim();
    const statusDiv = document.getElementById('github-status');
    
    if (!repoUrl) {
        showToast('Repository Required', 'Please enter a GitHub repository URL', 'warning');
        return;
    }
    
    // Parse GitHub URL
    const match = repoUrl.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (!match) {
        showToast('Invalid URL', 'Please enter a valid GitHub repository URL', 'error');
        return;
    }
    
    const owner = match[1];
    const repo = match[2].replace('.git', '');
    
    statusDiv.innerHTML = '<div class="status-message info"><i class="fas fa-spinner fa-spin"></i> Fetching repository...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/github/fetch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                owner: owner,
                repo: repo,
                branch: branch,
                path: path
            })
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to fetch repository');
        }
        
        const data = await safeJsonParse(response);
        fetchedFiles = data.files;
        
        if (data.files.length === 0) {
            statusDiv.innerHTML = `
                <div class="status-message warning" style="background: rgba(255, 193, 7, 0.1); border-color: rgba(255, 193, 7, 0.3);">
                    <i class="fas fa-exclamation-triangle"></i>
                    No code files found in ${owner}/${repo}${path ? ' at path: ' + path : ''}
                    <br><small>Explored ${data.folders_explored || 0} folders. Supported extensions: .py, .js, .ts, .java, .cpp, .c, .go, .rs, .jsx, .tsx, .html, .css</small>
                </div>
            `;
            showToast('No Files Found', 'Repository has no code files with supported extensions', 'warning');
        } else {
            statusDiv.innerHTML = `
                <div class="status-message success">
                    <i class="fas fa-check-circle"></i>
                    Successfully fetched ${data.files.length} files from ${owner}/${repo}
                    <br><small>Explored ${data.folders_explored || 0} folders recursively</small>
                </div>
            `;
            showToast('Repository Fetched', `${data.files.length} files loaded from ${data.folders_explored || 0} folders`, 'success');
        }
        
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="status-message error">
                <i class="fas fa-exclamation-circle"></i>
                ${error.message}
            </div>
        `;
        showToast('Fetch Failed', error.message, 'error');
    }
}

// ============================================
// ORIGINAL FUNCTIONS (kept for compatibility)
// ============================================

// Create Plan (legacy function - now using chat)
async function createPlan() {
    const userId = getUserId();
    const prompt = document.getElementById('prompt').value.trim();
    const resultBox = document.getElementById('plan-result');
    
    if (!userId || !prompt) {
        resultBox.innerHTML = '<div class="error-message">Please enter both User ID and Project Idea</div>';
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                user_id: userId
            })
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to create plan');
        }
        
        const data = await safeJsonParse(response);
        
        // Display results
        let html = `<div class="success-message">✅ Project created successfully!</div>`;
        html += `<p><strong>Project ID:</strong> <code>${data.project_id}</code></p>`;
        html += `<p><strong>Milestones:</strong> ${data.milestones.length}</p>`;
        
        data.milestones.forEach((milestone, index) => {
            html += `
                <div class="milestone-card">
                    <div class="milestone-header">
                        <div class="milestone-title">${index + 1}. ${milestone.title}</div>
                        <div class="status-badge status-pending">PENDING</div>
                    </div>
                    <div class="milestone-description">${milestone.description}</div>
                    <p><strong>ID:</strong> <code>${milestone.id}</code></p>
                    <p><strong>Estimated Hours:</strong> ${milestone.estimated_hours}</p>
                    <p><strong>Requirements:</strong></p>
                    <ul class="requirements-list">
                        ${milestone.requirements.map(req => `<li>${req}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        
        resultBox.innerHTML = html;
        
        // Auto-fill project ID in submit tab
        document.getElementById('submit-project-id').value = data.project_id;
        if (data.milestones.length > 0) {
            document.getElementById('submit-milestone-id').value = data.milestones[0].id;
        }
        
    } catch (error) {
        resultBox.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    } finally {
        hideLoading();
    }
}

// Submit Code
async function submitCode() {
    const projectId = document.getElementById('submit-project-id').value.trim();
    const milestoneId = document.getElementById('submit-milestone-id').value.trim();
    const filesInput = document.getElementById('code-files');
    const resultBox = document.getElementById('submit-result');
    const pfiContainer = document.getElementById('pfi-gauge-container');
    
    if (!projectId || !milestoneId) {
        showToast('Missing Information', 'Please enter Project ID and Milestone ID', 'warning');
        return;
    }
    
    // Check if using GitHub fetch or file upload
    const activeSection = document.querySelector('.submit-section.active');
    const isGitHub = activeSection && activeSection.id === 'github-section';
    
    let formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('milestone_id', milestoneId);
    
    if (isGitHub) {
        if (fetchedFiles.length === 0) {
            showToast('No Files', 'Please fetch repository files first', 'warning');
            return;
        }
        
        // Send GitHub files as JSON
        formData.append('github_files', JSON.stringify(fetchedFiles));
        // Send the repo URL so backend can store it for client download
        const repoUrl = document.getElementById('github-repo').value.trim();
        if (repoUrl) formData.append('github_repo_url', repoUrl);
        
    } else {
        if (!filesInput.files || filesInput.files.length === 0) {
            showToast('No Files', 'Please select at least one code file', 'warning');
            return;
        }
        
        for (let file of filesInput.files) {
            formData.append('files', file);
        }
    }
    
    showLoading();
    pfiContainer.style.display = 'none';
    
    // Show progress message
    resultBox.innerHTML = `
        <div class="status-message info">
            <i class="fas fa-spinner fa-spin"></i>
            Analyzing code... This may take 30-60 seconds for large projects.
            <br><small>Please wait, do not refresh the page.</small>
        </div>
    `;
    
    try {
        // Increase timeout to 5 minutes (300000ms)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000);
        
        const response = await fetch(`${API_BASE_URL}/submit`, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to submit code');
        }
        
        const data = await safeJsonParse(response);
        
        // Display results
        if (data.passed) {
            let html = `
                <div class="success-message">
                    <i class="fas fa-check-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                    <h3>Code Inspection Passed!</h3>
                    <p>${data.feedback}</p>
                    <p style="margin-top: 16px; padding: 12px; background: rgba(29, 191, 115, 0.1); border-radius: 8px;">
                        <strong>Status:</strong> Milestone completed and payment released!
                    </p>
                </div>
            `;
            
            if (data.pfi_score !== null) {
                html += `<p style="margin-top: 16px;"><strong>PFI Score:</strong> ${data.pfi_score.toFixed(2)}</p>`;
                
                // Animate PFI gauge
                pfiContainer.style.display = 'block';
                animatePFIGauge(data.pfi_score);
            }
            
            // Display reputation change if available
            if (data.reputation_change) {
                const rep = data.reputation_change;
                const isPositive = rep.score_delta > 0;
                const changeColor = isPositive ? 'var(--accent-green)' : rep.score_delta < 0 ? 'var(--accent-red)' : '#888';
                const changeIcon = isPositive ? '↑' : rep.score_delta < 0 ? '↓' : '→';
                
                html += `
                    <div style="margin-top: 20px; padding: 15px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; border: 2px solid rgba(99, 102, 241, 0.3);">
                        <h4 style="margin: 0 0 10px 0; color: #6366f1;">📊 Reputation Impact</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <strong>Score Change:</strong>
                                <span style="font-size: 24px; font-weight: bold; color: ${changeColor}; margin-left: 10px;">
                                    ${changeIcon} ${Math.abs(rep.score_delta)}
                                </span>
                            </div>
                            <div style="text-align: right;">
                                <strong>New Score:</strong>
                                <span style="font-size: 24px; font-weight: bold; color: #6366f1; margin-left: 10px;">
                                    ${rep.new_score.toFixed(1)}
                                </span>
                            </div>
                        </div>
                        <p style="margin: 10px 0 0 0; color: var(--text-muted); font-size: 14px;">
                            <strong>Reason:</strong> ${rep.reason}
                        </p>
                    </div>
                `;
            }
            
            resultBox.innerHTML = html;
            showToast('Success', 'Code inspection passed!', 'success');
            // Refresh dashboards so client sees RELEASED and dev sees updated status
            loadDevDashboard();
            loadClientDashboard();
            loadPayoutPage();
        } else {
            let html = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                    <h3>Code Inspection Failed</h3>
                    <p>${data.feedback}</p>
                    <p style="margin-top: 16px; padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                        <strong>Status:</strong> Milestone unlocked - you can submit new code to try again.
                    </p>
                </div>
            `;
            resultBox.innerHTML = html;
            showToast('Failed', 'Code inspection did not pass - milestone unlocked for resubmission', 'error');
            // Refresh dev dashboard so milestone shows back as PENDING
            loadDevDashboard();
        }
        
    } catch (error) {
        // Handle timeout specifically
        if (error.name === 'AbortError') {
            resultBox.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 16px;"></i>
                    <h3>Request Timed Out</h3>
                    <p>The code analysis took too long (over 5 minutes). This usually happens with very large codebases.</p>
                    <p style="margin-top: 16px; padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                        <strong>Suggestions:</strong><br>
                        • Try submitting fewer files at once<br>
                        • Check your backend logs for errors<br>
                        • The milestone has been unlocked - you can try again
                    </p>
                </div>
            `;
            showToast('Timeout', 'Request took too long. Try with fewer files.', 'error');
        } else {
            resultBox.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${error.message}</p>
                </div>
            `;
            showToast('Error', error.message, 'error');
        }
    } finally {
        hideLoading();
    }
}

// Animate PFI Gauge
function animatePFIGauge(score) {
    const scoreElement = document.getElementById('pfi-score');
    const fillElement = document.getElementById('pfi-fill');
    
    let currentScore = 0;
    const duration = 2000; // 2 seconds
    const steps = 60;
    const increment = score / steps;
    const stepDuration = duration / steps;
    
    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= score) {
            currentScore = score;
            clearInterval(interval);
        }
        
        scoreElement.textContent = Math.round(currentScore);
        
        // Change color based on score
        if (currentScore >= 80) {
            scoreElement.style.color = 'var(--accent-green)';
            scoreElement.style.textShadow = '0 0 20px var(--accent-green)';
        } else if (currentScore >= 50) {
            scoreElement.style.color = '#ffff00';
            scoreElement.style.textShadow = '0 0 20px #ffff00';
        } else {
            scoreElement.style.color = 'var(--accent-red)';
            scoreElement.style.textShadow = '0 0 20px var(--accent-red)';
        }
    }, stepDuration);
}

// View Project
async function viewProject() {
    const projectId = document.getElementById('view-project-id').value.trim();
    const resultBox = document.getElementById('project-result');
    
    if (!projectId) {
        resultBox.innerHTML = '<div class="error-message">Please enter Project ID</div>';
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/project/${projectId}`);
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to load project');
        }
        
        const project = await safeJsonParse(response);
        
        // Display project info
        let html = `<div class="success-message">✅ Project loaded successfully!</div>`;
        html += `<h3>${project.title}</h3>`;
        html += `<p>${project.description}</p>`;
        html += `<p><strong>User ID:</strong> ${project.user_id}</p>`;
        html += `<p><strong>Created:</strong> ${new Date(project.created_at).toLocaleString()}</p>`;
        html += `<h4>Milestones (${project.milestones.length}):</h4>`;
        
        project.milestones.forEach((milestone, index) => {
            const statusClass = `status-${milestone.status.toLowerCase()}`;
            const canDelete = milestone.status === 'PENDING';
            
            // Status descriptions
            const statusDescriptions = {
                'PENDING': 'Ready for code submission',
                'LOCKED': 'Under review - code is being inspected',
                'RELEASED': 'Completed - payment released',
                'DISPUTED': 'Disputed - requires resolution'
            };
            const statusDesc = statusDescriptions[milestone.status] || milestone.status;
            
            // Format deadline and calculate days remaining
            let deadlineHtml = '';
            if (milestone.deadline) {
                const deadlineDate = new Date(milestone.deadline);
                const formattedDeadline = deadlineDate.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const daysRemaining = milestone.days_remaining;
                const isOverdue = milestone.overdue;
                
                let daysRemainingText = '';
                if (isOverdue) {
                    daysRemainingText = `<span style="color: var(--accent-red); font-weight: bold;">⚠️ ${Math.abs(daysRemaining)} days overdue</span>`;
                } else if (daysRemaining === 0) {
                    daysRemainingText = `<span style="color: #ffff00; font-weight: bold;">⏰ Due today</span>`;
                } else if (daysRemaining <= 3) {
                    daysRemainingText = `<span style="color: #ffff00; font-weight: bold;">⏰ ${daysRemaining} days remaining</span>`;
                } else {
                    daysRemainingText = `<span style="color: var(--accent-green);">${daysRemaining} days remaining</span>`;
                }
                
                const canAdjust = milestone.status !== 'RELEASED';
                
                deadlineHtml = `
                    <p><strong>Deadline:</strong> ${formattedDeadline}
                        ${canAdjust ? `<button class="btn-primary" style="margin-left: 10px; padding: 4px 12px; font-size: 12px;" onclick="adjustDeadline('${milestone.id}', '${milestone.deadline}')">Adjust</button>` : ''}
                    </p>
                    <p><strong>Time Remaining:</strong> ${daysRemainingText}</p>
                `;
            }
            
            html += `
                <div class="milestone-card">
                    <div class="milestone-header">
                        <div class="milestone-title">${index + 1}. ${milestone.title}</div>
                        <div>
                            <span class="status-badge ${statusClass}" title="${statusDesc}">${milestone.status}</span>
                            ${milestone.status === 'LOCKED' ? `
                                <button class="btn-primary" onclick="unlockMilestone('${milestone.id}')" 
                                        style="background: #f59e0b; margin-left: 8px;"
                                        title="Unlock this stuck milestone">
                                    Unlock
                                </button>
                            ` : ''}
                            <button class="btn-danger" onclick="deleteMilestone('${milestone.id}')" 
                                    ${!canDelete ? 'disabled' : ''} 
                                    title="${canDelete ? 'Delete this milestone' : 'Cannot delete - milestone is ' + milestone.status}">
                                Delete
                            </button>
                        </div>
                    </div>
                    <div class="milestone-description">${milestone.description}</div>
                    <p><strong>ID:</strong> <code>${milestone.id}</code></p>
                    <p><strong>Status:</strong> ${statusDesc}${milestone.status === 'LOCKED' ? ' <span style="color: #f59e0b;">(Click Unlock if stuck)</span>' : ''}</p>
                    <p><strong>Estimated Hours:</strong> ${milestone.estimated_hours}</p>
                    ${deadlineHtml}
                    <p><strong>Requirements:</strong></p>
                    <ul class="requirements-list">
                        ${milestone.requirements.map(req => `<li>${req}</li>`).join('')}
                    </ul>
                    ${milestone.inspection_result ? `
                        <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;">
                            <strong>Inspection Result:</strong><br>
                            Passed: ${milestone.inspection_result.passed ? '✅' : '❌'}<br>
                            Coverage: ${milestone.inspection_result.coverage_score}%<br>
                            Feedback: ${milestone.inspection_result.feedback}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        resultBox.innerHTML = html;
        
    } catch (error) {
        resultBox.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    } finally {
        hideLoading();
    }
}

// Delete Milestone
async function deleteMilestone(milestoneId) {
    if (!confirm('Are you sure you want to delete this milestone?')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/milestone/${milestoneId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to delete milestone');
        }
        
        alert('Milestone deleted successfully!');
        
        // Reload project view
        const projectId = document.getElementById('view-project-id').value.trim();
        if (projectId) {
            await viewProject();
        }
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Unlock Milestone
async function unlockMilestone(milestoneId) {
    if (!confirm('Unlock this milestone? This will reset it to PENDING state so you can submit code again.')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/milestone/${milestoneId}/unlock`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to unlock milestone');
        }
        
        const data = await safeJsonParse(response);
        
        showToast('Success', data.message, 'success');
        
        // Reload project view
        const projectId = document.getElementById('view-project-id').value.trim();
        if (projectId) {
            await viewProject();
        }
        
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Adjust Milestone Deadline
async function adjustDeadline(milestoneId, currentDeadline) {
    // Prompt for new deadline
    const newDeadlineStr = prompt(
        'Enter new deadline (YYYY-MM-DD HH:MM format):\n\nCurrent deadline: ' + 
        (currentDeadline ? new Date(currentDeadline).toLocaleString() : 'Not set'),
        currentDeadline ? new Date(currentDeadline).toISOString().slice(0, 16).replace('T', ' ') : ''
    );
    
    if (!newDeadlineStr) {
        return; // User cancelled
    }
    
    // Parse and validate the input
    let newDeadline;
    try {
        // Try to parse the date
        const parts = newDeadlineStr.trim().split(' ');
        if (parts.length !== 2) {
            throw new Error('Invalid format');
        }
        
        const [datePart, timePart] = parts;
        newDeadline = new Date(datePart + 'T' + timePart + ':00Z').toISOString();
    } catch (e) {
        showToast('Invalid Format', 'Please use YYYY-MM-DD HH:MM format (e.g., 2024-12-31 23:59)', 'error');
        return;
    }
    
    // Optional: Ask for reason
    const reason = prompt('Reason for deadline adjustment (optional):');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/milestone/${milestoneId}/deadline`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                new_deadline: newDeadline,
                reason: reason || undefined
            })
        });
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to adjust deadline');
        }
        
        const data = await safeJsonParse(response);
        
        showToast('Success', 'Deadline adjusted successfully!', 'success');
        
        // Reload project view
        const projectId = document.getElementById('view-project-id').value.trim();
        if (projectId) {
            await viewProject();
        }
        
    } catch (error) {
        showToast('Error', error.message, 'error');
    } finally {
        hideLoading();
    }
}

// View Reputation
async function viewReputation() {
    const userId = document.getElementById('reputation-user-id').value.trim();
    const resultBox = document.getElementById('reputation-result');
    
    if (!userId) {
        resultBox.innerHTML = '<div class="error-message">Please enter User ID</div>';
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/reputation/${userId}`);
        
        if (!response.ok) {
            const error = await safeJsonParse(response);
            throw new Error(error.detail || 'Failed to load reputation');
        }
        
        const reputation = await safeJsonParse(response);
        
        // Display reputation info with new fields
        let html = `<div class="success-message">✅ Reputation loaded successfully!</div>`;
        html += `<h3>User: ${reputation.user_id}</h3>`;
        
        // Reputation Score with visual indicator
        const scoreColor = reputation.reputation_score >= 80 ? 'var(--accent-green)' : 
                          reputation.reputation_score >= 50 ? '#ffff00' : 'var(--accent-red)';
        html += `
            <div style="margin: 20px 0; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px; text-align: center;">
                <h2 style="color: ${scoreColor}; font-size: 48px; margin: 0;">${reputation.reputation_score.toFixed(1)}</h2>
                <p style="color: var(--text-muted); margin: 5px 0;">Reputation Score</p>
            </div>
        `;
        
        // Timeline Performance Metrics
        html += `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                <div style="padding: 15px; background: rgba(29, 191, 115, 0.1); border-radius: 8px; border: 1px solid rgba(29, 191, 115, 0.3);">
                    <div style="font-size: 24px; font-weight: bold; color: var(--accent-green);">${reputation.on_time_count}</div>
                    <div style="color: var(--text-muted); font-size: 13px;">On-Time Deliveries</div>
                </div>
                <div style="padding: 15px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);">
                    <div style="font-size: 24px; font-weight: bold; color: var(--accent-red);">${reputation.late_count}</div>
                    <div style="color: var(--text-muted); font-size: 13px;">Late Deliveries</div>
                </div>
                <div style="padding: 15px; background: rgba(99, 102, 241, 0.1); border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.3);">
                    <div style="font-size: 24px; font-weight: bold; color: #6366f1;">${reputation.on_time_percentage.toFixed(1)}%</div>
                    <div style="color: var(--text-muted); font-size: 13px;">On-Time Rate</div>
                </div>
                <div style="padding: 15px; background: rgba(168, 85, 247, 0.1); border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.3);">
                    <div style="font-size: 24px; font-weight: bold; color: #a855f7;">${reputation.total_milestones_completed}</div>
                    <div style="color: var(--text-muted); font-size: 13px;">Total Milestones</div>
                </div>
            </div>
        `;
        
        html += `<p><strong>Average PFI Score:</strong> ${reputation.average_pfi_score.toFixed(2)}</p>`;
        
        // Reputation History Timeline
        if (reputation.reputation_history && reputation.reputation_history.length > 0) {
            html += `<h4 style="margin-top: 30px;">Reputation History:</h4>`;
            reputation.reputation_history.slice().reverse().forEach((event, index) => {
                const isPositive = event.score_change > 0;
                const changeColor = isPositive ? 'var(--accent-green)' : 'var(--accent-red)';
                const changeIcon = isPositive ? '↑' : '↓';
                
                // Event type labels
                const eventLabels = {
                    'on_time_delivery': '✅ On-Time Delivery',
                    'late_delivery': '⏰ Late Delivery',
                    'high_quality': '⭐ High Quality',
                    'low_quality': '⚠️ Low Quality'
                };
                const eventLabel = eventLabels[event.event_type] || event.event_type;
                
                html += `
                    <div style="padding: 15px; margin: 10px 0; background: rgba(0,0,0,0.3); border-radius: 8px; border-left: 3px solid ${changeColor};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${eventLabel}</strong><br>
                                <small style="color: var(--text-muted);">Milestone: ${event.milestone_id}</small><br>
                                <small style="color: var(--text-muted);">${new Date(event.timestamp).toLocaleString()}</small>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 24px; font-weight: bold; color: ${changeColor};">
                                    ${changeIcon} ${Math.abs(event.score_change)}
                                </div>
                                <small style="color: var(--text-muted);">Score: ${event.resulting_score.toFixed(1)}</small>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            html += `<p style="margin-top: 20px; color: var(--text-muted);">No reputation history yet.</p>`;
        }
        
        resultBox.innerHTML = html;
        
    } catch (error) {
        resultBox.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
    } finally {
        hideLoading();
    }
}


// ============================================
// PAYOUT PAGE
// ============================================

async function loadPayoutPage() {
    const container = document.getElementById('payout-content');
    if (!container) return;

    const devId = currentUser && currentUser.user_id;
    if (!devId) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-user"></i><p>Please log in to view earnings.</p></div>`;
        return;
    }

    container.innerHTML = `<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading earnings...</p></div>`;

    try {
        const res = await fetch(`${API_BASE_URL}/developer/${devId}/earnings`);
        if (!res.ok) throw new Error('Failed to load earnings');
        const data = await safeJsonParse(res);

        if (!data.projects || data.projects.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-wallet"></i><p>No earnings yet. Complete milestones to see your payouts here.</p></div>`;
            return;
        }

        const totalEarned = Number(data.total_earned).toLocaleString('en-IN');
        const pendingCount = data.pending_milestones;
        const completedProjects = data.completed_projects;

        let html = `
            <div class="payout-summary-grid">
                <div class="payout-stat-card payout-stat-green">
                    <div class="payout-stat-value">₹${totalEarned}</div>
                    <div class="payout-stat-label">Total Earned</div>
                </div>
                <div class="payout-stat-card payout-stat-blue">
                    <div class="payout-stat-value">${completedProjects}</div>
                    <div class="payout-stat-label">Projects Completed</div>
                </div>
                <div class="payout-stat-card payout-stat-amber">
                    <div class="payout-stat-value">${pendingCount}</div>
                    <div class="payout-stat-label">Milestones Pending</div>
                </div>
            </div>
        `;

        data.projects.forEach(project => {
            const projectEarned = Number(project.project_earned).toLocaleString('en-IN');
            const completionPct = project.total_milestones > 0
                ? Math.round((project.released_milestones / project.total_milestones) * 100)
                : 0;
            const completedBadge = project.all_completed
                ? `<span class="status-badge status-released" style="margin-left:8px;"><i class="fas fa-check-circle"></i> Fully Paid</span>`
                : `<span class="status-badge status-pending" style="margin-left:8px;">${project.released_milestones}/${project.total_milestones} done</span>`;

            html += `
                <div class="payout-project-card">
                    <div class="payout-project-header">
                        <div>
                            <div class="payout-project-title">${escapeHtml(project.project_title)} ${completedBadge}</div>
                            <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                                Client: ${escapeHtml(project.client_name)} &nbsp;·&nbsp;
                                Rate: ₹${Number(project.hourly_rate).toLocaleString('en-IN')}/hr
                            </div>
                        </div>
                        <div class="payout-project-total">₹${projectEarned}</div>
                    </div>
                    <div class="payout-progress-bar">
                        <div class="payout-progress-fill" style="width:${completionPct}%"></div>
                    </div>
                    <table class="payout-milestone-table">
                        <thead><tr><th>Milestone</th><th>Hours</th><th>Status</th><th>Earned</th></tr></thead>
                        <tbody>
                            ${project.milestones.map(m => `
                                <tr>
                                    <td>${escapeHtml(m.title)}</td>
                                    <td>${m.estimated_hours}h</td>
                                    <td><span class="status-badge status-${(m.status || 'pending').toLowerCase()}">${m.status}</span></td>
                                    <td style="font-weight:600;color:${m.status === 'RELEASED' ? 'var(--accent-green)' : 'var(--text-muted)'}">
                                        ${m.status === 'RELEASED' ? '₹' + Number(m.earned).toLocaleString('en-IN') : '—'}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (e) {
        container.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-circle"></i><p>Could not load earnings: ${e.message}</p></div>`;
    }
}

// Check if any project just became fully completed and notify
function checkProjectCompletionNotifications(projects) {
    if (!projects) return;
    projects.forEach(project => {
        const milestones = project.milestones || [];
        if (milestones.length === 0) return;
        const allDone = milestones.every(m => m.status === 'RELEASED');
        if (allDone) {
            const key = `notified_complete_${project.id}`;
            if (!sessionStorage.getItem(key)) {
                sessionStorage.setItem(key, '1');
                showToast(
                    '🎉 Project Complete!',
                    `All milestones for "${project.title}" have been released. Full payment earned!`,
                    'success'
                );
            }
        }
    });
}
