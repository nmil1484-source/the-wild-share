# Vercel Deployment Guide for The Wild Share

## Step-by-Step Instructions

### 1. Authorize GitHub Access

On the "New Project" page:
- Click the **"Select Git Scope"** dropdown
- Select your GitHub account (nmil1484-source)
- Authorize Vercel to access your repositories

### 2. Configure Project Settings

Once authorized, you'll see project configuration:

**Framework Preset:** Vite  
**Root Directory:** `rental-site`  
**Build Command:** `npm run build`  
**Output Directory:** `dist`  

### 3. Add Environment Variables

Click "Environment Variables" and add:

```
VITE_API_URL=https://web-production-cb94.up.railway.app
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
```

**Important:** Replace `your_stripe_publishable_key_here` with your actual Stripe publishable key from https://dashboard.stripe.com/apikeys

### 4. Deploy

- Click **"Deploy"**
- Wait 2-3 minutes for build to complete
- Vercel will provide a URL like `https://the-wild-share-xxx.vercel.app`

### 5. Test the Deployment

Once deployed, test:
- ✅ Admin dashboard (click Admin button)
- ✅ Boost purchase (click Pricing → Boost a Listing)
- ✅ All other features

### 6. Update Backend CORS

After successful deployment, update the backend to allow the Vercel URL:

1. Go to Railway backend settings
2. Add environment variable:
   ```
   FRONTEND_URL=https://your-vercel-url.vercel.app
   ```
3. Update backend CORS configuration to allow the Vercel domain

### 7. Custom Domain (Optional)

To use thewildshare.com with Vercel:

1. In Vercel project settings → Domains
2. Add `thewildshare.com`
3. Update DNS records as instructed by Vercel
4. Wait for DNS propagation (5-30 minutes)

## Troubleshooting

### Build Fails
- Check that `rental-site` is set as root directory
- Verify environment variables are set correctly

### API Calls Fail
- Check VITE_API_URL is correct
- Verify backend CORS allows Vercel domain

### Admin/Boost Still Don't Work
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors
- Verify environment variables deployed correctly

## Expected Result

After Vercel deployment:
- ✅ Admin dashboard will work
- ✅ Boost purchase will work
- ✅ No more caching issues
- ✅ Instant deployments on every Git push
- ✅ Automatic HTTPS
- ✅ Global CDN

## Next Steps After Deployment

1. Test all features thoroughly
2. Update thewildshare.com DNS to point to Vercel
3. Implement remaining features:
   - Contract download
   - Message owner button
   - Final UX polish

---

**Need Help?** Let me know if you encounter any issues during deployment!

