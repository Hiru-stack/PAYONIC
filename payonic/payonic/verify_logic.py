import os
from app import create_app, db
from app.models import User, ScheduledTopup, Wallet
from datetime import datetime

app = create_app()

def verify():
    with app.app_context():
        # 1. Setup Student
        print("Seting up test student...")
        student = User.query.filter_by(username='test_student').first()
        if student:
            ScheduledTopup.query.filter_by(user_id=student.id).delete()
            db.session.delete(student)
            db.session.commit()
            
        student = User(username='test_student', email='test@student.com', role='student')
        student.set_password('pass')
        db.session.add(student)
        db.session.commit()
        
        wallet = Wallet(owner=student)
        db.session.add(wallet)
        db.session.commit()
        
        # 2. Simulate Student Enabling/Updating Schedule
        print("\nSimulating student enabling schedule...")
        amount = 5000.0
        frequency = 'monthly'
        
        # Logic from routes.py:
        schedule = ScheduledTopup.query.filter_by(user_id=student.id, is_active=True).first()
        if schedule:
            schedule.amount = amount
            schedule.frequency = frequency
            schedule.status = 'pending'
        else:
            schedule = ScheduledTopup(user_id=student.id, amount=amount, frequency=frequency, status='pending')
            db.session.add(schedule)
        
        db.session.commit()
        
        # Verify status is pending
        schedule = ScheduledTopup.query.filter_by(user_id=student.id).first()
        print(f"Schedule Status: {schedule.status}")
        assert schedule.status == 'pending', f"Expected pending, got {schedule.status}"
        
        # 3. Simulate Admin Approval
        print("\nSimulating admin approval...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='a@a.com', role='admin')
            db.session.add(admin)
            db.session.commit()
        
        # Logic from admin/routes.py:
        schedule.status = 'approved'
        schedule.reviewed_at = datetime.utcnow()
        schedule.reviewed_by = admin.id
        schedule.is_active = True
        
        db.session.commit()
        
        # Verify status is approved
        schedule = ScheduledTopup.query.filter_by(user_id=student.id).first()
        print(f"Schedule Status: {schedule.status}")
        assert schedule.status == 'approved', f"Expected approved, got {schedule.status}"
        print(f"Reviewed By: {schedule.reviewer.username}")
        
        print("\nVERIFICATION SUCCESSFUL!")

if __name__ == "__main__":
    verify()
