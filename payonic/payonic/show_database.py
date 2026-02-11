import sys
import os
from datetime import datetime

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.curdir))

from app import create_app, db
from app.models import User, Wallet, Transaction, QRCode

app = create_app()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

with app.app_context():
    clear_screen()
    print("====================================================")
    print("          PAYONIC LIVE DATABASE MONITOR             ")
    print("====================================================")
    
    print("\n[ REGISTERED USERS & WALLET BALANCES ]")
    print("-" * 52)
    print(f"{'Username':<15} | {'Role':<10} | {'Balance (LKR)':<15}")
    print("-" * 52)
    users = User.query.all()
    for u in users:
        balance = f"{u.wallet.balance:,.2f}" if u.wallet else "0.00"
        print(f"{u.username:<15} | {u.role:<10} | {balance:<15}")
    
    print("\n\n[ RECENT TRANSACTIONS ]")
    print("-" * 75)
    print(f"{'From':<12} | {'To':<12} | {'Amount':<10} | {'Description':<25}")
    print("-" * 75)
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(8).all()
    for t in transactions:
        print(f"{t.sender.username:<12} | {t.receiver.username:<12} | {t.amount:<10.2f} | {t.description[:25]:<25}")
    
    print("\n====================================================")
    print(f" Last Updated: {datetime.now().strftime('%H:%M:%S')} ")
    print("====================================================")
