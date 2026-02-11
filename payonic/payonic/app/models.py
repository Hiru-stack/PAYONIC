from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # student, vendor, admin
    is_active_user = db.Column(db.Boolean, default=True)
    
    # Phase 2: Profile Fields
    # Role-specific fields
    phone_number = db.Column(db.String(20))
    registration_number = db.Column(db.String(50)) # For students
    student_id = db.Column(db.String(20)) # Internal ID
    vendor_name = db.Column(db.String(100)) # For vendors
    business_name = db.Column(db.String(100)) # For vendors
    business_type = db.Column(db.String(50)) # For vendors
    is_approved_vendor = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(255))
    merchant_id = db.Column(db.String(50), unique=True)
    
    # Bank Details for Payouts
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    account_holder_name = db.Column(db.String(100))

    wallet = db.relationship('Wallet', backref='owner', uselist=False, lazy=True)
    sent_transactions = db.relationship('Transaction', foreign_keys='Transaction.sender_id', backref='sender', lazy='dynamic')
    received_transactions = db.relationship('Transaction', foreign_keys='Transaction.receiver_id', backref='receiver', lazy='dynamic')
    qr_codes = db.relationship('QRCode', backref='vendor', lazy='dynamic')
    payout_requests = db.relationship('PayoutRequest', foreign_keys='PayoutRequest.vendor_id', backref='vendor', lazy='dynamic')
    
    # Advanced Phase: Security & Budgeting
    two_factor_enabled = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(32))
    low_balance_threshold = db.Column(db.Float, default=100.0) # LKR
    
    # Relationships for New Modules
    refund_requests = db.relationship('RefundRequest', foreign_keys='RefundRequest.user_id', backref='requester', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic')
    
    # Relationships for Split Bills
    created_bills = db.relationship('SplitBill', backref='creator', lazy='dynamic')
    split_participations = db.relationship('SplitBillParticipant', backref='user', lazy='dynamic')
    
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_user

    @property
    def unread_notification_count(self):
        return self.notifications.filter_by(is_read=False).count()

    @property
    def lifetime_earnings(self):
        if self.role != 'vendor':
            return 0.0
        # Sum of all completed transactions received by this vendor
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.receiver_id == self.id,
            Transaction.status == 'completed'
        ).scalar()
        return total if total else 0.0

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(20), default='info') # info, success, warning, danger

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='General') # Food, Education, etc.
    status = db.Column(db.String(20), default='completed') # completed, failed, pending

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code_payload = db.Column(db.String(256), unique=True, nullable=False)
    numeric_code = db.Column(db.String(6), unique=True, nullable=True) # 6-digit code for manual entry
    amount = db.Column(db.Float, nullable=True) # Optional fixed amount
    description = db.Column(db.String(128))
    category = db.Column(db.String(50), default='General')
    is_static = db.Column(db.Boolean, default=False) # True for static vendor QR, False for dynamic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SplitBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending') # pending, completed, cancelled
    
    participants = db.relationship('SplitBillParticipant', backref='bill', lazy='dynamic')

class SplitBillParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('split_bill.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_owed = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, paid, rejected

class ScheduledTopup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), default='monthly') # monthly, weekly
    next_run_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='scheduled_topups')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class RechargeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='recharge_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class PayoutRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Snapshot of bank details at time of request
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    account_holder_name = db.Column(db.String(100))

    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class RefundRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # The student requesting
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    transaction = db.relationship('Transaction', backref='refund_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., Canteen, Transport
    limit_amount = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0.0)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
