# How to Update Your Website with New Payment Features

## Quick Update Steps

### Option 1: Upload New Files to GitHub (Easiest)

1. **Download the new code:**
   - Download `the-wild-share-v2-stripe-connect.tar.gz` (attached)
   - Extract it on your computer

2. **Go to your GitHub repository:**
   - Visit https://github.com/YOUR_USERNAME/the-wild-share

3. **Replace the files:**
   - Click on each file in GitHub
   - Click the pencil icon (Edit)
   - Copy the new content from your extracted files
   - Click "Commit changes"
   
   **Files to update:**
   - `src/models/user.py`
   - `src/routes/payments.py`
   - `src/main.py`
   - Add new file: `src/routes/stripe_connect.py`

4. **Render will automatically redeploy** (takes 3-5 minutes)

### Option 2: Delete and Re-upload (Faster)

1. **In your GitHub repo:**
   - Click "Add file" → "Upload files"
   - Drag all files from the extracted `backend` folder
   - Check "Replace existing files"
   - Click "Commit changes"

2. **Render automatically redeploys**

---

## What's New

✅ **12% automatic commission** on all rentals  
✅ **88% automatic payout** to equipment owners  
✅ **Stripe Connect integration** for bank transfers  
✅ **Automatic deposit refunds** when equipment returned  
✅ **Damage protection** - deduct from deposits  
✅ **Earnings dashboard** for owners  

---

## After Updating

1. **Set up Stripe Connect** (see STRIPE_CONNECT_SETUP.md)
2. **Test the payment flow** in test mode
3. **Owners can connect bank accounts**
4. **Start accepting real bookings!**

---

## Need Help?

Check the detailed guide: **STRIPE_CONNECT_SETUP.md**

