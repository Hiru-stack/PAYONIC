import sys
import os
from datetime import datetime

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.curdir))

from app import create_app, db
from app.models import User, Wallet, Transaction, QRCode, Notification

app = create_app()

with app.app_context():
    print("--- User & Wallet Summary ---")
    users = User.query.all()
    for u in users:
        balance = u.wallet.balance if u.wallet else "N/A"
        print(f"ID: {u.id} | Name: {u.username} | Role: {u.role} | Balance: {balance} | MerchantID: {u.merchant_id}")
    
    print("\n--- Recent Transactions ---")
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(10).all()
    for t in transactions:
        print(f"ID: {t.id} | From: {t.sender.username} | To: {t.receiver.username} | Amount: {t.amount} | Status: {t.status} | Time: {t.timestamp}")
    
    print("\n--- Active QR Codes (Dynamic) ---")
    qrs = QRCode.query.filter_by(is_static=False).order_by(QRCode.created_at.desc()).limit(10).all()
    for q in qrs:
        print(f"ID: {q.id} | Vendor: {q.vendor.username} | Amount: {q.amount} | NumCode: {q.numeric_code} | Created: {q.created_at}")

    print("\n--- Recent Notifications ---")
    notifs = Notification.query.order_by(Notification.timestamp.desc()).limit(5).all()
    for n in notifs:
        print(f"To: {n.user.username} | Msg: {n.message} | Time: {n.timestamp}")
