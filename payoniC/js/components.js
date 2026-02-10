/**
 * Payonic Components - HTML templates and rendering functions
 */
const Components = {
    // Layout Components
    Navbar(user) {
        if (!user) return '';

        const links = {
            student: `
                <li><a href="#dashboard" class="nav-link">Dashboard</a></li>
                <li><a href="#pay" class="nav-link">Pay</a></li>
                <li><a href="#split-bill" class="nav-link">Split Bill</a></li>
                <li><a href="#recharge" class="nav-link">Recharge</a></li>
            `,
            vendor: `
                <li><a href="#dashboard" class="nav-link">Dashboard</a></li>
                <li><a href="#qr" class="nav-link">My QR</a></li>
            `,
            admin: `
                <li><a href="#dashboard" class="nav-link">Admin</a></li>
                <li><a href="#requests" class="nav-link">Requests</a></li>
            `
        };

        return `
            ${links[user.role] || ''}
            <li><a href="#logout" class="nav-link" onclick="Store.logout()">Logout</a></li>
        `;
    },

    // View Components
    Landing() {
        return `
            <div class="landing-page animate-fade-in">
                <div class="container">
                    <div class="hero-wrapper">
                        <div class="hero-text">
                            <div style="margin-bottom: 2.5rem;">
                                <div class="nav-brand" style="font-size: 2.5rem;">
                                    <i data-lucide="wallet" class="text-gradient" style="width: 54px; height: 54px;"></i>
                                    Payonic
                                </div>
                            </div>
                            <span class="hero-badge">Future of campus fintech</span>
                            <h1 class="hero-headline">Empowering Campus Life with Digital Payments</h1>
                            <p class="hero-subtitle" style="margin-bottom: 2.5rem; font-size: 1.125rem; opacity: 0.8;">
                                The all-in-one financial ecosystem designed specifically for modern university ecosystems. 
                                Streamline transactions for students, vendors, and admins alike.
                            </p>
                            <div style="display: flex; gap: 1rem;">
                                <a href="#register" class="btn btn-primary" style="padding: 1rem 2rem;">Join the Ecosystem</a>
                                <a href="#login" class="btn btn-outline" style="padding: 1rem 2rem; border-color: rgba(255,255,255,0.2);">Sign In</a>
                            </div>
                        </div>
                        <div class="hero-image">
                            <!-- Placeholder for mockup image -->
                            <div style="width: 100%; height: 350px; background: rgba(255,255,255,0.05); border-radius: 1.5rem; display: flex; align-items: center; justify-content: center;">
                                <i data-lucide="wallet" style="width: 64px; height: 64px; opacity: 0.2;"></i>
                            </div>
                        </div>
                    </div>

                    <div class="stats-bar glass-panel">
                        <div class="stat-item">
                            <span class="stat-num">10k+</span>
                            <span class="stat-text">Daily Active Users</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num">50+</span>
                            <span class="stat-text">Campus Partners</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num">1M+</span>
                            <span class="stat-text">Monthly Transactions</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num">99.9%</span>
                            <span class="stat-text">Average Uptime</span>
                        </div>
                    </div>

                    <div class="stakeholder-section">
                        <h2 style="font-size: 3rem; margin-bottom: 1.5rem; font-weight: 800;">Tailored for Every Campus Stakeholder</h2>
                        <p style="color: var(--text-muted); font-size: 1.25rem; max-width: 700px; margin: 0 auto 5rem;">
                            A unified ecosystem that solves specific pain points for students, merchant vendors, and university administrators.
                        </p>
                        
                        <div class="stakeholder-grid">
                            <div class="feature-card">
                                <div class="feature-icon-wrapper">
                                    <div class="feature-icon"><i data-lucide="graduation-cap"></i></div>
                                </div>
                                <h3>For Students</h3>
                                <p>Tap-to-Pay convenience, easy split bills with friends, and instant wallet top-ups.</p>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon-wrapper">
                                    <div class="feature-icon"><i data-lucide="store"></i></div>
                                </div>
                                <h3>For Vendors</h3>
                                <p>Real-time settlements, merchant QR system, and detailed sales analytics.</p>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon-wrapper">
                                    <div class="feature-icon"><i data-lucide="shield-check"></i></div>
                                </div>
                                <h3>For Admins</h3>
                                <p>Centralized user management, recharge approval workflows, and ecosystem oversight.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <footer style="padding: 4rem 0; background: rgba(0,0,0,0.2); margin-top: 4rem;">
                    <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="nav-brand" style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                                <i data-lucide="wallet" class="text-gradient"></i>
                                Payonic
                            </div>
                            <p style="color: var(--text-muted); font-size: 0.875rem;">© 2026 Payonic Technologies Inc. All rights reserved.</p>
                            <a href="#admin-login" style="font-size: 0.75rem; color: rgba(255,255,255,0.1); margin-top: 1rem; display: inline-block;">Admin Portal Access</a>
                        </div>
                        <div style="display: flex; gap: 2rem;">
                            <a href="#" class="nav-link">Privacy Policy</a>
                            <a href="#" class="nav-link">Terms of Use</a>
                            <a href="#" class="nav-link">Campus Contact</a>
                        </div>
                    </div>
                </footer>
            </div>
        `;
    },

    AdminLogin() {
        return `
            <div class="landing-page animate-fade-in" style="min-height: 100vh;">
                <nav class="navbar">
                    <div class="container nav-content">
                        <div class="nav-brand">
                            <i data-lucide="wallet" class="text-gradient"></i>
                            Payonic
                        </div>
                        <a href="#home" class="btn btn-outline" style="padding: 0.6rem 1.25rem;">Exit Portal</a>
                    </div>
                </nav>
                <div class="auth-container">
                    <div class="glass-panel auth-card" style="border-top: 4px solid var(--accent);">
                        <div style="text-align: center; margin-bottom: 2.5rem;">
                            <div class="nav-brand" style="justify-content: center; font-size: 2rem;">
                                <i data-lucide="shield-check" class="text-gradient" style="width: 42px; height: 42px;"></i>
                                Admin Portal
                            </div>
                        </div>

                        <div class="glass-panel" style="padding: 1rem; border-color: var(--accent); background: rgba(139, 92, 246, 0.05); margin-bottom: 2rem; text-align: center;">
                            <p style="font-size: 0.875rem; color: var(--text-main);">
                                <i data-lucide="info" style="width: 16px; vertical-align: middle; margin-right: 4px;"></i>
                                Authorized Personnel Only. Try <strong>admin</strong> and <strong>23456</strong>.
                            </p>
                        </div>

                        <form id="admin-login-form">
                            <div class="form-group">
                                <label class="form-label">System Username</label>
                                <input type="text" id="admin-username" class="form-control" required placeholder="Master access ID">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Secure Passkey</label>
                                <input type="password" id="admin-password" class="form-control" required placeholder="••••••••">
                            </div>
                            <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1.25rem; background: linear-gradient(135deg, var(--accent), var(--secondary));">Initialize Dashboard</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    },

    Login() {
        return `
            <div class="landing-page animate-fade-in" style="min-height: 100vh;">
                <nav class="navbar">
                    <div class="container nav-content">
                        <div class="nav-brand">
                    <i data-lucide="wallet" class="text-gradient"></i>
                    Payonic
                </div>
                        <div style="display: flex; align-items: center; gap: 1.5rem;">
                            <span style="font-size: 0.9rem; color: var(--text-muted);">New here?</span>
                            <a href="#register" class="btn btn-outline" style="padding: 0.6rem 1.25rem;">Create Account</a>
                        </div>
                    </div>
                </nav>
                <div class="auth-container">
                    <div class="glass-panel auth-card">
                        <div style="text-align: center; margin-bottom: 2.5rem;">
                            <div class="nav-brand" style="justify-content: center; font-size: 2rem;">
                                <i data-lucide="wallet" class="text-gradient" style="width: 42px; height: 42px;"></i>
                                Payonic
                            </div>
                        </div>
                        <h2 class="auth-title">Welcome back</h2>
                        <p class="auth-subtitle">Sign in to your secure campus wallet.</p>
                        <form id="login-form">
                            <div class="form-group">
                                <label class="form-label">Username</label>
                                <input type="text" id="username" class="form-control" required placeholder="e.g. alex_johnson">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Password</label>
                                <input type="password" id="password" class="form-control" required placeholder="••••••••">
                            </div>
                            <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1.25rem; margin-top: 1rem;">Sign In</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    },

    Register() {
        return `
            <div class="landing-page animate-fade-in" style="min-height: 100vh;">
                <nav class="navbar">
                    <div class="container nav-content">
                        <div class="nav-brand">
                    <i data-lucide="wallet" class="text-gradient"></i>
                    Payonic
                </div>
                        <div style="display: flex; align-items: center; gap: 1.5rem;">
                            <span style="font-size: 0.9rem; color: var(--text-muted);">Already have an account?</span>
                            <a href="#login" class="btn btn-outline" style="padding: 0.6rem 1.25rem;">Sign In</a>
                        </div>
                    </div>
                </nav>
                <div class="auth-container">
                    <div class="glass-panel auth-card">
                        <div style="text-align: center; margin-bottom: 2.5rem;">
                            <div class="nav-brand" style="justify-content: center; font-size: 2rem;">
                                <i data-lucide="wallet" class="text-gradient" style="width: 42px; height: 42px;"></i>
                                Payonic
                            </div>
                        </div>

                        <h2 class="auth-title">Create your account</h2>
                        <p class="auth-subtitle">Join the bridge between campus and commerce.</p>
                        
                        <div class="progress-header">
                            <span id="reg-step-text">Step 1 of 2</span>
                            <span id="reg-progress-text">50% Complete</span>
                        </div>
                        <div class="progress-bar-container">
                            <div id="reg-progress-bar" class="progress-bar-fill" style="width: 50%"></div>
                        </div>

                        <form id="register-form">
                            <!-- Step 1: Role Selection -->
                            <div id="reg-step-1">
                                <div class="form-label" style="text-align: center; margin-bottom: 1.5rem;">Choose Account Type</div>
                                <input type="hidden" id="reg-role" value="student">
                                
                                <div class="role-grid">
                                    <div id="role-student" class="glass-panel role-card active" onclick="App.handleRegRoleChange('student')">
                                        <i data-lucide="graduation-cap"></i>
                                        <h4>Student</h4>
                                        <p>Pay, split bills, and top up instantly.</p>
                                    </div>
                                    <div id="role-vendor" class="glass-panel role-card" onclick="App.handleRegRoleChange('vendor')">
                                        <i data-lucide="store"></i>
                                        <h4>Vendor</h4>
                                        <p>Receive payments and track sales.</p>
                                    </div>
                                </div>
                                <button type="button" onclick="App.nextRegStep()" class="btn btn-primary" style="width: 100%; padding: 1.25rem;">Continue to Details</button>
                            </div>

                            <!-- Step 2: Details (Dynamic) -->
                            <div id="reg-step-2" style="display: none;">
                                <div id="dynamic-fields">
                                    <!-- Injected by JS -->
                                </div>
                                
                                <div class="form-group" style="margin-top: 2rem;">
                                    <label class="form-label">Create a Username</label>
                                    <input type="text" id="reg-username" class="form-control" required placeholder="Pick a unique username">
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Set Password</label>
                                    <input type="password" id="reg-password" class="form-control" required placeholder="••••••••">
                                </div>

                                <div style="display: flex; gap: 1rem; margin-top: 3.5rem;">
                                    <button type="button" onclick="App.prevRegStep()" class="btn btn-outline" style="flex: 1; padding: 1rem;">Back</button>
                                    <button type="submit" class="btn btn-primary" style="flex: 2; padding: 1rem;">Create My Account</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
    },

    StudentFields() {
        return `
            <div class="form-group">
                <label class="form-label">Full Name</label>
                <input type="text" id="reg-fullname" class="form-control" required placeholder="e.g. Alex Johnson">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div class="form-group">
                    <label class="form-label">Registration Number</label>
                    <input type="text" id="reg-student-id" class="form-control" required placeholder="e.g. UWU/ICT/20/001">
                </div>
                <div class="form-group">
                    <label class="form-label">Faculty</label>
                    <input type="text" id="reg-faculty" class="form-control" required placeholder="e.g. Technological Studies">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">University Email</label>
                <input type="email" id="reg-email" class="form-control" required placeholder="alex@university.edu">
            </div>
        `;
    },

    VendorFields() {
        return `
            <div class="form-group">
                <label class="form-label">Full Name (Contact Person)</label>
                <input type="text" id="reg-fullname" class="form-control" required placeholder="e.g. John Doe">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div class="form-group">
                    <label class="form-label">NIC Number</label>
                    <input type="text" id="reg-nic" class="form-control" required placeholder="NIC format">
                </div>
                <div class="form-group">
                    <label class="form-label">Business Type</label>
                    <select id="reg-business-type" class="form-control">
                        <option value="canteen">Canteen/Cafe</option>
                        <option value="store">Stationery Shop</option>
                        <option value="service">Printing/Service</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Business Name</label>
                <input type="text" id="reg-business-name" class="form-control" required placeholder="e.g. Campus Central Cafe">
            </div>
        `;
    },

    AdminRequests(requests, pendingVendors) {
        return `
            <div class="container animate-fade-in" style="padding: 2rem 0;">
                <h2 class="text-gradient">Admin Approval Center</h2>
                
                <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
                    <h3>Pending Vendor Registrations</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Business Name</th>
                                    <th>Owner</th>
                                    <th>Type</th>
                                    <th>NIC</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${pendingVendors.length ? pendingVendors.map(v => `
                                    <tr>
                                        <td>${v.businessName}</td>
                                        <td>${v.fullname}</td>
                                        <td>${v.businessType}</td>
                                        <td>${v.nicNumber}</td>
                                        <td>
                                            <button onclick="App.handleVendorApproval('${v.id}', 'approve')" class="btn btn-primary btn-sm">Approve</button>
                                            <button onclick="App.handleVendorApproval('${v.id}', 'reject')" class="btn btn-danger btn-sm">Reject</button>
                                        </td>
                                    </tr>
                                `).join('') : '<tr><td colspan="5" style="text-align: center">No pending vendors</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="glass-panel" style="padding: 2rem;">
                    <h3>Recharge Requests</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Amount</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${requests.length ? requests.map(r => `
                                    <tr>
                                        <td>${r.username}</td>
                                        <td>LKR ${r.amount}</td>
                                        <td>${new Date(r.createdAt).toLocaleDateString()}</td>
                                        <td><span class="badge badge-${r.status === 'pending' ? 'warning' : r.status === 'approved' ? 'success' : 'danger'}">${r.status}</span></td>
                                        <td>
                                            ${r.status === 'pending' ? `
                                                <button onclick="App.handleRequest('${r.id}', 'approved')" class="btn btn-primary btn-sm">Approve</button>
                                                <button onclick="App.handleRequest('${r.id}', 'rejected')" class="btn btn-danger btn-sm">Reject</button>
                                            ` : '-'}
                                        </td>
                                    </tr>
                                `).join('') : '<tr><td colspan="5" style="text-align: center">No requests found</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    },

    StudentDashboard(user, transactions) {
        return `
            <div class="container animate-fade-in" style="padding: 2rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <h2 class="text-gradient">Student Wallet</h2>
                    <a href="#analytics" class="btn btn-outline" style="border-radius: 2rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i data-lucide="pie-chart" style="width: 18px;"></i> Monthly Report
                    </a>
                </div>
                
                <div class="dashboard-grid">
                    <div class="glass-panel stat-card">
                        <span class="stat-label">Available Balance</span>
                        <span class="stat-value text-gradient">LKR ${user.wallet.toLocaleString()}</span>
                        <div style="display: flex; gap: 0.75rem; margin-top: 1.5rem;">
                            <a href="#pay" class="btn btn-primary" style="flex: 1;">Pay Vendor</a>
                            <a href="#recharge" class="btn btn-outline" style="flex: 1;">Top Up</a>
                        </div>
                    </div>
                    
                    <div class="glass-panel" style="grid-column: span 2; padding: 1.5rem;">
                        <h3 style="display: flex; align-items: center; gap: 0.75rem;">
                            <i data-lucide="history" style="width: 20px;"></i> Recent Activity
                        </h3>
                        <div class="table-container">
                            <table>
                                <thead><tr><th>Target</th><th>Type</th><th>Amount</th><th>Date</th></tr></thead>
                                <tbody>
                                    ${transactions.slice(0, 5).map(t => `
                                        <tr>
                                            <td>${t.description || (t.type === 'pay' ? t.receiverId : t.senderId)}</td>
                                            <td><span class="badge badge-${t.type === 'pay' ? 'danger' : 'success'}">${t.type}</span></td>
                                            <td>${t.type === 'pay' ? '-' : '+'}LKR ${t.amount}</td>
                                            <td>${new Date(t.timestamp).toLocaleDateString()}</td>
                                        </tr>
                                    `).join('') || '<tr><td colspan="4">No transactions yet</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    PaymentGate() {
        return `
            <div class="container animate-fade-in" style="padding: 2rem 0;">
                <h2 class="text-gradient">Choose Payment Mode</h2>
                <div class="role-grid" style="grid-template-columns: 1fr 1fr; margin-top: 2rem;">
                    <div class="glass-panel role-card active" onclick="App.renderPayByUsername()">
                        <i data-lucide="user"></i>
                        <h4>Pay by Username</h4>
                        <p>Type the vendor's unique username to pay.</p>
                    </div>
                    <div class="glass-panel role-card" onclick="App.renderScanQR()">
                        <i data-lucide="qr-code"></i>
                        <h4>Scan QR Code</h4>
                        <p>Simulate scanning a merchant's QR.</p>
                    </div>
                </div>
            </div>
        `;
    },

    PayByUsername() {
        return `
            <div class="centered-layout">
                <div class="glass-panel auth-card animate-fade-in" style="width: 100%; max-width: 450px;">
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <h3 class="text-gradient">Pay Vendor</h3>
                    </div>
                    <form id="payment-form">
                        <div class="form-group">
                            <label class="form-label">Vendor Username</label>
                            <input type="text" id="vendor-username" class="form-control" placeholder="e.g. campus_cafe" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Amount (LKR)</label>
                            <input type="number" id="pay-amount" class="form-control" placeholder="0.00" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Receipt / Item Name</label>
                            <input type="text" id="pay-note" class="form-control" placeholder="e.g. Chicken Kottu">
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1.25rem;">Confirm Payment</button>
                    </form>
                    <a href="#pay" style="display: block; text-align: center; margin-top: 1.5rem; font-size: 0.875rem; color: var(--text-muted);">Change Payment Mode</a>
                </div>
            </div>
        `;
    },

    ScanQR() {
        return `
            <div class="centered-layout">
                <div class="glass-panel auth-card animate-fade-in" style="width: 100%; max-width: 450px; text-align: center;">
                    <h3 class="text-gradient" style="margin-bottom: 2rem;">Scan QR</h3>
                    <div style="width: 200px; height: 200px; margin: 0 auto 2rem; border: 2px dashed var(--primary); border-radius: 1rem; display: flex; align-items: center; justify-content: center; background: rgba(99, 102, 241, 0.05); position: relative; overflow: hidden;">
                        <i data-lucide="qr-code" style="width: 100px; height: 100px; opacity: 0.3;"></i>
                        <div style="position: absolute; width: 100%; height: 2px; background: var(--primary); top: 0; animation: scanLine 2s infinite linear;"></div>
                    </div>
                    <p style="color: var(--text-muted); margin-bottom: 2rem;">Align the merchant's QR code within the frame to simulate payment.</p>
                    <button onclick="App.simulateQRScan()" class="btn btn-primary" style="width: 100%; padding: 1rem;">Simulate Success Scan</button>
                    <a href="#pay" style="display: block; margin-top: 1.5rem; font-size: 0.875rem; color: var(--text-muted);">Cancel</a>
                </div>
            </div>
            <style>
                @keyframes scanLine {
                    0% { top: 0; }
                    100% { top: 100%; }
                }
            </style>
        `;
    },

    SplitBill() {
        return `
            <div class="container animate-fade-in" style="padding: 2rem 0;">
                <h2 class="text-gradient">Split a Bill</h2>
                <div class="glass-panel" style="padding: 2.5rem; margin-top: 1.5rem; max-width: 600px;">
                    <form id="split-bill-form">
                        <div class="form-group">
                            <label class="form-label">Vendor Username / Restaurant</label>
                            <input type="text" id="bill-vendor" class="form-control" placeholder="e.g. main_canteen" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Receipt / Event Name</label>
                            <input type="text" id="bill-desc" class="form-control" placeholder="e.g. Friday Lunch with Team" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Total Amount (LKR)</label>
                            <input type="number" id="bill-amount" class="form-control" placeholder="0.00" required>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <label class="form-label">Add Participants (Usernames)</label>
                            <div style="display: flex; gap: 0.5rem;">
                                <input type="text" id="participant-username" class="form-control" placeholder="Enter username">
                                <button type="button" onclick="App.addParticipant()" class="btn btn-outline">Add</button>
                            </div>
                        </div>
                        
                        <div id="participants-list" style="margin-bottom: 2rem;">
                            <!-- Participants will be listed here -->
                        </div>
                        
                        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1.25rem;">Create Split Request</button>
                    </form>
                </div>
            </div>
        `;
    },

    Recharge() {
        return `
            <div class="centered-layout">
                <div class="glass-panel auth-card animate-fade-in" style="width: 100%; max-width: 450px;">
                    <h3 style="text-align: center; margin-bottom: 2rem;">Request Top Up</h3>
                    <p style="color: var(--text-muted); text-align: center; margin-bottom: 2.5rem;">Enter the amount you wish to recharge. An Admin will review and approve your request.</p>
                    <form id="recharge-form">
                        <div class="form-group">
                            <label class="form-label">Amount (LKR)</label>
                            <input type="number" id="recharge-amount" class="form-control" placeholder="e.g. 500" required>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 1.25rem;">Submit Request</button>
                    </form>
                </div>
            </div>
        `;
    },

    ExpenseAnalytics(transactions) {
        return `
            <div class="container animate-fade-in" style="padding: 2rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem;">
                    <h2 class="text-gradient">Monthly Expense Report</h2>
                    <a href="#dashboard" class="btn btn-outline btn-sm">Back to Home</a>
                </div>

                <div class="dashboard-grid" style="grid-template-columns: 1fr 1.5fr;">
                    <div class="glass-panel" style="padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <h3 style="margin-bottom: 2rem;">Spend Distribution</h3>
                        <div style="width: 100%; max-width: 300px;">
                            <canvas id="expenseChart"></canvas>
                        </div>
                    </div>

                    <div class="glass-panel" style="padding: 2rem;">
                        <h3>Spending Breakdown</h3>
                        <div id="expense-summary-list" style="margin-top: 1.5rem;">
                            <!-- Injected by JS -->
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    Flash(message, type = 'info') {
        const id = 'flash-' + Date.now();
        const colors = {
            success: 'var(--success)',
            danger: 'var(--danger)',
            warning: 'var(--warning)',
            info: 'var(--primary)'
        };
        return `
            <div id="${id}" class="alert animate-fade-in" style="border-left-color: ${colors[type]}">
                <span>${message}</span>
                <button onclick="this.parentElement.remove()" style="background:none; border:none; color:white; cursor:pointer">&times;</button>
            </div>
        `;
    }
};
