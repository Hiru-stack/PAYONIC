import sys
import os
from datetime import datetime
from sqlalchemy import extract

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.curdir))

from app import create_app, db
from app.models import User, Transaction

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='hirusha').first()
    if not user:
        print("User 'hirusha' not found.")
    else:
        print(f"Checking transactions for {user.username} (ID: {user.id})")
        
        # Check all transactions for this user as sender
        txs = Transaction.query.filter_by(sender_id=user.id).all()
        print(f"Total transactions as sender: {len(txs)}")
        
        for t in txs:
            print(f"ID: {t.id} | Date: {t.timestamp} | Month: {t.timestamp.month} | Year: {t.timestamp.year}")
            
        # Test the exact filter used in the route
        month = datetime.utcnow().month
        year = datetime.utcnow().year
        print(f"\nTesting Filter: Month={month}, Year={year}")
        
        filtered = Transaction.query.filter(
            Transaction.sender_id == user.id,
            extract('month', Transaction.timestamp) == month,
            extract('year', Transaction.timestamp) == year
        ).all()
        
        print(f"Filtered transactions count: {len(filtered)}")
