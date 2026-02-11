from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User, Wallet

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        if user.role == 'vendor' and not user.is_approved_vendor:
            flash('Your merchant account is pending administrator approval.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.role == 'student':
                next_page = url_for('main.dashboard') # Student home
            elif user.role == 'vendor':
                next_page = url_for('vendor.dashboard')
            elif user.role == 'admin':
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        is_approved = True if form.role.data in ['student', 'admin'] else False
        registration_number = form.registration_number.data if form.role.data == 'student' else None
        
        # Generate initial merchant_id for vendors
        generated_merchant_id = None
        if form.role.data == 'vendor':
            import uuid
            # Temporary merchant ID that will be refined once we have a user ID
            generated_merchant_id = f"PENDING-{uuid.uuid4().hex[:8].upper()}"

        user = User(
            username=form.username.data, 
            email=form.email.data, 
            role=form.role.data, 
            phone_number=form.phone.data,
            registration_number=registration_number,
            vendor_name=form.vendor_name.data if form.role.data == 'vendor' else None,
            business_name=form.business_name.data if form.role.data == 'vendor' else None,
            business_type=form.business_type.data if form.role.data == 'vendor' else None,
            is_approved_vendor=is_approved,
            merchant_id=generated_merchant_id
        )
        user.set_password(form.password.data)
        db.session.add(user)
        wallet = Wallet(owner=user)
        db.session.add(wallet)
        db.session.commit()
        
        if not is_approved:
            flash('Registration successful. Please wait for administrator approval before logging in.')
        else:
            flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)
