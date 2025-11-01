# Quick Reference - Vercel Deployment

## Environment Variables to Add in Vercel

When setting up the project in Vercel, add these two environment variables:

### Variable 1: API URL
```
Name: VITE_API_URL
Value: https://web-production-cb94.up.railway.app
```

### Variable 2: Stripe Publishable Key
```
Name: VITE_STRIPE_PUBLISHABLE_KEY
Value: pk_test_51SJPdQGW9js9GVkoZfMrWFNQkyGJGyW9Ls6Aisq4tGlYN2UNLG9HvS36YwjO51kHNTKvIgx5ImLK6I8PpjEV2zg700WKXnDRQ5
```

## Project Settings

- **Framework:** Vite (auto-detected)
- **Root Directory:** `rental-site` ⚠️ IMPORTANT
- **Build Command:** `npm run build` (default)
- **Output Directory:** `dist` (default)

## After Deployment

1. Copy the Vercel URL (e.g., `https://the-wild-share-xxxxx.vercel.app`)
2. Share it with me
3. I'll update backend CORS
4. We'll test everything!

---

**That's it!** Everything else is already configured in the code.

