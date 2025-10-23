# Stripe Connect Setup Guide - Automatic Payments with 12% Commission

## Overview

Your platform now has **automatic payment processing** with:

✅ **12% platform commission** on all rentals  
✅ **88% automatic payout** to equipment owners  
✅ **Automatic deposit refunds** when equipment is returned  
✅ **Damage protection** - owners can deduct from deposits  
✅ **Direct bank transfers** - owners get paid to their bank account automatically

---

## How It Works

### For You (Platform Owner)

1. **You get 12% of every rental** automatically
2. **Money flows through your Stripe account** (you're the platform)
3. **Owners get 88% deposited** directly to their bank accounts
4. **You never have to manually pay anyone** - it's all automatic

### For Equipment Owners

1. **Connect their bank account** (one-time setup via Stripe)
2. **List equipment** on your platform
3. **Get booked** by renters
4. **Receive 88% of rental cost** automatically to their bank (within 2-7 days)
5. **Confirm equipment returned** to trigger deposit refund

### For Renters

1. **Book equipment** and pay with credit/debit card
2. **Pay rental cost + 50% deposit**
3. **Use the equipment**
4. **Return equipment** to owner
5. **Get deposit refunded** automatically (or partial refund if damaged)

---

## Setting Up Stripe Connect

### Step 1: Upgrade Your Stripe Account

1. **Go to your Stripe Dashboard:** https://dashboard.stripe.com
2. **Click "Connect" in the left sidebar**
3. **Click "Get started"**
4. **Choose "Platform or marketplace"**
5. **Follow the setup wizard**

This enables Stripe Connect on your account (it's free, no extra fees).

### Step 2: Get Your API Keys

1. **Go to:** https://dashboard.stripe.com/apikeys
2. **Copy your Secret Key** (starts with `sk_test_...` for testing)
3. **For production:** Use the live key (starts with `sk_live_...`)

### Step 3: Add to Render

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click your "the-wild-share" service**
3. **Click "Environment"**
4. **Find `STRIPE_SECRET_KEY`** (or add it if missing)
5. **Paste your Stripe secret key**
6. **Click "Save Changes"**

Your app will automatically redeploy with payment processing enabled!

---

## How Owners Connect Their Bank Accounts

### Owner Onboarding Flow

When an equipment owner signs up, they need to connect their bank account:

1. **Owner logs in** to The Wild Share
2. **Goes to "My Equipment" dashboard**
3. **Clicks "Connect Bank Account" button**
4. **Redirected to Stripe** (secure, official Stripe page)
5. **Enters bank account details:**
   - Bank account number
   - Routing number
   - Personal information (for verification)
   - Tax information (required by law)
6. **Stripe verifies** their identity (instant or 1-2 days)
7. **Owner is approved** and can start receiving payments

### What Owners See

Owners get access to:
- **Stripe Express Dashboard** - View earnings, payouts, transaction history
- **Automatic transfers** - Money appears in their bank account 2-7 days after rental
- **Payout schedule** - Can see when money is coming
- **Tax documents** - Stripe provides 1099 forms at year-end

---

## Payment Flow Example

### Scenario: Renter books a Starlink for 3 days at $75/day

**Renter pays:**
- Rental cost: $225 (3 days × $75)
- Deposit (50%): $112.50
- **Total charged: $337.50**

**Money distribution:**
- **Platform (you) receives:** $27 (12% of $225)
- **Owner receives:** $198 (88% of $225)
- **Deposit held:** $112.50 (refunded when returned)

**When equipment is returned:**
- **If in good condition:** Renter gets $112.50 refunded
- **If damaged:** Owner deducts damage cost (e.g., $50), renter gets $62.50 refunded

**Timeline:**
- Renter pays immediately (credit card charged)
- Platform fee ($27) stays in your Stripe account
- Owner payout ($198) transfers to owner's bank in 2-7 days
- Deposit refund processes when owner confirms return

---

## API Endpoints (For Developers)

### Stripe Connect Endpoints

**Create Connect Account:**
```
POST /api/stripe/create-connect-account
Headers: Authorization: Bearer <JWT_TOKEN>
```

**Create Onboarding Link:**
```
POST /api/stripe/create-onboarding-link
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "refresh_url": "https://your-site.com/dashboard",
  "return_url": "https://your-site.com/dashboard"
}
```

**Check Onboarding Status:**
```
GET /api/stripe/check-onboarding-status
Headers: Authorization: Bearer <JWT_TOKEN>
```

**Get Stripe Dashboard Link:**
```
POST /api/stripe/dashboard-link
Headers: Authorization: Bearer <JWT_TOKEN>
```

### Updated Payment Endpoints

**Create Payment (with commission):**
```
POST /api/create-payment-intent
Headers: Authorization: Bearer <JWT_TOKEN>
Body: { "booking_id": 123 }

Response includes:
- platform_fee: 12% commission
- owner_receives: 88% payout
- breakdown of all amounts
```

**Confirm Return (with deposit refund):**
```
POST /api/confirm-return
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "booking_id": 123,
  "condition": "good",  // or "damaged"
  "damage_cost": 0      // amount to deduct if damaged
}
```

**Get Earnings:**
```
GET /api/my-earnings
Headers: Authorization: Bearer <JWT_TOKEN>

Returns owner's total earnings, platform fees, net income
```

---

## Testing the Payment System

### Test Mode (Recommended First)

1. **Use test API keys** (start with `sk_test_...`)
2. **Use test credit cards:**
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits

3. **Test the flow:**
   - Create owner account
   - Connect bank account (use test mode)
   - List equipment
   - Create renter account
   - Book equipment
   - Complete payment
   - Confirm return
   - Check that deposit refunds

### Going Live

1. **Activate your Stripe account** (complete business verification)
2. **Switch to live API keys** (start with `sk_live_...`)
3. **Update Render environment variable** with live key
4. **Test with small real transaction**
5. **Launch!**

---

## Fees & Costs

### Stripe Fees (Standard)

- **2.9% + $0.30** per successful card charge
- **No monthly fees**
- **No setup fees**
- **No fees for Connect** (included free)

### Your Revenue Example

**$100 rental:**
- Renter pays: $100
- Stripe fee: $3.20 (2.9% + $0.30)
- Your commission (12%): $12
- Owner receives (88%): $88
- **Your net profit: $8.80** ($12 commission - $3.20 Stripe fee)

---

## Important Notes

### Tax Implications

- **You are responsible** for reporting your platform commission income
- **Owners are responsible** for reporting their rental income
- **Stripe provides 1099 forms** to owners earning over $600/year
- **Consult a tax professional** for your specific situation

### Legal Requirements

- **Terms of Service** - You should have clear terms about the 12% commission
- **Privacy Policy** - Required for collecting user data
- **Refund Policy** - Clearly state deposit refund rules
- **Liability** - Consider insurance or liability waivers

### Security

- **Never share your Secret API key** publicly
- **Use environment variables** (already set up in Render)
- **Enable Stripe Radar** (fraud protection - free)
- **Monitor your Stripe dashboard** for suspicious activity

---

## Troubleshooting

### "Owner hasn't completed payment setup"

**Solution:** Owner needs to complete Stripe onboarding
1. Owner logs in
2. Clicks "Connect Bank Account"
3. Completes Stripe verification
4. Wait for approval (usually instant)

### "Payment failed"

**Possible causes:**
- Invalid Stripe API key
- Test mode vs live mode mismatch
- Insufficient funds on renter's card
- Card declined by bank

**Check:**
- Stripe Dashboard logs
- Render application logs
- Error message details

### "Payout not received"

**Timeline:**
- Standard payout: 2-7 business days
- First payout: May take up to 10 days (Stripe verification)
- Check Stripe Express Dashboard for payout schedule

---

## Support Resources

- **Stripe Connect Docs:** https://stripe.com/docs/connect
- **Stripe Support:** https://support.stripe.com
- **Your Stripe Dashboard:** https://dashboard.stripe.com

---

## Next Steps

1. ✅ **Set up Stripe Connect** in your Stripe account
2. ✅ **Add API key** to Render environment variables
3. ✅ **Test with test mode** first
4. ✅ **Create test owner account** and connect bank
5. ✅ **Make test booking** and verify payment flow
6. ✅ **Go live** when ready!

---

**Questions?** Check your Stripe Dashboard or test the flow in test mode first!

