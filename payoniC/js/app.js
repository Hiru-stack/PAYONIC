/**
 * Payonic App - Routing and Event Handling
 */
const App = {
    init() {
        this.main = document.getElementById('main-content');
        this.nav = document.getElementById('nav-links');

        window.addEventListener('hashchange', () => this.route());
        this.route();
    },

    route() {
        const hash = window.location.hash || '#home';
        const user = Store.getCurrentUser();

        // Theme management
        if (hash === '#home' || hash === '#login' || hash === '#register') {
            document.body.className = 'landing-page';
        } else {
            document.body.className = ''; // Default dark theme for dashboard
        }

        // Security check
        if (!user && hash !== '#login' && hash !== '#register' && hash !== '#home' && hash !== '#admin-login') {
            window.location.hash = '#home';
            return;
        }

        if (user && (hash === '#login' || hash === '#register' || hash === '#home' || hash === '#admin-login')) {
            window.location.hash = '#dashboard';
            return;
        }

        // Update Navbar
        if (hash === '#home' || hash === '#login' || hash === '#register' || hash === '#admin-login') {
            // Navbar is handled within the components for these pages for custom layout
            document.getElementById('navbar').style.display = 'none';
        } else {
            document.getElementById('navbar').style.display = 'block';
            this.nav.innerHTML = Components.Navbar(user);
        }
        lucide.createIcons();

        // Route Content
        switch (hash) {
            case '#home':
                this.main.innerHTML = Components.Landing();
                break;
            case '#login':
                this.renderLogin();
                break;
            case '#admin-login':
                this.renderAdminLogin();
                break;
            case '#register':
                this.renderRegister();
                break;
            case '#dashboard':
                this.renderDashboard(user);
                break;
            case '#recharge':
                this.renderRecharge(user);
                break;
            case '#pay':
                this.renderPayGate(user);
                break;
            case '#analytics':
                if (user.role === 'student') this.renderExpenseAnalytics(user);
                break;
            case '#qr':
                if (user.role === 'vendor') this.main.innerHTML = Components.VendorQR(user);
                break;
            case '#requests':
                if (user.role === 'admin') this.renderAdminRequests();
                break;
            case '#split-bill':
                if (user.role === 'student') this.renderSplitBill(user);
                break;
            default:
                this.main.innerHTML = '<div class="centered-layout"><h1>404 - Not Found</h1></div>';
        }
    },

    // Rendering Methods
    renderLogin() {
        this.main.innerHTML = Components.Login();
        const form = document.getElementById('login-form');
        form.onsubmit = (e) => {
            e.preventDefault();
            const username = e.target.username.value;
            const password = e.target.password.value;

            const users = Store.getUsers();
            const user = users.find(u => u.username === username && u.password === password);

            if (user) {
                if (user.role === 'vendor' && user.status === 'pending') {
                    this.showFlash('Account pending admin approval.', 'warning');
                    return;
                }
                Store.setCurrentUser(user);
                this.showFlash(`Login successful! Welcome ${user.username}`, 'success');
                window.location.hash = '#dashboard';
            } else {
                this.showFlash('Invalid credentials', 'danger');
            }
        };
    },

    renderAdminLogin() {
        this.main.innerHTML = Components.AdminLogin();
        lucide.createIcons();
        const form = document.getElementById('admin-login-form');
        form.onsubmit = (e) => {
            e.preventDefault();
            const username = document.getElementById('admin-username').value;
            const password = document.getElementById('admin-password').value;

            // Dedicated Admin Credentials
            if (username === 'admin' && password === '23456') {
                const users = Store.getUsers();
                let adminUser = users.find(u => u.username === 'admin');

                if (!adminUser) {
                    adminUser = { id: 0, username: 'admin', password: 'password', role: 'admin', fullname: 'System Administrator', wallet: 0 };
                    Store.saveUser(adminUser);
                }

                Store.setCurrentUser(adminUser);
                this.showFlash('Welcome Master Admin', 'success');
                window.location.hash = '#dashboard';
            } else {
                this.showFlash('Invalid Administrator passkey', 'danger');
            }
        };
    },

    renderRegister() {
        this.main.innerHTML = Components.Register();
        this.handleRegRoleChange('student'); // Default fields

        const form = document.getElementById('register-form');
        form.onsubmit = (e) => {
            e.preventDefault();
            const role = document.getElementById('reg-role').value;
            const username = e.target['reg-username'].value;
            const password = e.target['reg-password'].value;
            const fullname = e.target['reg-fullname'].value;

            const users = Store.getUsers();
            if (users.find(u => u.username === username)) {
                this.showFlash('Username already exists', 'danger');
                return;
            }

            let userData = {
                username,
                password,
                role,
                fullname,
                wallet: role === 'student' ? 1000 : 0
            };

            if (role === 'student') {
                userData.regNumber = e.target['reg-student-id'].value;
                userData.faculty = e.target['reg-faculty'].value;
                userData.universityEmail = e.target['reg-email'].value;
            } else {
                userData.nicNumber = e.target['reg-nic'].value;
                userData.businessName = e.target['reg-business-name'].value;
                userData.businessType = e.target['reg-business-type'].value;
            }

            Store.saveUser(userData);

            if (role === 'vendor') {
                this.showFlash('Vendor registration submitted! Wait for Admin approval.', 'info');
                window.location.hash = '#home';
            } else {
                this.showFlash('Registration successful! Please login.', 'success');
                window.location.hash = '#login';
            }
        };
    },

    handleRegRoleChange(role) {
        const input = document.getElementById('reg-role');
        if (input) input.value = role;

        // Toggle active class on cards
        document.querySelectorAll('.role-card').forEach(card => card.classList.remove('active'));
        const activeCard = document.getElementById(`role-student${role === 'student' ? '' : '-vendor'}`);
        // Wait, I named them role-student and role-vendor in components.js
        const targetId = role === 'student' ? 'role-student' : 'role-vendor';
        const card = document.getElementById(targetId);
        if (card) card.classList.add('active');

        const fields = document.getElementById('dynamic-fields');
        if (fields) {
            fields.innerHTML = role === 'student' ? Components.StudentFields() : Components.VendorFields();
            lucide.createIcons();
        }
    },

    nextRegStep() {
        const s1 = document.getElementById('reg-step-1');
        const s2 = document.getElementById('reg-step-2');
        if (s1 && s2) {
            s1.style.display = 'none';
            s2.style.display = 'block';
            document.getElementById('reg-step-text').innerText = 'Step 2 of 2';
            document.getElementById('reg-progress-text').innerText = '100% Complete';
            document.getElementById('reg-progress-bar').style.width = '100%';
            lucide.createIcons();
        }
    },

    prevRegStep() {
        const s1 = document.getElementById('reg-step-1');
        const s2 = document.getElementById('reg-step-2');
        if (s1 && s2) {
            s1.style.display = 'block';
            s2.style.display = 'none';
            document.getElementById('reg-step-text').innerText = 'Step 1 of 2';
            document.getElementById('reg-progress-text').innerText = '50% Complete';
            document.getElementById('reg-progress-bar').style.width = '50%';
        }
    },

    renderDashboard(user) {
        if (user.role === 'student') {
            const transactions = Store.getTransactions(user.id);
            this.main.innerHTML = Components.StudentDashboard(user, transactions);
        } else if (user.role === 'vendor') {
            if (user.status === 'pending') {
                this.main.innerHTML = `
                    <div class="centered-layout">
                        <div class="glass-panel auth-card animate-fade-in" style="text-align: center; border-top: 4px solid var(--warning);">
                            <h2 class="text-gradient">Approval Pending</h2>
                            <p>Your vendor account is currently being reviewed by an administrator. Please check back later.</p>
                            <button onclick="Store.logout()" class="btn btn-outline" style="margin-top:2rem">Logout</button>
                        </div>
                    </div>
                `;
                return;
            }
            const transactions = Store.getTransactions(user.id);
            this.main.innerHTML = `
                <div class="container animate-fade-in" style="padding: 2rem 0;">
                    <h2 class="text-gradient">Vendor Dashboard</h2>
                    <div class="dashboard-grid">
                        <div class="glass-panel stat-card">
                            <span class="stat-label">Total Earnings</span>
                            <span class="stat-value text-gradient">LKR ${user.wallet.toLocaleString()}</span>
                            <a href="#qr" class="btn btn-primary" style="margin-top: 1rem;">View My QR</a>
                        </div>
                        <div class="glass-panel" style="grid-column: span 2; padding: 1.5rem;">
                            <h3>Recent Payments Received</h3>
                            <div class="table-container">
                                <table>
                                    <thead><tr><th>From</th><th>Amount</th><th>Date</th></tr></thead>
                                    <tbody>
                                        ${transactions.map(t => `<tr><td>${t.senderId}</td><td>LKR ${t.amount}</td><td>${new Date(t.timestamp).toLocaleDateString()}</td></tr>`).join('') || '<tr><td colspan="3">No sales yet</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else if (user.role === 'admin') {
            const users = Store.getUsers();
            const requests = Store.getRequests().filter(r => r.status === 'pending');
            const pendingVendors = users.filter(u => u.role === 'vendor' && u.status === 'pending');

            this.main.innerHTML = `
                <div class="container animate-fade-in" style="padding: 2rem 0;">
                    <h2 class="text-gradient">Admin Executive Dashboard</h2>
                    <div class="dashboard-grid">
                        <div class="glass-panel stat-card">
                            <span class="stat-label">Action Required</span>
                            <span class="stat-value text-gradient">${requests.length + pendingVendors.length}</span>
                            <a href="#requests" class="btn btn-primary" style="margin-top: 1rem;">Go to Approval Center</a>
                        </div>
                        <div class="glass-panel stat-card">
                            <span class="stat-label">System Liquidity</span>
                            <span class="stat-value text-gradient">LKR ${users.reduce((acc, u) => acc + (u.wallet || 0), 0).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            `;
        }
    },

    renderAdminRequests() {
        const requests = Store.getRequests();
        const pendingVendors = Store.getUsers().filter(u => u.role === 'vendor' && u.status === 'pending');
        this.main.innerHTML = Components.AdminRequests(requests, pendingVendors);
    },

    handleVendorApproval(vendorId, action) {
        if (action === 'approve') {
            Store.approveVendor(parseInt(vendorId));
            this.showFlash('Vendor account approved!', 'success');
        } else {
            this.showFlash('Vendor request rejected.', 'danger');
        }
        this.renderAdminRequests();
    },

    handleRequest(requestId, status) {
        const admin = Store.getCurrentUser();
        Store.updateRequest(parseInt(requestId), status, admin.id);
        this.showFlash(`Request ${status}!`, status === 'approved' ? 'success' : 'danger');
        this.renderAdminRequests();
    },

    renderRecharge(user) {
        this.main.innerHTML = Components.Recharge();
        document.getElementById('recharge-form').onsubmit = (e) => {
            e.preventDefault();
            const amount = parseFloat(document.getElementById('recharge-amount').value);
            Store.addRequest(user.id, user.username, amount);
            this.showFlash('Recharge request submitted for Admin approval!', 'success');
            window.location.hash = '#dashboard';
        };
    },

    renderPayGate(user) {
        this.main.innerHTML = Components.PaymentGate();
        lucide.createIcons();
    },

    renderPayByUsername() {
        this.main.innerHTML = Components.PayByUsername();
        lucide.createIcons();

        document.getElementById('payment-form').onsubmit = (e) => {
            e.preventDefault();
            const user = Store.getCurrentUser();
            const vendorName = document.getElementById('vendor-username').value;
            const amount = parseFloat(document.getElementById('pay-amount').value);
            const note = document.getElementById('pay-note').value;

            this.processPayment(user, vendorName, amount, note);
        };
    },

    renderScanQR() {
        this.main.innerHTML = Components.ScanQR();
        lucide.createIcons();
    },

    simulateQRScan() {
        // In a real app, this would be the data from the QR (e.g. "payonic:cafe_vendor")
        const mockQRData = "campus_cafe";
        this.main.innerHTML = Components.PayByUsername();
        document.getElementById('vendor-username').value = mockQRData;
        lucide.createIcons();

        document.getElementById('payment-form').onsubmit = (e) => {
            e.preventDefault();
            const user = Store.getCurrentUser();
            const vendorName = document.getElementById('vendor-username').value;
            const amount = parseFloat(document.getElementById('pay-amount').value);
            const note = document.getElementById('pay-note').value;

            this.processPayment(user, vendorName, amount, note);
        };
    },

    processPayment(user, recipientName, amount, note) {
        if (user.wallet < amount) {
            this.showFlash('Insufficient balance!', 'danger');
            return;
        }

        const users = Store.getUsers();
        const recipient = users.find(u => u.username === recipientName);

        if (!recipient) {
            this.showFlash('Vendor not found!', 'danger');
            return;
        }

        user.wallet -= amount;
        recipient.wallet = (recipient.wallet || 0) + amount;

        Store.saveUser(user);
        Store.saveUser(recipient);

        Store.addTransaction({
            type: 'pay',
            senderId: user.username,
            receiverId: recipient.username,
            description: note || `Payment to ${recipient.username}`,
            amount: amount,
            status: 'completed'
        });

        this.showFlash('Payment successful!', 'success');
        window.location.hash = '#dashboard';
    },

    renderSplitBill(user) {
        this.main.innerHTML = Components.SplitBill();
        this.participants = [];

        document.getElementById('split-bill-form').onsubmit = (e) => {
            e.preventDefault();
            const vendor = document.getElementById('bill-vendor').value;
            const desc = document.getElementById('bill-desc').value;
            const total = parseFloat(document.getElementById('bill-amount').value);

            if (this.participants.length === 0) {
                this.showFlash('Please add at least one participant', 'warning');
                return;
            }

            const perPerson = total / (this.participants.length + 1);
            const participantsData = this.participants.map(p => ({
                id: p.id,
                username: p.username,
                amount: perPerson
            }));

            Store.createBill(user.id, total, `${vendor}: ${desc}`, participantsData);
            this.showFlash('Split bill request sent to participants!', 'success');
            window.location.hash = '#dashboard';
        };
    },

    addParticipant() {
        const username = document.getElementById('participant-username').value.trim();
        if (!username) return;

        const users = Store.getUsers();
        const user = users.find(u => u.username === username && u.role === 'student');

        if (!user) {
            this.showFlash('Student not found!', 'danger');
            return;
        }

        if (this.participants.find(p => p.id === user.id)) {
            this.showFlash('Already added!', 'warning');
            return;
        }

        this.participants.push(user);
        this.updateParticipantsList();
        document.getElementById('participant-username').value = '';
    },

    updateParticipantsList() {
        const list = document.getElementById('participants-list');
        list.innerHTML = this.participants.map(p => `
            <div class="glass-panel" style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 1rem; margin-bottom: 0.5rem; border-radius: 0.5rem;">
                <span>${p.username}</span>
                <button type="button" onclick="App.removeParticipant(${p.id})" style="background: none; border: none; color: var(--danger); cursor: pointer;">&times;</button>
            </div>
        `).join('');
    },

    removeParticipant(id) {
        this.participants = this.participants.filter(p => p.id !== id);
        this.updateParticipantsList();
    },

    renderExpenseAnalytics(user) {
        const transactions = Store.getTransactions(user.id).filter(t => t.type === 'pay');
        this.main.innerHTML = Components.ExpenseAnalytics(transactions);

        const categories = {};
        transactions.forEach(t => {
            const cat = t.category || 'other';
            categories[cat] = (categories[cat] || 0) + t.amount;
        });

        const ctx = document.getElementById('expenseChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(categories).map(c => c.charAt(0).toUpperCase() + c.slice(1)),
                datasets: [{
                    data: Object.values(categories),
                    backgroundColor: ['#6366f1', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Outfit', size: 12 } }
                    }
                }
            }
        });

        const list = document.getElementById('expense-summary-list');
        list.innerHTML = Object.entries(categories).map(([cat, amount]) => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border);">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: ${this.getCategoryColor(cat)}"></div>
                    <span style="font-weight: 500;">${cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
                </div>
                <span class="text-gradient" style="font-weight: 700;">LKR ${amount.toLocaleString()}</span>
            </div>
        `).join('') || '<p style="color: var(--text-muted); text-align: center;">No expenses recorded this month.</p>';
    },

    getCategoryColor(cat) {
        const colors = {
            canteen: '#6366f1',
            store: '#ec4899',
            service: '#8b5cf6',
            other: '#10b981',
            transfer: '#f59e0b'
        };
        return colors[cat] || '#94a3b8';
    },

    // Utils
    showFlash(message, type) {
        const flashContainer = document.getElementById('flash-messages');
        flashContainer.innerHTML = Components.Flash(message, type);
        setTimeout(() => {
            const alert = flashContainer.querySelector('.alert');
            if (alert) alert.remove();
        }, 3000);
    }
};

App.init();
lucide.createIcons();
