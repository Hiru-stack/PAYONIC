from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import extract
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app import db
from app.main import bp
from app.models import Wallet, Transaction, User, Notification
from app.main.forms import UpdateProfileForm, ChangePasswordForm

def create_notification(user_id, message, type='info'):
    n = Notification(user_id=user_id, message=message, type=type)
    db.session.add(n)
    db.session.commit()

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('main.dashboard'))
        elif current_user.role == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html', title='Welcome to Payonic')

@bp.route('/student/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied.')
        return redirect(url_for('main.index'))
    
    wallet = current_user.wallet
    transactions = Transaction.query.filter(
        (Transaction.sender_id == current_user.id) | 
        (Transaction.receiver_id == current_user.id)
    ).order_by(Transaction.timestamp.desc()).all()
    
    return render_template('student/dashboard.html', title='Dashboard', wallet=wallet, transactions=transactions)

from app.models import QRCode, User, ScheduledTopup, RechargeRequest

@bp.route('/student/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        topup_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        
        if topup_type == 'instant':
            if amount > 0:
                # Create Verification Request
                req = RechargeRequest(user_id=current_user.id, amount=amount)
                db.session.add(req)
                db.session.commit()
                flash(f'Recharge request for LKR {amount} submitted for admin verification.')
                return redirect(url_for('main.dashboard'))
                
        elif topup_type == 'schedule':
            frequency = request.form.get('frequency')
            
            # Check for existing
            schedule = ScheduledTopup.query.filter_by(user_id=current_user.id, is_active=True).first()
            if schedule:
                schedule.amount = amount
                schedule.frequency = frequency
                schedule.status = 'pending' # Require re-approval
                flash('Schedule updated successfully. Pending admin approval.')
            else:
                schedule = ScheduledTopup(user_id=current_user.id, amount=amount, frequency=frequency, status='pending')
                db.session.add(schedule)
                flash('Auto-topup scheduled enabled. Pending admin approval.')
            
            db.session.commit()
            return redirect(url_for('main.topup'))

    # Get active schedule to display
    active_schedule = ScheduledTopup.query.filter_by(user_id=current_user.id, is_active=True).first()
    return render_template('student/topup.html', title='Wallet Settings', active_schedule=active_schedule)

@bp.route('/student/schedule/cancel', methods=['POST'])
@login_required
def cancel_schedule():
    schedule = ScheduledTopup.query.filter_by(user_id=current_user.id, is_active=True).first()
    if schedule:
        schedule.is_active = False
        db.session.commit()
        flash('Scheduled top-up disabled.')
    return redirect(url_for('main.topup'))
    
from app.models import QRCode, User

@bp.route('/student/pay', methods=['GET', 'POST'])
@login_required
def pay():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
        
    # Step 1: Input Code (Simulate Scan or Manual Entry)
    if request.method == 'GET':
        code = request.args.get('code')
        if not code:
            return render_template('student/pay.html', title='Scan QR')
        
        print(f"DEBUG: Processing GET /student/pay with code: {code}")
        
        # Check if it's a numeric code (6 digits)
        is_numeric = code.isdigit() and len(code) == 6
        is_static = code.startswith('STATIC:')
        
        qr = None
        vendor = None
        
        if is_numeric:
            qr = QRCode.query.filter_by(numeric_code=code).first()
            if not qr:
                flash(f'Invalid Numeric Code: {code}')
                return redirect(url_for('main.pay'))
            vendor = User.query.get(qr.vendor_id)
            is_static = False
        elif is_static:
            merchant_id = code.replace('STATIC:', '')
            vendor = User.query.filter_by(merchant_id=merchant_id).first()
            if not vendor:
                flash(f'Merchant not found: {merchant_id}')
                return redirect(url_for('main.pay'))
            
            # Temporary object for static QR
            qr = type('obj', (object,), {
                'is_static': True,
                'vendor_id': vendor.id,
                'amount': None,
                'description': f'Payment to {vendor.username}',
                'category': 'General',
                'code_payload': code
            })()
        else:
            qr = QRCode.query.filter_by(code_payload=code).first()
            if not qr:
                flash('Invalid QR Code Payload.')
                return redirect(url_for('main.pay'))
            vendor = User.query.get(qr.vendor_id)
            is_static = False
            
        if not vendor:
            flash('Error identifying vendor.')
            return redirect(url_for('main.pay'))
            
        return render_template('student/confirm_pay.html', title='Confirm Payment', qr=qr, vendor=vendor, is_static=is_static)
        
    # Step 3: Process Payment
    elif request.method == 'POST':
        code = request.form.get('code')
        amount_str = request.form.get('amount')
        
        print(f"DEBUG: Processing POST /student/pay with code: {code}, amount: {amount_str}")
        
        if not code:
            flash('Missing payment code.')
            return redirect(url_for('main.pay'))
            
        # Check if numeric, static, or raw payload
        is_numeric = code.isdigit() and len(code) == 6
        is_static = code.startswith('STATIC:')
        
        qr = None
        vendor = None
        
        if is_numeric:
            qr = QRCode.query.filter_by(numeric_code=code).first()
        elif is_static:
            merchant_id = code.replace('STATIC:', '')
            vendor = User.query.filter_by(merchant_id=merchant_id).first()
        else:
            qr = QRCode.query.filter_by(code_payload=code).first()

        if not qr and not vendor:
            flash('Session expired or invalid code.')
            return redirect(url_for('main.pay'))
            
        if not vendor:
            vendor = User.query.get(qr.vendor_id)
            
        if not vendor:
            flash('Vendor not found.')
            return redirect(url_for('main.pay'))

        # Determine final amount
        try:
            if amount_str:
                final_amount = float(amount_str)
            elif qr and qr.amount:
                final_amount = qr.amount
            else:
                flash('Amount is required.')
                return redirect(url_for('main.pay', code=code))
        except (ValueError, TypeError):
            flash(f'Invalid amount entered: {amount_str}')
            return redirect(url_for('main.pay', code=code))
            
        description = f"Payment to {vendor.username}"
        if qr and not is_static and qr.description:
            description += f": {qr.description}"
        category = qr.category if (qr and not is_static and qr.category) else 'General'
        
        if final_amount <= 0:
            flash('Amount must be greater than zero.')
            return redirect(url_for('main.pay', code=code))
            
        if current_user.wallet.balance < final_amount:
            flash(f'Insufficient funds. Your balance is LKR {current_user.wallet.balance:.2f}')
            return redirect(url_for('main.pay', code=code))
            
        # Execute Transfer
        try:
            current_user.wallet.balance -= final_amount
            vendor.wallet.balance += final_amount
            
            t = Transaction(
                sender_id=current_user.id,
                receiver_id=vendor.id,
                amount=final_amount,
                description=description,
                category=category,
                status='completed'
            )
            db.session.add(t)
            
            # Create Notifications (without committing yet)
            n1 = Notification(user_id=current_user.id, message=f"You sent LKR {final_amount:.2f} to {vendor.username}", type="success")
            n2 = Notification(user_id=vendor.id, message=f"You received LKR {final_amount:.2f} from {current_user.username}", type="success")
            db.session.add_all([n1, n2])
            
            db.session.commit()
            print(f"DEBUG: Transaction {t.id} completed successfully.")
            
            return redirect(url_for('main.payment_success', 
                                   transaction_id=t.id,
                                   vendor_name=vendor.username,
                                   amount=final_amount))
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Transaction failed: {str(e)}")
            flash(f'Transaction failed: {str(e)}')
            return redirect(url_for('main.pay'))

    return "Error"

@bp.route('/student/payment_success')
@login_required
def payment_success():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
    
    transaction_id = request.args.get('transaction_id', type=int)
    vendor_name = request.args.get('vendor_name')
    amount = request.args.get('amount', type=float)
    
    # Generate reference number
    ref_number = f"PAY-{transaction_id:05d}" if transaction_id else "PAY-00000"
    
    return render_template('student/payment_success.html',
                         title='Payment Successful',
                         vendor_name=vendor_name,
                         amount=amount,
                         ref_number=ref_number)

@bp.route('/student/reports')
@login_required
def reports():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
        
    now = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)
    
    expenses = Transaction.query.filter(
        Transaction.sender_id == current_user.id,
        extract('month', Transaction.timestamp) == month,
        extract('year', Transaction.timestamp) == year
    ).all()
    
    total_spent = sum([t.amount for t in expenses])
    
    return render_template('student/reports.html', 
                           expenses=expenses, 
                           total_spent=total_spent, 
                           month=month, 
                           year=year,
                           now=now,
                           datetime=datetime)

