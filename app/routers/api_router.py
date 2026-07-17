from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, database, auth
import math
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api", tags=["API"])

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

@router.post("/ngo-request")
def create_ngo_request(request: schemas.NGORequestCreate, db: Session = Depends(database.get_db)):
    new_request = models.NGORequest(**request.model_dump())
    db.add(new_request)
    db.commit()
    return {"message": "NGO Request submitted successfully"}

@router.get("/ngo-requests")
def get_ngo_requests(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["superadmin", "admin"]))):
    requests = db.query(models.NGORequest).filter(models.NGORequest.status == "pending").all()
    return requests

@router.post("/ngo-requests/{req_id}/approve")
def approve_ngo_request(req_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["superadmin"]))):
    req = db.query(models.NGORequest).filter(models.NGORequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "approved"
    
    # Create the admin user
    default_password = "password123" # Should ideally send email, keeping it simple for mock
    hashed_password = auth.get_password_hash(default_password)
    
    # generate a username
    base_username = req.organization_name.lower().replace(" ", "")
    username = base_username
    counter = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
        
    new_admin = models.User(
        username=username,
        password_hash=hashed_password,
        role="admin",
        organization_name=req.organization_name,
        city=req.city
    )
    db.add(new_admin)
    db.commit()
    return {"message": f"Approved. Admin created with username: {username} and password: {default_password}"}

@router.post("/donations")
def create_donation(donation: schemas.DonationCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["donor"]))):
    new_donation = models.Donation(
        **donation.model_dump(),
        donor_id=current_user.id
    )
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    return new_donation

@router.get("/donations/my")
def get_my_donations(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["donor"]))):
    donations = db.query(models.Donation).filter(models.Donation.donor_id == current_user.id).order_by(models.Donation.created_at.desc()).all()
    # Check expiry
    for d in donations:
        expiry_time = d.created_at + timedelta(hours=d.hours_before_expiry)
        if datetime.now(timezone.utc) > expiry_time.replace(tzinfo=timezone.utc):
            d.is_expired = True
        else:
            d.is_expired = False
    return donations

@router.delete("/donations/{donation_id}")
def delete_donation(donation_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["donor"]))):
    donation = db.query(models.Donation).filter(models.Donation.id == donation_id, models.Donation.donor_id == current_user.id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found or not authorized")
    if donation.status == "claimed":
        raise HTTPException(status_code=400, detail="Cannot delete a claimed donation")
    
    db.delete(donation)
    db.commit()
    return {"message": "Donation deleted"}

@router.get("/donations/nearby")
def get_nearby_donations(lat: float, lng: float, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["receiver"]))):
    # Fetch all available donations
    available_donations = db.query(models.Donation).filter(models.Donation.status == "available").all()
    
    valid_donations = []
    now = datetime.now(timezone.utc)
    for d in available_donations:
        expiry_time = d.created_at.replace(tzinfo=timezone.utc) + timedelta(hours=d.hours_before_expiry)
        if now < expiry_time:
            dist = haversine(lat, lng, d.lat, d.lng)
            hours_left = (expiry_time - now).total_seconds() / 3600
            valid_donations.append({
                "donation": schemas.DonationOut.model_validate(d).model_dump(),
                "distance": dist,
                "donor_name": d.donor.organization_name or d.donor.username,
                "hours_left": hours_left
            })
            
    # Sort by distance and urgency
    valid_donations.sort(key=lambda x: (x["distance"], x["hours_left"]))
    
    return valid_donations

@router.post("/donations/{donation_id}/claim")
def claim_donation(donation_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["receiver", "admin", "superadmin"]))):
    donation = db.query(models.Donation).filter(models.Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.status != "available":
        raise HTTPException(status_code=400, detail="Donation is no longer available")
        
    expiry_time = donation.created_at.replace(tzinfo=timezone.utc) + timedelta(hours=donation.hours_before_expiry)
    if datetime.now(timezone.utc) > expiry_time:
         raise HTTPException(status_code=400, detail="Donation has expired")
         
    donation.status = "claimed"
    donation.receiver_id = current_user.id
    db.commit()
    return {"message": "Donation claimed successfully"}

@router.get("/admin/stats")
def get_admin_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["admin", "superadmin"]))):
    total_users = db.query(models.User).count()
    total_donations = db.query(models.Donation).count()
    total_claims = db.query(models.Donation).filter(models.Donation.status == "claimed").count()
    
    total_meals_rescued = db.query(func.sum(models.Donation.quantity)).filter(models.Donation.status == "claimed").scalar() or 0
    
    # 1 meal = 0.5 kg food waste prevented
    # 1 kg food = 2.5 kg CO2 saved
    food_waste_prevented_kg = total_meals_rescued * 0.5
    co2_saved_kg = food_waste_prevented_kg * 2.5
    
    return {
        "total_users": total_users,
        "total_donations": total_donations,
        "total_claims": total_claims,
        "meals_rescued": total_meals_rescued,
        "food_waste_prevented_kg": food_waste_prevented_kg,
        "co2_saved_kg": co2_saved_kg
    }

@router.get("/admin/expiring-donations")
def get_expiring_donations(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["admin", "superadmin"]))):
    available_donations = db.query(models.Donation).filter(models.Donation.status == "available").all()
    expiring = []
    now = datetime.now(timezone.utc)
    for d in available_donations:
        expiry_time = d.created_at.replace(tzinfo=timezone.utc) + timedelta(hours=d.hours_before_expiry)
        hours_left = (expiry_time - now).total_seconds() / 3600
        if 0 < hours_left <= 3: # expiring within 3 hours
            expiring.append({
                "donation": schemas.DonationOut.model_validate(d).model_dump(),
                "hours_left": hours_left,
                "donor_name": d.donor.organization_name or d.donor.username,
                "city": d.donor.city
            })
    expiring.sort(key=lambda x: x["hours_left"])
    return expiring

