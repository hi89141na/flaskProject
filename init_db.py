"""
Database initialization script for SecretsClan
Run this script to populate the database with dummy data
"""

from app import app
from models import db, User, Category, Product
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with dummy data"""
    with app.app_context():
        # Drop all tables and recreate them
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            name="Admin User",
            email="admin@secretsclan.com",
            is_admin=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Create regular user
        print("Creating regular user...")
        user = User(
            name="John Doe",
            email="user@example.com",
            is_admin=False
        )
        user.set_password("user123")
        db.session.add(user)
        
        # Create categories
        print("Creating categories...")
        categories = [
            Category(name="Perfumes"),
            Category(name="Keychains"),
            Category(name="Wrist Watches"),
            Category(name="Ties"),
            Category(name="Hoodies"),
            Category(name="Shirts")
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create products
        print("Creating products...")
        
        products_data = [
            # Perfumes
            {
                "name": "Velvet Noir",
                "description": "A luxurious and sophisticated fragrance with notes of vanilla, amber, and sandalwood. Perfect for evening wear and special occasions.",
                "price": 2500.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Velvet+Noir+Perfume",
                "category": "Perfumes"
            },
            {
                "name": "Ocean Breeze",
                "description": "Fresh and invigorating scent reminiscent of a coastal morning. Features aquatic notes with hints of citrus and sea salt.",
                "price": 2200.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Ocean+Breeze+Perfume",
                "category": "Perfumes"
            },
            {
                "name": "Mystic Rose",
                "description": "Elegant floral perfume with rose petals, jasmine, and a touch of musk. A timeless classic for any occasion.",
                "price": 2800.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Mystic+Rose+Perfume",
                "category": "Perfumes"
            },
            
            # Keychains
            {
                "name": "Leather Classic Keychain",
                "description": "Premium genuine leather keychain with brass hardware. Durable and stylish accessory for your keys.",
                "price": 450.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Leather+Keychain",
                "category": "Keychains"
            },
            {
                "name": "Metal Eagle Keychain",
                "description": "Detailed metal eagle design keychain with antique finish. A symbol of strength and freedom.",
                "price": 550.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Eagle+Keychain",
                "category": "Keychains"
            },
            {
                "name": "Crystal Heart Keychain",
                "description": "Elegant crystal heart keychain with silver chain. Makes a perfect gift for loved ones.",
                "price": 600.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Crystal+Heart+Keychain",
                "category": "Keychains"
            },
            
            # Wrist Watches
            {
                "name": "Classic Chrono",
                "description": "Sophisticated chronograph watch with stainless steel case and leather strap. Water resistant up to 50m.",
                "price": 4500.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Classic+Chrono+Watch",
                "category": "Wrist Watches"
            },
            {
                "name": "Minimalist Black",
                "description": "Sleek minimalist design with black dial and mesh strap. Perfect for modern professionals.",
                "price": 3800.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Minimalist+Black+Watch",
                "category": "Wrist Watches"
            },
            {
                "name": "Sports Elite",
                "description": "Durable sports watch with multiple functions including stopwatch, timer, and backlight. Ideal for active lifestyles.",
                "price": 3200.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Sports+Elite+Watch",
                "category": "Wrist Watches"
            },
            
            # Ties
            {
                "name": "Silk Striped Tie",
                "description": "Classic striped tie made from 100% pure silk. Perfect for business meetings and formal events.",
                "price": 1200.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Silk+Striped+Tie",
                "category": "Ties"
            },
            {
                "name": "Paisley Pattern Tie",
                "description": "Sophisticated paisley pattern tie in rich colors. Adds elegance to any formal outfit.",
                "price": 1350.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Paisley+Tie",
                "category": "Ties"
            },
            {
                "name": "Solid Black Tie",
                "description": "Timeless solid black tie in premium silk. An essential accessory for every gentleman's wardrobe.",
                "price": 1100.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Black+Tie",
                "category": "Ties"
            },
            
            # Hoodies
            {
                "name": "Urban Comfort",
                "description": "Cozy cotton-blend hoodie with kangaroo pocket and adjustable drawstrings. Available in multiple colors.",
                "price": 3200.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Urban+Comfort+Hoodie",
                "category": "Hoodies"
            },
            {
                "name": "Tech Fleece Pro",
                "description": "Advanced tech fleece material for maximum warmth with minimal weight. Modern fit with zippered pockets.",
                "price": 4200.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Tech+Fleece+Hoodie",
                "category": "Hoodies"
            },
            {
                "name": "Classic Pullover",
                "description": "Timeless pullover hoodie in heavyweight cotton. Ribbed cuffs and hem for perfect fit.",
                "price": 2900.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Classic+Pullover+Hoodie",
                "category": "Hoodies"
            },
            
            # Shirts
            {
                "name": "Denim Casual",
                "description": "Relaxed fit denim shirt perfect for casual outings. Features two chest pockets and button-down collar.",
                "price": 2800.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Denim+Casual+Shirt",
                "category": "Shirts"
            },
            {
                "name": "Oxford White",
                "description": "Crisp white oxford shirt in premium cotton. Essential for business and formal occasions.",
                "price": 2400.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Oxford+White+Shirt",
                "category": "Shirts"
            },
            {
                "name": "Flannel Check",
                "description": "Warm flannel shirt with classic check pattern. Soft brushed fabric for all-day comfort.",
                "price": 2600.00,
                "image_url": "https://via.placeholder.com/400x400.png?text=Flannel+Check+Shirt",
                "category": "Shirts"
            }
        ]
        
        for product_data in products_data:
            category = Category.query.filter_by(name=product_data["category"]).first()
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                image_filename=None,  # Changed from image_url - will use placeholder
                category_id=category.id
            )
            db.session.add(product)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nLogin Credentials:")
        print("-" * 50)
        print("Admin Login:")
        print("  Email: admin@secretsclan.com")
        print("  Password: admin123")
        print("\nRegular User Login:")
        print("  Email: user@example.com")
        print("  Password: user123")
        print("="*50)
        print(f"\nTotal Categories: {len(categories)}")
        print(f"Total Products: {len(products_data)}")
        print(f"Total Users: 2")
        print("\nNote: Products created with placeholder images.")
        print("You can upload real images through the admin panel.")
        print("\nYou can now run the application with: python app.py")
        print("="*50)

if __name__ == "__main__":
    init_database()
