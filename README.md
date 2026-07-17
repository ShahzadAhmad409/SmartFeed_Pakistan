# SmartFeed Pakistan

SmartFeed Pakistan is a food donation and food-rescue platform designed to connect food donors (restaurants, households, events) with people in need and verified NGOs across Pakistan using real-time geolocation.

## Features
- **3 User Roles:** Donor, Receiver, and Admin (NGO/Welfare org).
- **Live Location:** Uses Haversine distance and `navigator.geolocation` to find nearby donations.
- **Interactive Map:** Built with Leaflet.js to visualize nearby donations.
- **Stats Dashboard:** Live metrics for Admins and Donors.
- **Polished UI:** TailwindCSS + Alpine.js for smooth animations and transitions.

## Prerequisites
- Python 3.9+
- SQLite (included via SQLAlchemy)

## Setup and Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: if you encounter a passlib/bcrypt error, make sure `bcrypt<4.0.0` is installed: `pip install "bcrypt<4.0.0"`)*

2. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Open the app:**
   Navigate to `http://localhost:8000` in your web browser.

## Helpers

- **Seed Data:** Run `python seed_data.py` to populate the database with sample users (admin, donors, receivers) and active/expired donations across different cities.
- **Create Super Admin:** Run `python create_superadmin.py` to manually create a super-admin account via CLI.

## How NGO Verification Works
1. A user visits the `/ngo-request` page and submits their organization details.
2. The request goes into a "pending" state.
3. The Super Admin logs in, views the pending requests on their dashboard, and clicks "Approve".
4. The system automatically creates an `admin` account for that NGO and alerts the Super Admin with the credentials to share with the NGO.
