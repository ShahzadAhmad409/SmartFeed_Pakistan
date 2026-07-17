from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Donation, NGORequest
from app.auth import get_password_hash
from datetime import datetime, timedelta, timezone

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Passwords
    hashed_pw = get_password_hash("password123")

    # 1. SuperAdmin
    superadmin = User(username="admin", password_hash=hashed_pw, role="superadmin", organization_name="SmartFeed Admin")
    db.add(superadmin)

    # 2. Donors
    donor1 = User(username="donor_karachi", password_hash=hashed_pw, role="donor", organization_name="Karachi Bakery", city="Karachi")
    donor2 = User(username="donor_lahore", password_hash=hashed_pw, role="donor", organization_name="Lahore Wedding Hall", city="Lahore")
    db.add_all([donor1, donor2])
    db.commit()

    # 3. Receiver
    receiver1 = User(username="receiver1", password_hash=hashed_pw, role="receiver", city="Karachi")
    db.add(receiver1)
    db.commit()

    # 4. Donations (Karachi coordinates approx 24.8607, 67.0011)
    # Available - Karachi
    d1 = Donation(
        food_name="Leftover Biryani", category="Cooked Meals", quantity=50, hours_before_expiry=5,
        lat=24.8607, lng=67.0011, donor_id=donor1.id
    )
    # Expiring soon - Karachi
    d2 = Donation(
        food_name="Bread and Buns", category="Baked Goods", quantity=20, hours_before_expiry=2,
        lat=24.8700, lng=67.0200, donor_id=donor1.id
    )
    # Available - Lahore (approx 31.5204, 74.3587)
    d3 = Donation(
        food_name="Wedding Buffet Leftovers", category="Cooked Meals", quantity=200, hours_before_expiry=10,
        lat=31.5204, lng=74.3587, donor_id=donor2.id
    )
    
    # Already expired donation (created 10 hours ago, expires in 5)
    d4 = Donation(
        food_name="Expired Sandwiches", category="Cooked Meals", quantity=10, hours_before_expiry=5,
        lat=24.8600, lng=67.0000, donor_id=donor1.id
    )
    d4.created_at = datetime.now(timezone.utc) - timedelta(hours=10)
    
    db.add_all([d1, d2, d3, d4])
    db.commit()

    # 5. NGO Request
    ngo_req = NGORequest(
        organization_name="Edhi Foundation Demo", registration_number="REG-12345", 
        contact_info="info@edhi.demo", city="Karachi"
    )
    db.add(ngo_req)
    db.commit()

    print("Database seeded with sample data.")
    print("SuperAdmin login -> user: admin, pass: password123")
    print("Donor login -> user: donor_karachi, pass: password123")
    print("Receiver login -> user: receiver1, pass: password123")
    
    db.close()

if __name__ == "__main__":
    seed()
