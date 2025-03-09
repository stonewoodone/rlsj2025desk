import os
from werkzeug.security import generate_password_hash
from app_simple import app, db
from models_simple import User, Supplier, FuelContract, FuelMineDelivery, FuelTransportation, FuelArrival

def init_db():
    """Initialize the database with tables and admin user."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
        
        print("Database initialized successfully.")

if __name__ == '__main__':
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize the database
    init_db() 