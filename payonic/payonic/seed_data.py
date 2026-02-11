from app import create_app, db
from app.models import User, Wallet

app = create_app()

with app.app_context():
    print("Creating admin user...")
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@payonic.edu', role='admin', is_approved_vendor=True)
        db.session.add(admin)
        print("Creating new admin user...")
    
    admin.is_approved_vendor = True
    admin.set_password('2345')
    db.session.commit()
    print("Admin credentials verified: admin / 2345")

    print("Creating demo vendor...")
    vendor = User.query.filter_by(username='cafe').first()
    if not vendor:
        vendor = User(username='cafe', email='cafe@payonic.edu', role='vendor', is_approved_vendor=True)
        vendor.set_password('cafe123')
        db.session.add(vendor)
        db.session.commit()
        print("Vendor created: cafe / cafe123")
    
    vendor.is_approved_vendor = True
    if not vendor.wallet:
        w = Wallet(owner=vendor)
        db.session.add(w)
    db.session.commit()
    print("Vendor cafe status verified as approved.")
        
    print("Done.")
