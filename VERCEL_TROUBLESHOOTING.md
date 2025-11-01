# Vercel Deployment Troubleshooting

## Error Encountered

**Error:** `FUNCTION_INVOCATION_FAILED` - 500 Internal Server Error  
**Code:** `INTERNAL_SERVER_ERROR`

## Root Cause

The vercel.json file had environment variables defined in it, which is incorrect for Vercel. Environment variables should only be configured through the Vercel UI, not in vercel.json.

## Fix Applied

✅ **Removed env section from vercel.json**

**Before:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [...],
  "env": {
    "VITE_API_URL": "https://web-production-cb94.up.railway.app",
    "VITE_STRIPE_PUBLISHABLE_KEY": "@stripe_publishable_key"
  }
}
```

**After:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [...]
}
```

✅ **Committed and pushed to GitHub**

## Next Steps

### 1. Configure Environment Variables in Vercel UI

Go to: **Project Settings → Environment Variables**

Add these two variables:

**Variable 1:**
- Name: `VITE_API_URL`
- Value: `https://web-production-cb94.up.railway.app`
- Environment: Production, Preview, Development (all checked)

**Variable 2:**
- Name: `VITE_STRIPE_PUBLISHABLE_KEY`
- Value: `pk_test_51SJPdQGW9js9GVkoZfMrWFNQkyGJGyW9Ls6Aisq4tGlYN2UNLG9HvS36YwjO51kHNTKvIgx5ImLK6I8PpjEV2zg700WKXnDRQ5`
- Environment: Production, Preview, Development (all checked)

### 2. Verify Root Directory

Go to: **Project Settings → General → Root Directory**

Should be set to: `rental-site`

### 3. Redeploy

Option A: Automatic
- Vercel should automatically redeploy when it detects the new commit

Option B: Manual
- Go to **Deployments** tab
- Click on the failed deployment
- Click **"Redeploy"** button

### 4. Monitor Deployment

Watch the build logs to ensure:
- ✅ Build completes successfully
- ✅ No errors in the logs
- ✅ Deployment shows "Ready" status

## Expected Outcome

Once environment variables are configured and the site redeploys:
- ✅ Deployment should succeed
- ✅ Site should load without errors
- ✅ API calls should work (connecting to Railway backend)
- ✅ Admin dashboard and boost purchase features should be accessible

## Additional Notes

- The `@stripe_publishable_key` syntax in the old vercel.json was for Vercel secrets, which require separate setup
- Environment variables in vercel.json are not supported for static sites
- All build-time env vars (those starting with `VITE_`) must be configured in the Vercel UI

---

**Status:** Fix applied, waiting for user to configure environment variables and redeploy

