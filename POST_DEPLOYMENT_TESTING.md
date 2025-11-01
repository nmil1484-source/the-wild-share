# Post-Deployment Testing Checklist

## After Vercel Deployment Completes

### Phase 1: Update Backend CORS (5 minutes)

1. **Get Vercel URL** from deployment (e.g., `https://the-wild-share-abc123.vercel.app`)

2. **Run CORS update script:**
   ```bash
   cd /home/ubuntu/wild-share-deploy
   python3 update_cors_for_vercel.py https://your-vercel-url.vercel.app
   ```

3. **Commit and push changes:**
   ```bash
   git add backend/src/main.py
   git commit -m "Update CORS to allow Vercel domain"
   git push origin main
   ```

4. **Wait for Railway auto-deployment** (2-3 minutes)
   - Check Railway dashboard for deployment status
   - Wait for "Deployed" status

---

### Phase 2: Test Critical Features (15 minutes)

#### Test 1: Admin Dashboard ✅
**URL:** `https://your-vercel-url.vercel.app`

1. Log in with admin account
2. Click "Admin" button in navigation
3. Verify admin dashboard loads
4. Check all tabs: Users, Equipment, Bookings, Boosts
5. **Expected:** Dashboard displays data, no errors

#### Test 2: Boost Purchase Flow ✅
**URL:** `https://your-vercel-url.vercel.app/pricing`

1. Click "Boost a Listing" button
2. Verify boost selection modal opens
3. Check all three pricing tiers display:
   - 3 Days - $2.99
   - 7 Days - $4.99
   - 14 Days - $9.99
4. Select equipment from dropdown
5. Choose a pricing tier
6. Click "Continue to Payment"
7. Verify Stripe checkout modal opens
8. **Expected:** Stripe payment form loads (don't complete payment in test mode)

#### Test 3: Security Deposit Field ✅
**URL:** `https://your-vercel-url.vercel.app`

1. Log in as equipment owner
2. Go to "My Equipment"
3. Click "Add Equipment" or edit existing
4. Verify "Security Deposit" field exists
5. Enter a custom amount (e.g., $100)
6. Save equipment
7. View equipment listing
8. **Expected:** Security deposit displays correctly

#### Test 4: Image Upload in Edit Modal ✅
**URL:** Equipment edit modal

1. Edit an existing equipment listing
2. Verify image upload shows file input (not broken URL field)
3. Upload a new image
4. Save changes
5. **Expected:** Image uploads and displays correctly

#### Test 5: General Functionality ✅

1. Browse equipment listings
2. View equipment details
3. Create a booking
4. Check user profile
5. **Expected:** All features work, no console errors

---

### Phase 3: Performance & UX Check (5 minutes)

1. **Check page load speed:**
   - Should be fast (< 2 seconds)
   - Vercel CDN should make it faster than Railway

2. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors (should be none)
   - Check Network tab for failed API calls

3. **Test on mobile:**
   - Open site on phone or use DevTools mobile view
   - Verify responsive design works

---

### Phase 4: Optional - Update Domain (10 minutes)

If you want `thewildshare.com` to point to Vercel:

1. **In Vercel Dashboard:**
   - Go to Project Settings → Domains
   - Add `thewildshare.com`
   - Vercel will provide DNS instructions

2. **Update DNS:**
   - Go to your domain registrar
   - Update A record or CNAME as instructed
   - Wait 5-30 minutes for DNS propagation

3. **Verify:**
   - Visit `https://thewildshare.com`
   - Should load from Vercel (not Railway)

---

## Success Criteria

✅ Admin dashboard loads and displays data  
✅ Boost purchase modal opens and shows Stripe checkout  
✅ Security deposit field works in equipment forms  
✅ Image upload works in edit modal  
✅ No console errors  
✅ API calls work (check Network tab)  
✅ Page loads fast  
✅ Mobile responsive  

---

## Troubleshooting

### Admin Dashboard Doesn't Load
- Check browser console for errors
- Verify user is logged in as admin
- Check Network tab - API calls should go to Railway backend

### Boost Purchase Fails
- Verify VITE_STRIPE_PUBLISHABLE_KEY is set in Vercel
- Check browser console for Stripe errors
- Verify API calls reach Railway backend

### API Calls Fail (CORS errors)
- Verify backend CORS was updated correctly
- Check Railway deployment completed
- Verify Vercel URL matches CORS configuration

### Images Don't Load
- Check if images are stored on Railway
- Verify image URLs are absolute (not relative)
- Check browser console for 404 errors

---

## Next Steps After Testing

Once everything works:

1. **Document any issues** found during testing
2. **Implement remaining features:**
   - Message Owner button
   - Contract download
   - Final UX polish
3. **Prepare for launch:**
   - Test with real users
   - Monitor for errors
   - Set up analytics

---

**Ready to test!** 🚀

