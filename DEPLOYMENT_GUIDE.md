# The Wild Share - Deployment Guide for Render.com

## Quick Deployment Steps

### Prerequisites
1. **GitHub Account** - Sign up at https://github.com if you don't have one
2. **Render Account** - Sign up at https://render.com (free tier available)

### Step 1: Push Code to GitHub

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it: `the-wild-share`
   - Make it Public
   - Don't initialize with README (we already have code)
   - Click "Create repository"

2. **Push your code to GitHub:**
   ```bash
   cd ~/outdoor-rental-website/backend
   git init
   git add .
   git commit -m "Initial commit - The Wild Share marketplace"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/the-wild-share.git
   git push -u origin main
   ```
   
   Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 2: Deploy on Render

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Sign in with your GitHub account (recommended)

2. **Create New Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Click "Connect" next to your `the-wild-share` repository
   - If you don't see it, click "Configure account" to grant Render access

3. **Configure the Service:**
   - **Name:** `the-wild-share` (or any name you prefer)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** Leave blank
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT src.main:app`
   - **Instance Type:** Free

4. **Add Environment Variables:**
   Click "Advanced" and add these:
   - `FLASK_APP` = `src/main.py`
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = (click "Generate" for random value)
   - `JWT_SECRET_KEY` = (click "Generate" for random value)
   - `STRIPE_SECRET_KEY` = `sk_test_...` (your Stripe key, optional for now)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 3-5 minutes for the build to complete
   - Your app will be live at: `https://the-wild-share.onrender.com` (or similar)

### Step 3: Test Your Deployment

1. Visit your Render URL (e.g., `https://the-wild-share.onrender.com`)
2. You should see "The Wild Share" homepage
3. Click "Sign In" to test the authentication dialog
4. Try creating an account

## Alternative: One-Click Deploy

If you prefer, you can use Render's one-click deploy:

1. Make sure your code is on GitHub
2. Add this button to your README:
   ```markdown
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
   ```
3. Click the button and follow the prompts

## Important Notes

### Free Tier Limitations
- **Spin down after 15 minutes of inactivity** - First request after inactivity may take 30-60 seconds
- **750 hours/month** - More than enough for testing and small-scale use
- **No credit card required**

### Database
- Currently using SQLite (file-based database)
- For production, consider upgrading to PostgreSQL
- Render offers free PostgreSQL databases

### Custom Domain
- Free tier includes `.onrender.com` subdomain
- Can add custom domain on paid plans

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is in the root directory
- Verify Python version compatibility
- Check build logs in Render dashboard

### App Won't Start
- Verify the start command is correct
- Check that all environment variables are set
- Review application logs in Render dashboard

### Database Errors
- SQLite database will reset on each deploy (free tier)
- For persistent data, use Render's PostgreSQL add-on

## Upgrading to PostgreSQL (Optional)

1. In Render Dashboard, create a new PostgreSQL database
2. Copy the Internal Database URL
3. Add to your web service environment variables:
   - `DATABASE_URL` = (paste the PostgreSQL URL)
4. Update `src/main.py` to use PostgreSQL instead of SQLite

## Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Flask Deployment Guide:** https://render.com/docs/deploy-flask

---

## Your Application URLs

After deployment, you'll have:
- **Website:** `https://your-app-name.onrender.com`
- **API:** `https://your-app-name.onrender.com/api/`
- **Dashboard:** https://dashboard.render.com

Share the website URL with anyone - it's publicly accessible!

---

**Need help?** Check the Render logs in your dashboard for detailed error messages.