import csv
from io import StringIO
from flask import Response

@bp.route('/student/download_statement')
@login_required
def download_statement():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
    
    now = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)
    
    try:
        month_name = datetime(year, month, 1).strftime('%B')
    except (ValueError, TypeError):
        month_name = "Unknown"
    
    expenses = Transaction.query.filter(
        Transaction.sender_id == current_user.id,
        extract('month', Transaction.timestamp) == month,
        extract('year', Transaction.timestamp) == year
    ).order_by(Transaction.timestamp.desc()).all()
    
    # Use StringIO to build the CSV
    data = StringIO()
    # Add BOM for Excel compatibility (UTF-8)
    data.write('\ufeff')
    writer = csv.writer(data)
    
    # Header Info
    writer.writerow(['PAYONIC MONTHLY SPENDING REPORT'])
    writer.writerow(['User', current_user.username])
    writer.writerow(['Period', f"{month_name} {year}"])
    writer.writerow(['Generated At', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Summary Section
    writer.writerow(['SPENDING SUMMARY BY CATEGORY'])
    category_totals = {}
    total_sum = 0
    for t in expenses:
        cat = t.category or 'General'
        category_totals[cat] = category_totals.get(cat, 0) + t.amount
        total_sum += t.amount
        
    writer.writerow(['Category', 'Total Amount (LKR)'])
    for cat, amount in category_totals.items():
        writer.writerow([cat, f"{amount:.2f}"])
    writer.writerow(['TOTAL SPENT', f"{total_sum:.2f}"])
    writer.writerow([])
    
    # Detailed Transactions
    writer.writerow(['DETAILED TRANSACTION LOG'])
    writer.writerow(['Date', 'Recipient', 'Category', 'Description', 'Amount (LKR)'])
    
    for t in expenses:
        recipient = t.receiver.username if t.receiver else "Unknown"
        writer.writerow([
            t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            recipient,
            t.category or 'General',
            t.description or 'No description',
            f"{t.amount:.2f}"
        ])

    filename = f"Payonic_Report_{current_user.username}_{year}_{month:02d}.csv"
    
    response = Response(
        data.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
    return response

from app.models import SplitBill, SplitBillParticipant
from app.main.forms import SplitBillForm

def _get_split_bill_context(form=None):
    if form is None:
        form = SplitBillForm()
    
    # Incoming requests (where I am a participant and pending)
    incoming_requests = SplitBillParticipant.query.filter_by(user_id=current_user.id, status='pending').all()
    
    # My created requests
    my_requests = SplitBill.query.filter_by(creator_id=current_user.id).order_by(SplitBill.created_at.desc()).all()
    
    # Summary stats
    total_you_owe = sum(p.amount_owed for p in incoming_requests)
    
    pending_collection = 0
    for bill in my_requests:
        for p in bill.participants:
            if p.status == 'pending':
                pending_collection += p.amount_owed
                
    return {
        'title': 'Split Bill',
        'form': form,
        'incoming_requests': incoming_requests,
        'my_requests': my_requests,
        'total_you_owe': total_you_owe,
        'pending_collection': pending_collection
    }

@bp.route('/student/split', methods=['GET', 'POST'])
@login_required
def split_bill():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
    
    context = _get_split_bill_context()
    return render_template('student/split_bill.html', **context)

@bp.route('/student/split/create', methods=['POST'])
@login_required
def create_split():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))
    
    form = SplitBillForm()
    if form.validate_on_submit():
        # Parse participants
        usernames = [u.strip() for u in form.participants.data.split(',') if u.strip()]
        valid_users = []
        for uname in usernames:
            u = User.query.filter_by(username=uname).first()
            if u and u.id != current_user.id:
                valid_users.append(u)
        
        if not valid_users:
            flash('No valid participants found. Please check usernames.')
            context = _get_split_bill_context(form)
            return render_template('student/split_bill.html', **context)

        total_split_count = len(valid_users) + 1 # including self
        amount_per_person = form.total_amount.data / total_split_count
        
        try:
            bill = SplitBill(
                creator_id=current_user.id,
                total_amount=form.total_amount.data,
                description=form.description.data,
                status='pending'
            )
            db.session.add(bill)
            db.session.flush() # get ID
            
            # Add participants
            for u in valid_users:
                p = SplitBillParticipant(
                    bill_id=bill.id,
                    user_id=u.id,
                    amount_owed=amount_per_person,
                    status='pending'
                )
                db.session.add(p)
                
                # Notify each participant
                create_notification(u.id, f"{current_user.username} requested LKR {amount_per_person:.2f} for: {bill.description}", "info")
                
            db.session.commit()
            flash('Split bill request created successfully!')
            return redirect(url_for('main.split_bill'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating split bill: {str(e)}')
            context = _get_split_bill_context(form)
            return render_template('student/split_bill.html', **context)
            
    # If validation fails
    context = _get_split_bill_context(form)
    return render_template('student/split_bill.html', **context)

@bp.route('/student/split/<int:id>/pay', methods=['POST'])
@login_required
def pay_split(id):
    participant = SplitBillParticipant.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if participant.status == 'paid':
        flash('Already paid.')
        return redirect(url_for('main.split_bill'))
        
    amount = participant.amount_owed
    
    if current_user.wallet.balance < amount:
        flash('Insufficient funds.')
        return redirect(url_for('main.split_bill'))
        
    bill = SplitBill.query.get(participant.bill_id)
    creator = User.query.get(bill.creator_id)
    
    current_user.wallet.balance -= amount
    creator.wallet.balance += amount
    
    participant.status = 'paid'
    
    # Record transaction
    t = Transaction(
        sender_id=current_user.id,
        receiver_id=creator.id,
        amount=amount,
        description=f"Split Bill Payment: {bill.description}",
        status='completed'
    )
    db.session.add(t)
    
    # Create Notifications
    create_notification(current_user.id, f"You paid LKR {amount:.2f} for split bill: {bill.description}", "success")
    create_notification(creator.id, f"{current_user.username} paid their share of LKR {amount:.2f} for: {bill.description}", "info")
    
    db.session.commit()
    
    flash('Paid split bill share successfully.')
    return redirect(url_for('main.split_bill'))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    
    if 'update_profile' in request.form and profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.phone_number = profile_form.phone_number.data
        
        if profile_form.profile_pic.data:
            file = profile_form.profile_pic.data
            filename = secure_filename(f"user_{current_user.id}_{file.filename}")
            filepath = os.path.join('app', 'static', 'uploads', 'profile_pics', filename)
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            current_user.profile_pic = f"uploads/profile_pics/{filename}"
            
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('main.settings'))

    if 'change_password' in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.old_password.data):
            current_user.set_password(password_form.password.data)
            db.session.commit()
            flash('Password changed successfully.')
            return redirect(url_for('main.settings'))
        else:
            flash('Invalid current password.')
            
    return render_template('main/settings.html', title='Settings', profile_form=profile_form, password_form=password_form)

@bp.route('/notifications')
@login_required
def notifications():
    notifications = current_user.notifications.order_by(Notification.timestamp.desc()).all()
    return render_template('main/notifications.html', title='Notifications', notifications=notifications)

@bp.route('/notifications/read-all')
@login_required
def read_all_notifications():
    current_user.notifications.filter_by(is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return redirect(url_for('main.notifications'))
