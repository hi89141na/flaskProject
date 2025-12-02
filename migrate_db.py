"""
Migration script to update existing database from image_url to image_filename
Run this ONLY if you have an existing database with data
"""

from app import app
from models import db, Product

def migrate_database():
    """Migrate from image_url to image_filename column"""
    with app.app_context():
        print("Starting database migration...")
        
        # Check if the table exists and has data
        try:
            products = Product.query.all()
            print(f"Found {len(products)} products to migrate")
            
            # Since we're changing from image_url to image_filename,
            # existing products will have image_url set but not image_filename
            # We'll set image_filename to None for all (they'll use placeholder)
            for product in products:
                if hasattr(product, 'image_url'):
                    # Old column exists, we need to recreate the table
                    print("Old schema detected. Please run init_db.py to recreate the database.")
                    print("This will clear all data and create a fresh database with the new schema.")
                    return
                else:
                    print("Database is already using the new schema (image_filename)")
                    return
        
        except Exception as e:
            print(f"Error during migration: {e}")
            print("Please run init_db.py to create a fresh database with dummy data.")

if __name__ == "__main__":
    migrate_database()
