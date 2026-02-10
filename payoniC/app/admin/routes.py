from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app import db
from app.models import User, Transaction, Wallet

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    
    total_users = User.query.count()
    total_transactions = Transaction.query.count()
    
    wallets = Wallet.query.all()
    total_system_balance = sum([w.balance for w in wallets])
    
    pending_recharges = RechargeRequest.query.filter_by(status='pending').count()
    pending_vendors_count = User.query.filter_by(role='vendor', is_approved_vendor=False).count()
    total_pending_actions = pending_recharges + pending_vendors_count

    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard', 
                           users=users, 
                           transactions=transactions,
                           total_users=total_users,
                           total_transactions=total_transactions,
                           total_system_balance=total_system_balance,
                           total_pending_actions=total_pending_actions)

@bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('admin/users.html', title='User Management', users=users)

@bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(id)
    # Import locally to avoid circular import if placed at top level before bp definition? 
    # Actually bp is defined in __init__.py so safe.
    from app.admin.forms import UserEditForm 
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@bp.route('/user/<int:id>/delete')
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users'))

@bp.route('/recharge', methods=['GET', 'POST'])
@login_required
def recharge():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    from app.admin.forms import RechargeForm
    form = RechargeForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.wallet:
            user.wallet.balance += form.amount.data
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/recharge.html', title='Recharge Wallet', form=form)

from datetime import datetime
from app.models import RechargeRequest

@bp.route('/requests')
@login_required
def requests():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    pending_requests = RechargeRequest.query.filter_by(status='pending').order_by(RechargeRequest.created_at.desc()).all()
    return render_template('admin/requests.html', title='Recharge Requests', requests=pending_requests)

