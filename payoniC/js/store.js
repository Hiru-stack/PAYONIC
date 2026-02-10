/**
 * Payonic Store - Handles LocalStorage persistence
 */
const Store = {
    // Keys
    KEYS: {
        USER: 'payonic_user',
        USERS: 'payonic_users',
        TRANSACTIONS: 'payonic_transactions',
        REQUESTS: 'payonic_recharge_requests',
        BILLS: 'payonic_split_bills'
    },

    // Initial Data
    init() {
        if (!localStorage.getItem(this.KEYS.USERS)) {
            // Seed default admin
            localStorage.setItem(this.KEYS.USERS, JSON.stringify([
                {
                    id: 1,
                    username: 'admin',
                    password: 'password',
                    role: 'admin',
                    email: 'admin@payonic.com',
                    wallet: 0
                }
            ]));
        }
        if (!localStorage.getItem(this.KEYS.TRANSACTIONS)) {
            localStorage.setItem(this.KEYS.TRANSACTIONS, JSON.stringify([]));
        }
        if (!localStorage.getItem(this.KEYS.REQUESTS)) {
            localStorage.setItem(this.KEYS.REQUESTS, JSON.stringify([]));
        }
    },

    // User Methods
    getCurrentUser() {
        const user = localStorage.getItem(this.KEYS.USER);
        return user ? JSON.parse(user) : null;
    },

    setCurrentUser(user) {
        localStorage.setItem(this.KEYS.USER, JSON.stringify(user));
    },

    logout() {
        localStorage.removeItem(this.KEYS.USER);
        window.location.reload();
    },

    getUsers() {
        return JSON.parse(localStorage.getItem(this.KEYS.USERS)) || [];
    },

    saveUser(user) {
        const users = this.getUsers();
        let index = users.findIndex(u => u.username === user.username);
        if (index > -1) {
            users[index] = { ...users[index], ...user };
        } else {
            user.id = user.id || Date.now();
            user.status = user.role === 'vendor' ? 'pending' : 'active';
            users.push(user);
        }
        localStorage.setItem(this.KEYS.USERS, JSON.stringify(users));

        const currentUser = this.getCurrentUser();
        if (currentUser && currentUser.username === user.username) {
            this.setCurrentUser({ ...currentUser, ...user });
        }
    },

    approveVendor(vendorId) {
        const users = this.getUsers();
        const index = users.findIndex(u => u.id === vendorId);
        if (index > -1 && users[index].role === 'vendor') {
            users[index].status = 'active';
            localStorage.setItem(this.KEYS.USERS, JSON.stringify(users));
            return true;
        }
        return false;
    },

    // Wallet & Transactions
    getTransactions(userId) {
        const all = JSON.parse(localStorage.getItem(this.KEYS.TRANSACTIONS)) || [];
        if (!userId) return all;
        return all.filter(t => t.senderId === userId || t.receiverId === userId);
    },

    addTransaction(transaction) {
        const all = JSON.parse(localStorage.getItem(this.KEYS.TRANSACTIONS)) || [];
        const users = this.getUsers();

        // Categorization logic
        const receiver = users.find(u => u.id === transaction.receiverId || u.username === transaction.receiverId);
        if (receiver && receiver.role === 'vendor') {
            transaction.category = receiver.businessType || 'other';
        } else {
            transaction.category = 'transfer';
        }

        transaction.id = Date.now();
        transaction.timestamp = new Date().toISOString();
        all.unshift(transaction);
        localStorage.setItem(this.KEYS.TRANSACTIONS, JSON.stringify(all));
        return transaction;
    },

    // Recharge Requests
    getRequests() {
        return JSON.parse(localStorage.getItem(this.KEYS.REQUESTS)) || [];
    },

    addRequest(userId, username, amount) {
        const requests = this.getRequests();
        const request = {
            id: Date.now(),
            userId,
            username,
            amount,
            status: 'pending',
            createdAt: new Date().toISOString()
        };
        requests.unshift(request);
        localStorage.setItem(this.KEYS.REQUESTS, JSON.stringify(requests));
        return request;
    },

    updateRequest(requestId, status, adminId) {
        const requests = this.getRequests();
        const index = requests.findIndex(r => r.id === requestId);
        if (index > -1) {
            requests[index].status = status;
            requests[index].reviewedAt = new Date().toISOString();
            requests[index].reviewedBy = adminId;
            localStorage.setItem(this.KEYS.REQUESTS, JSON.stringify(requests));

            // If approved, update user balance
            if (status === 'approved') {
                const users = this.getUsers();
                const userIndex = users.findIndex(u => u.id === requests[index].userId);
                if (userIndex > -1) {
                    users[userIndex].wallet += requests[index].amount;
                    this.saveUser(users[userIndex]);
                }
            }
        }
    },

    // Split Bills
    getBills() {
        return JSON.parse(localStorage.getItem(this.KEYS.BILLS)) || [];
    },

    createBill(creatorId, totalAmount, description, participants) {
        const bills = this.getBills();
        const bill = {
            id: Date.now(),
            creatorId,
            totalAmount,
            description,
            status: 'pending',
            createdAt: new Date().toISOString(),
            participants: participants.map(p => ({
                id: p.id,
                username: p.username,
                amountOwed: p.amount,
                status: 'pending'
            }))
        };
        bills.unshift(bill);
        localStorage.setItem(this.KEYS.BILLS, JSON.stringify(bills));
        return bill;
    }
};

Store.init();
