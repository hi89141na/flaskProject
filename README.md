# SecretsClan - Online Fashion Accessories Store

SecretsClan is a modern Flask-based e-commerce web application for selling stylish fashion accessories including perfumes, keychains, wrist watches, ties, hoodies, and shirts.

## 🌟 Features

- **Modern Homepage** with category browsing and featured products
- **Search Functionality** to find products by name or category
- **User Authentication** with login, signup, and logout
- **Shopping Cart** with add, update, and remove items
- **Product Categories** for organized shopping
- **Admin Panel** with full CRUD operations for:
  - Products management
  - Categories management
  - Users management
- **Responsive Design** using Bootstrap 5
- **Dummy Data** pre-populated for testing

## 🗂️ Project Structure

```
SecretsClan/
│
├── app.py                  # Main Flask application
├── models.py               # Database models (User, Category, Product, Cart)
├── forms.py                # WTForms for validation
├── init_db.py             # Database initialization script
├── requirements.txt        # Python dependencies
├── database.db            # SQLite database (created after init)
│
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── images/            # Product images (placeholders)
│   └── js/                # JavaScript files
│
└── templates/
    ├── base.html          # Base template with navbar
    ├── index.html         # Homepage
    ├── category.html      # Category page
    ├── product.html       # Product details
    ├── cart.html          # Shopping cart
    ├── search.html        # Search results
    ├── login.html         # Login page
    ├── signup.html        # Registration page
    └── admin/
        ├── dashboard.html      # Admin dashboard
        ├── products.html       # Product management
        ├── product_form.html   # Add/Edit product
        ├── categories.html     # Category management
        ├── category_form.html  # Add/Edit category
        └── users.html          # User management
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the project directory:**
   ```powershell
   cd "d:\7th Sem\Software Construction and Dev\flaskProject\SecretsClan"
   ```

2. **Install required packages:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Initialize the database with dummy data:**
   ```powershell
   python init_db.py
   ```

4. **Run the application:**
   ```powershell
   python app.py
   ```

5. **Open your browser and visit:**
   ```
   http://127.0.0.1:5000
   ```

## 👥 Login Credentials

### Admin Account
- **Email:** admin@secretsclan.com
- **Password:** admin123

### Regular User Account
- **Email:** user@example.com
- **Password:** user123

## 🛣️ Routes

| Route | Description |
|-------|-------------|
| `/` | Homepage with categories and featured products |
| `/search` | Search results page |
| `/category/<name>` | Products in specific category |
| `/product/<id>` | Product details page |
| `/cart` | Shopping cart |
| `/cart/add/<id>` | Add item to cart |
| `/cart/update/<id>` | Update cart item quantity |
| `/cart/remove/<id>` | Remove item from cart |
| `/login` | User login |
| `/signup` | User registration |
| `/logout` | User logout |
| `/admin` | Admin dashboard (admin only) |
| `/admin/products` | Manage products (admin only) |
| `/admin/products/add` | Add new product (admin only) |
| `/admin/products/edit/<id>` | Edit product (admin only) |
| `/admin/products/delete/<id>` | Delete product (admin only) |
| `/admin/categories` | Manage categories (admin only) |
| `/admin/categories/add` | Add new category (admin only) |
| `/admin/categories/edit/<id>` | Edit category (admin only) |
| `/admin/categories/delete/<id>` | Delete category (admin only) |
| `/admin/users` | Manage users (admin only) |
| `/admin/users/delete/<id>` | Delete user (admin only) |

## 📦 Categories & Products

The application includes 6 categories with 3 products each:

1. **Perfumes** - Velvet Noir, Ocean Breeze, Mystic Rose
2. **Keychains** - Leather Classic, Metal Eagle, Crystal Heart
3. **Wrist Watches** - Classic Chrono, Minimalist Black, Sports Elite
4. **Ties** - Silk Striped, Paisley Pattern, Solid Black
5. **Hoodies** - Urban Comfort, Tech Fleece Pro, Classic Pullover
6. **Shirts** - Denim Casual, Oxford White, Flannel Check

## 🛠️ Technology Stack

- **Backend:** Flask 3.0.0
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF & WTForms
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Template Engine:** Jinja2

## 🔒 Security Features

- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Session-based authentication
- Admin-only route protection
- Form validation

## 📝 Notes

- This is a demonstration project with dummy data
- Images use placeholder URLs (via.placeholder.com)
- No actual payment processing is implemented
- The search bar is available on all pages via the navbar

## 🤝 Admin Features

The admin panel provides:
- Dashboard with statistics (total users, products, categories)
- Full CRUD operations for products
- Full CRUD operations for categories
- User management (view and delete)
- Protected routes (admin access only)

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🎨 Customization

You can customize the application by:
- Modifying `static/css/style.css` for styling
- Updating the color scheme in the CSS variables
- Adding your own product images
- Extending the database models
- Adding new features and routes

---

**Developed for Software Construction and Development Course**
