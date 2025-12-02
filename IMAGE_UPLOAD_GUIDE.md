# Image Upload Feature Documentation

## Overview
The SecretsClan application now supports image upload, display, and automatic deletion for product images.

## Features Implemented

### 1. **Image Upload**
- Upload images when adding or editing products through the admin panel
- Supported formats: **JPG, JPEG, PNG**
- Maximum file size: **16MB**
- Files are saved in `static/uploads/` folder
- Automatic filename sanitization using `secure_filename`
- Timestamp added to filenames to prevent conflicts

### 2. **Image Display**
- Product images displayed on:
  - Homepage (featured products)
  - Category pages
  - Product detail pages
  - Search results
  - Shopping cart
  - Admin product list
- Placeholder image (`placeholder.svg`) shown when no image is uploaded

### 3. **Image Deletion**
- Automatic image file deletion when:
  - A product is deleted
  - A product's image is updated (old image removed)
- Placeholder images are never deleted

### 4. **Image Preview**
- Live preview when uploading a new image in admin panel
- Shows current image when editing a product

## Database Schema Changes

### Product Model
```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)  # NEW: stores filename
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    def get_image_url(self):
        """Returns the URL path for the product image or placeholder"""
        if self.image_filename:
            return f'/static/uploads/{self.image_filename}'
        return '/static/uploads/placeholder.svg'
```

## File Structure

```
SecretsClan/
├── static/
│   └── uploads/                    # Image upload directory
│       ├── placeholder.svg         # Default placeholder image
│       └── [product_images]        # Uploaded product images
├── models.py                       # Updated Product model
├── app.py                          # Updated routes with upload logic
├── forms.py                        # Updated ProductForm with FileField
└── templates/
    ├── admin/
    │   ├── product_form.html       # Image upload form with preview
    │   └── products.html           # Shows product images
    ├── index.html                  # Shows product images
    ├── category.html               # Shows product images
    ├── product.html                # Shows product image
    ├── search.html                 # Shows product images
    └── cart.html                   # Shows product images in cart
```

## Configuration

### App Configuration (app.py)
```python
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

### Helper Functions
- `allowed_file(filename)` - Validates file extensions
- `delete_image_file(filename)` - Safely deletes image files
- `product.get_image_url()` - Returns image URL or placeholder

## Usage Guide

### For Admin Users

#### Adding a Product with Image:
1. Go to Admin Panel → Products → Add New Product
2. Fill in product details (name, description, price, category)
3. Click "Choose File" under "Product Image"
4. Select a JPG, JPEG, or PNG image
5. See live preview of the selected image
6. Click "Add Product" to save
7. Image is automatically saved with a unique filename

#### Editing a Product Image:
1. Go to Admin Panel → Products → Edit (on any product)
2. Current image is displayed (if exists)
3. Choose a new file to replace the old image
4. Old image file is automatically deleted
5. Click "Edit Product" to save changes

#### Deleting a Product:
1. Go to Admin Panel → Products → Delete (on any product)
2. Confirm deletion
3. Product and its image file are both deleted

### Image Display Logic
- **If image exists**: Shows uploaded image from `/static/uploads/[filename]`
- **If no image**: Shows placeholder SVG `/static/uploads/placeholder.svg`

## Migration from Old Database

If you have an existing database with the old `image_url` column:

1. **Backup your data** (if needed)
2. Run the initialization script to recreate the database:
   ```powershell
   python init_db.py
   ```
3. This will create a fresh database with:
   - Updated schema (image_filename instead of image_url)
   - Dummy data with placeholders
   - You can then upload real images through the admin panel

## Technical Details

### File Upload Process:
1. Form submitted with `enctype="multipart/form-data"`
2. File validated for allowed extension
3. Filename sanitized using `secure_filename()`
4. Timestamp added to prevent filename conflicts
5. File saved to `static/uploads/` directory
6. Filename stored in database

### Filename Format:
```
original_name_1699012345.jpg
[filename]_[timestamp].[ext]
```

### Security Features:
- ✅ Extension whitelist (jpg, jpeg, png only)
- ✅ Filename sanitization (prevents directory traversal)
- ✅ File size limit (16MB max)
- ✅ Safe file deletion (checks for placeholder)
- ✅ CSRF protection on forms

## Troubleshooting

### Images not uploading?
- Check folder permissions on `static/uploads/`
- Ensure file is JPG, JPEG, or PNG
- Check file size is under 16MB
- Verify form has `enctype="multipart/form-data"`

### Images not displaying?
- Check if file exists in `static/uploads/`
- Verify `get_image_url()` returns correct path
- Check browser console for 404 errors

### Old images not deleted?
- Ensure product has `image_filename` set
- Check file permissions in `static/uploads/`
- Review logs for deletion errors

## API Reference

### Model Method
```python
product.get_image_url()
# Returns: '/static/uploads/filename.jpg' or '/static/uploads/placeholder.svg'
```

### Template Usage
```html
<img src="{{ product.get_image_url() }}" alt="{{ product.name }}">
```

### Form Field
```python
image = FileField('Product Image', validators=[
    Optional(),
    FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG, JPEG, and PNG images are allowed!')
])
```

## Future Enhancements (Optional)

- Image resizing/optimization on upload
- Multiple images per product
- Image cropping interface
- Cloud storage integration (AWS S3, Cloudinary)
- Bulk image upload
- Image compression

---

**Note**: After updating to this version, you need to reinitialize the database since the schema has changed from `image_url` to `image_filename`.
