# Vercel Deployment Instructions for The Wild Share

## Quick Setup Guide

You're on the Vercel "New Project" page. Follow these steps:

### Step 1: Select Git Scope
- Click the **"Select Git Scope"** dropdown
- Choose your GitHub account (nmil1484-source)
- This authorizes Vercel to access your repository

### Step 2: Import Repository
- Find and select the **"the-wild-share"** repository
- Click **"Import"**

### Step 3: Configure Project Settings

**Framework Preset:** Vite (should auto-detect)

**Root Directory:** 
- Click "Edit" next to Root Directory
- Enter: `rental-site`
- This is critical - the frontend code is in the rental-site folder

**Build Settings:**
- Build Command: `npm run build` (default is fine)
- Output Directory: `dist` (default is fine)
- Install Command: `npm install` (default is fine)

### Step 4: Add Environment Variables

Click **"Environment Variables"** section and add these two variables:

**Variable 1:**
- Name: `VITE_API_URL`
- Value: `https://web-production-cb94.up.railway.app`
- Environment: Production, Preview, Development (all checked)

**Variable 2:**
- Name: `VITE_STRIPE_PUBLISHABLE_KEY`
- Value: `pk_test_51SJPdQGW9js9GVkoZfMrWFNQkyGJGyW9Ls6Aisq4tGlYN2UNLG9HvS36YwjO51kHNTKvIgx5ImLK6I8PpjEV2zg700WKXnDRQ5`
- Environment: Production, Preview, Development (all checked)

### Step 5: Deploy

- Click **"Deploy"** button
- Wait 2-3 minutes for the build to complete
- Vercel will show build logs in real-time

### Step 6: Get Your URL

Once deployed, Vercel will provide a URL like:
- `https://the-wild-share-xxx.vercel.app`

Copy this URL - we'll need it to update the backend CORS settings.

---

## What Happens After Deployment

Once the deployment succeeds:

1. **I'll update the backend** to allow API calls from your Vercel domain
2. **We'll test the admin dashboard** - it should finally work!
3. **We'll test the boost purchase feature** - all three pricing tiers
4. **We can optionally point thewildshare.com to Vercel** (instead of Railway)

---

## Troubleshooting

**If build fails:**
- Check that root directory is set to `rental-site`
- Verify both environment variables are added correctly

**If you get stuck:**
- Take a screenshot and share it
- I can guide you through any step

---

## Why This Solves Everything

✅ **No more caching issues** - Vercel handles cache invalidation properly  
✅ **Instant deployments** - Every Git push automatically deploys  
✅ **Admin dashboard will work** - New code will actually be served  
✅ **Boost purchase will work** - All features will be live  
✅ **Global CDN** - Fast loading worldwide  
✅ **Automatic HTTPS** - Secure by default  

Let's get this deployed! 🚀