@bp.route('/request/<int:id>/approve', methods=['POST'])
@login_required
def approve_request(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    req = RechargeRequest.query.get_or_404(id)
    if req.status != 'pending':
        flash('Request already processed.')
        return redirect(url_for('admin.requests'))
        
    req.status = 'approved'
    req.reviewed_at = datetime.utcnow()
    req.reviewed_by = current_user.id
    
    # Update Wallet
    user = User.query.get(req.user_id)
    user.wallet.balance += req.amount
    
    # Record Transaction
    t = Transaction(
        sender_id=current_user.id, # Admin as sender
        receiver_id=user.id,
        amount=req.amount,
        description='Wallet Recharge (Approved)',
        status='completed'
    )
    db.session.add(t)
    db.session.commit()
    
    flash(f'Request approved. LKR {req.amount} added to {user.username}.')
    return redirect(url_for('admin.requests'))

@bp.route('/request/<int:id>/reject', methods=['POST'])
@login_required
def reject_request(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    req = RechargeRequest.query.get_or_404(id)
    if req.status != 'pending':
        flash('Request already processed.')
        return redirect(url_for('admin.requests'))
        
    req.status = 'rejected'
    req.reviewed_at = datetime.utcnow()
    req.reviewed_by = current_user.id
    
    db.session.commit()
    flash('Request rejected.')
    return redirect(url_for('admin.requests'))

@bp.route('/vendors/pending')
@login_required
def pending_vendors():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    vendors = User.query.filter_by(role='vendor', is_approved_vendor=False).all()
    return render_template('admin/pending_vendors.html', title='Vendor Approvals', vendors=vendors)

@bp.route('/vendor/<int:id>/approve', methods=['POST'])
@login_required
def approve_vendor(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    vendor = User.query.get_or_404(id)
    vendor.is_approved_vendor = True
    db.session.commit()
    flash(f'Vendor {vendor.username} approved.')
    return redirect(url_for('admin.pending_vendors'))

@bp.route('/vendor/<int:id>/reject', methods=['POST'])
@login_required
def reject_vendor(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    vendor = User.query.get_or_404(id)
    # For rejection, we might want to delete or keep as unapproved.
    # User said "approve it", let's keep it simple and just delete or flag. 
    # Deleting is cleaner for "rejecting registration".
    db.session.delete(vendor)
    db.session.commit()
    flash(f'Vendor {vendor.username} rejected and removed.')
    return redirect(url_for('admin.pending_vendors'))
from app.models import PayoutRequest

@bp.route('/payouts')
@login_required
def payouts():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    pending_payouts = PayoutRequest.query.filter_by(status='pending').order_by(PayoutRequest.created_at.desc()).all()
    all_payouts = PayoutRequest.query.order_by(PayoutRequest.created_at.desc()).limit(50).all()
    
    return render_template('admin/payout_requests.html', 
                           title='Vendor Payouts', 
                           pending_payouts=pending_payouts,
                           all_payouts=all_payouts)

@bp.route('/payout/<int:id>/approve', methods=['POST'])
@login_required
def approve_payout(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    payout = PayoutRequest.query.get_or_404(id)
    if payout.status != 'pending':
        flash('Request already processed.')
        return redirect(url_for('admin.payouts'))
        
    vendor = User.query.get(payout.vendor_id)
    if vendor.wallet.balance < payout.amount:
        flash('Vendor has insufficient funds for this payout.')
        return redirect(url_for('admin.payouts'))
        
    # Process Payout
    vendor.wallet.balance -= payout.amount
    payout.status = 'approved'
    payout.reviewed_at = datetime.utcnow()
    payout.reviewed_by = current_user.id
    
    # Optional: Log as a separate type of transaction
    t = Transaction(
        sender_id=vendor.id, # Deducted from vendor
        receiver_id=current_user.id, # "Received" by system/admin for bank transfer
        amount=payout.amount,
        description=f'Payout Settlement: {payout.bank_name}',
        status='completed',
        category='Settlement'
    )
    db.session.add(t)
    db.session.commit()
    
    flash(f'Payout of LKR {payout.amount} approved for {vendor.username}. Funds deducted from wallet.')
    return redirect(url_for('admin.payouts'))

@bp.route('/payout/<int:id>/reject', methods=['POST'])
@login_required
def reject_payout(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    payout = PayoutRequest.query.get_or_404(id)
    if payout.status != 'pending':
        flash('Request already processed.')
        return redirect(url_for('admin.payouts'))
        
    payout.status = 'rejected'
    payout.reviewed_at = datetime.utcnow()
    payout.reviewed_by = current_user.id
    
    db.session.commit()
    flash('Payout request rejected.')
    return redirect(url_for('admin.payouts'))

@bp.route('/vendor/<int:id>/audit')
@login_required
def audit_vendor(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    vendor = User.query.get_or_404(id)
    if vendor.role != 'vendor':
        flash('User is not a vendor.')
        return redirect(url_for('admin.users'))
        
    transactions = Transaction.query.filter_by(receiver_id=vendor.id).order_by(Transaction.timestamp.desc()).all()
    payouts = PayoutRequest.query.filter_by(vendor_id=vendor.id).order_by(PayoutRequest.created_at.desc()).all()
    
    return render_template('admin/audit_vendor.html', 
                           title=f'Audit: {vendor.username}', 
                           vendor=vendor, 
                           transactions=transactions, 
                           payouts=payouts)

from app.models import ScheduledTopup

@bp.route('/scheduled-topups')
@login_required
def manage_scheduled_topups():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    pending_schedules = ScheduledTopup.query.filter_by(status='pending').order_by(ScheduledTopup.created_at.desc()).all()
    all_schedules = ScheduledTopup.query.order_by(ScheduledTopup.created_at.desc()).limit(50).all()
    
    return render_template('admin/scheduled_topups.html', 
                           title='Scheduled Top-ups', 
                           pending_schedules=pending_schedules,
                           all_schedules=all_schedules)

@bp.route('/scheduled-topup/<int:id>/approve', methods=['POST'])
@login_required
def approve_scheduled_topup(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    schedule = ScheduledTopup.query.get_or_404(id)
    if schedule.status != 'pending':
        flash('Schedule already processed.')
        return redirect(url_for('admin.manage_scheduled_topups'))
        
    schedule.status = 'approved'
    schedule.reviewed_at = datetime.utcnow()
    schedule.reviewed_by = current_user.id
    schedule.is_active = True
    
    db.session.commit()
    flash(f'Scheduled top-up for {schedule.user.username} (LKR {schedule.amount}) approved.')
    return redirect(url_for('admin.manage_scheduled_topups'))

@bp.route('/scheduled-topup/<int:id>/reject', methods=['POST'])
@login_required
def reject_scheduled_topup(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    schedule = ScheduledTopup.query.get_or_404(id)
    if schedule.status != 'pending':
        flash('Schedule already processed.')
        return redirect(url_for('admin.manage_scheduled_topups'))
        
    schedule.status = 'rejected'
    schedule.reviewed_at = datetime.utcnow()
    schedule.reviewed_by = current_user.id
    schedule.is_active = False # Deactivate on rejection
    
    db.session.commit()
    flash(f'Scheduled top-up for {schedule.user.username} rejected.')
    return redirect(url_for('admin.manage_scheduled_topups'))
