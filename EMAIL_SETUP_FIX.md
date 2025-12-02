# Email Configuration Quick Fix

## Problem
You're getting this error:
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

This means the Gmail credentials in `app.py` are not configured correctly.

## Solution

### Step 1: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Under "How you sign in to Google", enable **2-Step Verification** (if not already enabled)
4. After enabling 2-Step Verification, scroll down and click on **App passwords**
5. Select:
   - **App**: Mail
   - **Device**: Other (Custom name)
   - Enter: "SecretsClan Flask App"
6. Click **Generate**
7. Google will show you a **16-character password** (like: `abcd efgh ijkl mnop`)
8. **Copy this password** (you won't be able to see it again)

### Step 2: Update app.py

Open `app.py` and find line 22:

```python
app.config['MAIL_PASSWORD'] = 'your-app-password-here'  # Use Gmail App Password
```

Replace `'your-app-password-here'` with the 16-character app password (remove spaces):

```python
app.config['MAIL_PASSWORD'] = 'abcdefghijklmnop'  # Your actual app password
```

Also verify line 21 has your correct Gmail address:

```python
app.config['MAIL_USERNAME'] = 'secretsclanstore@gmail.com'  # Your Gmail address
```

And line 24 has the correct admin email:

```python
app.config['ADMIN_EMAIL'] = 'hinanadeem@gmail.com'  # Admin email for order notifications
```

### Step 3: Save and Restart

1. Save `app.py`
2. Stop the Flask server (Ctrl+C in terminal)
3. Start it again: `python app.py`
4. Try placing an order again

## Testing

After configuration, try placing a test order:

1. Add a product to cart
2. Go to checkout
3. Fill in the form
4. Click "Place Order"
5. Check both email inboxes (customer email and admin email)

## Troubleshooting

### Still getting authentication errors?

- **Check the email address**: Make sure `MAIL_USERNAME` is the SAME Gmail account you used to generate the app password
- **Check the app password**: Make sure you copied it correctly (no spaces)
- **2-Step Verification**: Must be enabled on the Gmail account
- **Less secure app access**: NOT needed (app passwords bypass this)

### Emails not arriving?

- Check **spam/junk** folders
- Wait 1-2 minutes (sometimes there's a delay)
- Check the terminal output for error messages

### "BadCredentials" error?

This is the error you're currently getting. It means:
- Wrong app password
- Wrong email address
- 2-Step Verification not enabled

## Alternative: Use Environment Variables (Recommended for Security)

Instead of hardcoding the password in `app.py`, use environment variables:

1. Install python-dotenv:
```bash
pip install python-dotenv
```

2. Create a `.env` file in your project root:
```
MAIL_PASSWORD=your-16-char-app-password
MAIL_USERNAME=secretsclanstore@gmail.com
ADMIN_EMAIL=hinanadeem@gmail.com
```

3. Update `app.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL')
```

4. Add `.env` to `.gitignore` to keep credentials secure

## Quick Test Command

You can test email sending without placing an order:

```python
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'secretsclanstore@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password-here'

mail = Mail(app)

with app.app_context():
    msg = Message('Test Email', recipients=['hinanadeem@gmail.com'])
    msg.body = 'This is a test email from SecretsClan!'
    mail.send(msg)
    print('Email sent successfully!')
```

Save this as `test_email.py` and run: `python test_email.py`

---

After following these steps, your email notifications should work perfectly! 📧✅
