"""
Quick setup script to reinitialize database with image upload support
"""

import os
import sys

def setup_database():
    """Setup database with new image upload schema"""
    
    print("="*60)
    print("SecretsClan - Database Setup for Image Upload Feature")
    print("="*60)
    
    # Check if database exists
    db_path = os.path.join('instance', 'database.db')
    
    if os.path.exists(db_path):
        print(f"\n⚠️  Warning: Database already exists at {db_path}")
        response = input("Do you want to delete and recreate it? (yes/no): ").lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ Setup cancelled. Database not modified.")
            return
        
        try:
            os.remove(db_path)
            print(f"✓ Old database deleted")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            return
    
    # Ensure uploads folder exists
    uploads_dir = os.path.join('static', 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"✓ Created uploads directory: {uploads_dir}")
    
    # Run init_db script
    print("\n📦 Initializing database with dummy data...")
    try:
        from init_db import init_database
        init_database()
        print("\n✅ Setup complete!")
        print("\n🎉 You can now run the application with: python app.py")
        print("📸 Upload product images through the admin panel!")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    setup_database()
