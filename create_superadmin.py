import getpass
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_superadmin():
    db: Session = SessionLocal()
    print("--- Create Super-Admin Account ---")
    username = input("Username: ")
    
    # Check if exists
    if db.query(User).filter(User.username == username).first():
        print(f"Error: User '{username}' already exists.")
        db.close()
        return

    password = getpass.getpass("Password: ")
    org_name = input("Organization Name (e.g. SmartFeed Platform): ")
    
    hashed = get_password_hash(password)
    
    new_superadmin = User(
        username=username,
        password_hash=hashed,
        role="superadmin",
        organization_name=org_name,
        city="Platform"
    )
    
    db.add(new_superadmin)
    db.commit()
    print(f"Super-admin '{username}' created successfully!")
    db.close()

if __name__ == "__main__":
    create_superadmin()
