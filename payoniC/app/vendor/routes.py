from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
import qrcode
import io
import uuid
import base64
from datetime import datetime
from app import db
from app.vendor import bp
from app.models import QRCode, Transaction, Wallet, User

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'vendor':
        return redirect(url_for('main.index'))
    
    # Calculate daily summaries? For now just show recent transactions.
    transactions = Transaction.query.filter_by(receiver_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(20).all()
    wallet = current_user.wallet
    
    # Get or create merchant_id for vendor
    if not current_user.merchant_id:
        # Generate merchant ID from username
        merchant_id = f"{current_user.username.upper()}-{current_user.id:04d}".replace(' ', '-')
        current_user.merchant_id = merchant_id
        db.session.commit()
    
    return render_template('vendor/dashboard.html', title='Vendor Dashboard', wallet=wallet, transactions=transactions, merchant_id=current_user.merchant_id)

@bp.route('/static_qr')
@login_required
def static_qr():
    if current_user.role != 'vendor':
        return redirect(url_for('main.index'))
    
    # Ensure vendor has merchant_id
    if not current_user.merchant_id:
        merchant_id = f"{current_user.username.upper()}-{current_user.id:04d}".replace(' ', '-')
        current_user.merchant_id = merchant_id
        db.session.commit()
    
    # Get or create static QR code
    static_qr = QRCode.query.filter_by(vendor_id=current_user.id, is_static=True).first()
    
    if not static_qr:
        # Create static QR with merchant_id as payload
        payload = f"STATIC:{current_user.merchant_id}"
        static_qr = QRCode(
            vendor_id=current_user.id,
            code_payload=payload,
            description=f"Static QR for {current_user.username}",
            is_static=True,
            amount=None  # No fixed amount for static QR
        )
        db.session.add(static_qr)
        db.session.commit()
    
    # Generate QR image
    img = qrcode.make(static_qr.code_payload, box_size=10, border=4)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_image = base64.b64encode(buf.getvalue()).decode('ascii')
    
    return render_template('vendor/static_qr.html', 
                         title='Static QR Code', 
                         qr_image=qr_image, 
                         merchant_id=current_user.merchant_id,
                         qr_payload=static_qr.code_payload)

@bp.route('/api/recent_payments')
@login_required
def recent_payments_api():
    """API endpoint for polling new transactions"""
    if current_user.role != 'vendor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get last_transaction_id from query params
    last_id = request.args.get('last_id', 0, type=int)
    
    # Fetch transactions newer than last_id
    new_transactions = Transaction.query.filter(
        Transaction.receiver_id == current_user.id,
        Transaction.id > last_id
    ).order_by(Transaction.timestamp.desc()).all()
    
    # Format transactions for JSON response
    transactions_data = []
    for t in new_transactions:
        sender = User.query.get(t.sender_id)
        transactions_data.append({
            'id': t.id,
            'amount': t.amount,
            'sender_name': sender.username if sender else 'Unknown',
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'description': t.description,
            'category': t.category
        })
    
    return jsonify({
        'transactions': transactions_data,
        'latest_id': new_transactions[0].id if new_transactions else last_id
    })

@bp.route('/generate_qr', methods=['GET', 'POST'])
@login_required
def generate_qr():
    if current_user.role != 'vendor':
        return redirect(url_for('main.index'))
    
    qr_data = None
    qr_image = None
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        description = request.form.get('description')
        category = request.form.get('category', 'General')
        
        # Create a unique payload
        payload = str(uuid.uuid4())
        
        # Generate a unique 6-digit numeric code
        import random
        numeric_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        # In a real app, we'd loop to ensure uniqueness
        
        new_qr = QRCode(vendor_id=current_user.id, code_payload=payload, numeric_code=numeric_code, amount=float(amount) if amount else None, description=description, category=category, is_static=False)
        db.session.add(new_qr)
        db.session.commit()
        
        # Generate the visual QR
        # We can embed the pay_url or just the payload. 
        # If we embed a URL, scanned on mobile it could open the system.
        # Let's simple embed the payload string for now.
        
        img = qrcode.make(payload)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        qr_image = base64.b64encode(buf.getvalue()).decode('ascii')
        qr_data = new_qr
        
    return render_template('vendor/generate_qr.html', title='Generate QR', qr_image=qr_image, qr_data=qr_data)

from app.vendor.forms import BankDetailsForm, PayoutRequestForm
from app.models import PayoutRequest

@bp.route('/settlement', methods=['GET', 'POST'])
@login_required
def settlement():
    if current_user.role != 'vendor':
        return redirect(url_for('main.index'))
    
    bank_form = BankDetailsForm(obj=current_user)
    payout_form = PayoutRequestForm()
    
    if 'bank_name' in request.form and bank_form.validate_on_submit():
        current_user.bank_name = bank_form.bank_name.data
        current_user.account_number = bank_form.account_number.data
        current_user.account_holder_name = bank_form.account_holder_name.data
        db.session.commit()
        flash('Bank details updated successfully.')
        return redirect(url_for('vendor.settlement'))
    
    if 'amount' in request.form and payout_form.validate_on_submit():
        if not current_user.bank_name or not current_user.account_number:
            flash('Please update your bank details before claiming earnings.')
            return redirect(url_for('vendor.settlement'))
            
        if current_user.wallet.balance < payout_form.amount.data:
            flash('Insufficient balance in wallet.')
        else:
            # Create Payout Request
            claim = PayoutRequest(
                vendor_id=current_user.id,
                amount=payout_form.amount.data,
                bank_name=current_user.bank_name,
                account_number=current_user.account_number,
                account_holder_name=current_user.account_holder_name
            )
            # We don't deduct wallet yet, we wait for admin approval
            db.session.add(claim)
            db.session.commit()
            flash('Payout request submitted for review.')
            return redirect(url_for('vendor.settlement'))

    payouts = PayoutRequest.query.filter_by(vendor_id=current_user.id).order_by(PayoutRequest.created_at.desc()).all()
    
    return render_template('vendor/settlement.html', 
                           title='Settlement & Payouts', 
                           bank_form=bank_form, 
                           payout_form=payout_form,
                           payouts=payouts)
