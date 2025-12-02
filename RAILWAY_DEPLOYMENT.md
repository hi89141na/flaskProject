# 🚀 Railway Deployment Guide for SecretsClan Flask Store

This guide will walk you through deploying your Flask e-commerce application to Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Git**: Install Git on your computer

## 🔧 Pre-Deployment Setup (Already Completed)

The following files have been configured for Railway:

✅ `railway.json` - Railway configuration
✅ `Procfile` - Web process command
✅ `requirements.txt` - Python dependencies (includes psycopg2-binary for PostgreSQL)
✅ `runtime.txt` - Python version specification
✅ `.gitignore` - Excludes sensitive files
✅ `app.py` - Database URL compatibility fix for Railway

## 📦 Step 1: Push Your Code to GitHub

If you haven't already, push your code to GitHub:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Railway deployment"

# Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

**⚠️ IMPORTANT**: Make sure your `.env` file is NOT pushed to GitHub (it's already in `.gitignore`).

## 🚂 Step 2: Deploy on Railway

### 2.1 Create New Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your Flask project repository

### 2.2 Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will automatically create a PostgreSQL database and set the `DATABASE_URL` environment variable

### 2.3 Configure Environment Variables

Click on your web service, go to the **"Variables"** tab, and add the following environment variables:

#### Required Variables:

```
SECRET_KEY=your-super-secret-random-key-change-this-to-something-secure
MAIL_USERNAME=secretsclanstore@gmail.com
MAIL_PASSWORD=your-gmail-app-password-here
ADMIN_EMAIL=hi89141na@gmail.com
BASE_URL=https://your-app-name.railway.app
```

#### How to Get Gmail App Password:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Copy the 16-character password and use it as `MAIL_PASSWORD`

#### Optional Variables (already have defaults in code):

```
DATABASE_URL=postgresql://... (automatically set by Railway PostgreSQL)
PORT=8080 (automatically set by Railway)
```

### 2.4 Update BASE_URL After Deployment

1. After your first deployment, Railway will provide you with a URL like `https://your-app-name.railway.app`
2. Update the `BASE_URL` environment variable with this URL
3. Railway will automatically redeploy with the new variable

## 🔄 Step 3: Initialize Database

After the first deployment, you need to initialize the database:

### Option A: Using Railway CLI (Recommended)

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to your project:
   ```bash
   railway link
   ```

4. Run database initialization:
   ```bash
   railway run python setup_db.py
   ```

### Option B: Using Railway Dashboard

1. Go to your project in Railway dashboard
2. Click on your web service
3. Go to **"Settings"** → **"Custom Start Command"**
4. Temporarily change it to: `python setup_db.py && gunicorn app:app`
5. Wait for deployment to complete (this will create tables)
6. Change it back to: `gunicorn app:app`
7. Redeploy

### Option C: Create Admin via Python Shell

1. Use Railway CLI: `railway run python`
2. Then run:
   ```python
   from app import app, db
   from models import User
   
   with app.app_context():
       db.create_all()
       admin = User(name='Admin', email='admin@example.com', is_admin=True)
       admin.set_password('admin123')
       db.session.add(admin)
       db.session.commit()
       print("Admin user created!")
   ```

## 🎯 Step 4: Verify Deployment

1. Visit your Railway app URL: `https://your-app-name.railway.app`
2. Test the following:
   - ✅ Homepage loads correctly
   - ✅ User signup and login work
   - ✅ Admin login works (use credentials from setup_db.py)
   - ✅ Add products, categories
   - ✅ Place a test order
   - ✅ Check email notifications

## 🐛 Troubleshooting

### App Won't Start

**Check Logs:**
1. Go to Railway dashboard
2. Click on your service
3. View **"Deployments"** → **"View Logs"**

**Common Issues:**

1. **Database not connected**: Make sure PostgreSQL service is added and `DATABASE_URL` is set
2. **Missing environment variables**: Check all required variables are set
3. **Import errors**: Ensure `requirements.txt` includes all dependencies

### Email Not Sending

1. Verify `MAIL_USERNAME` and `MAIL_PASSWORD` are set correctly
2. Make sure you're using a Gmail App Password (not your regular password)
3. Test email with the admin route: `/admin/test-email`

### Static Files Not Loading

Railway serves static files through Flask. Make sure:
- `static/` folder exists
- CSS and JS files are in correct paths
- No hardcoded local paths

### Database Tables Missing

Run the initialization command:
```bash
railway run python setup_db.py
```

## 🔒 Security Checklist

Before going live, ensure:

- ✅ `SECRET_KEY` is set to a strong random value
- ✅ `.env` file is in `.gitignore` and NOT in GitHub
- ✅ Gmail App Password is used (not regular password)
- ✅ `debug=False` in production (already set in app.py)
- ✅ Admin password is strong and changed from default

## 🔄 Updating Your App

To deploy updates:

```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin main
```

Railway will automatically detect the push and redeploy your application!

## 📊 Monitoring

- **View Logs**: Railway Dashboard → Your Service → Deployments → View Logs
- **Check Metrics**: Railway Dashboard → Your Service → Metrics
- **Database Usage**: Railway Dashboard → PostgreSQL Service → Metrics

## 💰 Pricing

Railway offers:
- **Free Trial**: $5 credit to start
- **Hobby Plan**: $5/month usage-based
- **Pro Plan**: $20/month with more resources

Your Flask app should fit comfortably in the Hobby plan.

## 🆘 Need Help?

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Flask Docs: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---

## 🎉 Success!

Once deployed, your SecretsClan store will be:
- 🌍 Accessible worldwide
- 🔒 Using secure PostgreSQL database
- 📧 Sending email confirmations
- 🚀 Auto-deploying on git push
- 📊 Monitored and scalable

**Your live URL**: `https://your-app-name.railway.app`

Happy selling! 🛍️
