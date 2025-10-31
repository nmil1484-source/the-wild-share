# Stripe Boost Purchase - Complete Implementation Guide

## Executive Summary

**Status:** Backend fully implemented ✅ | Frontend not connected ❌

The backend Stripe integration for boost purchases is **100% complete and ready to use**. The only issue is that the frontend doesn't call the API - it just shows an alert saying "Stripe integration coming soon."

**Backend API Endpoint:** `/api/boost/purchase` (fully functional)  
**Boost Pricing:** $2.99 (7 days), $9.99 (30 days), $19.99 (homepage featured)

---

## Current Implementation Status

### ✅ Backend (Complete)
- Stripe checkout session creation
- Customer creation/retrieval
- Payment processing
- Webhook handling
- Boost activation on equipment
- Expiration tracking
- All routes registered and working

### ❌ Frontend (Not Implemented)
- Boost button just redirects to equipment page
- No API call to `/api/boost/purchase`
- No equipment selection modal
- No Stripe redirect
- No success callback handling

---

## Implementation Steps

### Step 1: Add Boost State to App.jsx

Add these state variables after line 103 (after reviewForm):

```javascript
// Boost purchase states
const [showBoostModal, setShowBoostModal] = useState(false)
const [selectedBoostType, setSelectedBoostType] = useState(null)
const [boostPricing, setBoostPricing] = useState({
  boost_7_days: { name: 'Boost 7 Days', price: 2.99, duration_days: 7 },
  boost_30_days: { name: 'Boost 30 Days', price: 9.99, duration_days: 30 },
  homepage_featured: { name: 'Homepage Featured', price: 19.99, duration_days: 7 }
})
```

### Step 2: Add Boost Purchase Handler

Add this function after the other handlers (around line 800-900):

```javascript
const handleBoostPurchase = async (equipmentId, boostType) => {
  if (!equipmentId) {
    alert('Please select an equipment to boost')
    return
  }
  
  setLoading(true)
  
  try {
    const response = await fetch(`${API_URL}/api/boost/purchase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        equipment_id: equipmentId,
        boost_type: boostType
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Redirect to Stripe checkout
      window.location.href = data.checkout_url
    } else {
      alert(data.error || 'Failed to create checkout session')
      setLoading(false)
    }
  } catch (error) {
    console.error('Boost purchase error:', error)
    alert('Error creating checkout session: ' + error.message)
    setLoading(false)
  }
}
```

### Step 3: Add Boost Success Handler

Add this function to handle the success callback:

```javascript
const handleBoostSuccess = async (sessionId) => {
  setLoading(true)
  
  try {
    const response = await fetch(`${API_URL}/api/boost/success`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        session_id: sessionId
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert(`Boost activated successfully! Your equipment will be featured until ${new Date(data.expires_at).toLocaleDateString()}`)
      setCurrentView('equipment')
      fetchMyEquipment() // Refresh equipment list
    } else {
      alert(data.error || 'Failed to activate boost')
    }
  } catch (error) {
    console.error('Boost success error:', error)
    alert('Error activating boost: ' + error.message)
  } finally {
    setLoading(false)
  }
}
```

### Step 4: Handle URL Parameters for Success Callback

Add this useEffect to check for success callback:

```javascript
useEffect(() => {
  // Check if returning from Stripe checkout
  const urlParams = new URLSearchParams(window.location.search)
  const sessionId = urlParams.get('session_id')
  const view = window.location.pathname.split('/').pop()
  
  if (view === 'success' && sessionId) {
    handleBoostSuccess(sessionId)
    // Clean up URL
    window.history.replaceState({}, document.title, '/equipment')
  }
}, [])
```

### Step 5: Create Boost Selection Modal Component

Create `/rental-site/src/components/BoostSelectionModal.jsx`:

```javascript
import React from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Zap } from 'lucide-react'

const BoostSelectionModal = ({ open, onClose, boostType, boostPricing, myEquipment, onSelect }) => {
  if (!boostType || !boostPricing[boostType]) return null
  
  const boost = boostPricing[boostType]
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            {boost.name} - ${boost.price}
          </DialogTitle>
          <DialogDescription>
            Select which equipment you want to boost for {boost.duration_days} days
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {myEquipment && myEquipment.length > 0 ? (
            myEquipment.map((equipment) => (
              <Card key={equipment.id} className="cursor-pointer hover:bg-gray-50 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{equipment.name}</h3>
                      <p className="text-sm text-gray-600">{equipment.description}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        ${equipment.daily_price}/day | {equipment.location}
                      </p>
                      {equipment.is_boosted && (
                        <p className="text-xs text-blue-600 mt-1">
                          Already boosted until {new Date(equipment.boost_expires_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <Button
                      onClick={() => onSelect(equipment.id)}
                      className="ml-4"
                    >
                      Boost This
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>You don't have any equipment listed yet.</p>
              <Button
                onClick={() => {
                  onClose()
                  // Navigate to equipment page
                }}
                className="mt-4"
              >
                Create Your First Listing
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default BoostSelectionModal
```

### Step 6: Update PricingPage.jsx

Replace lines 218-225 in `/rental-site/src/components/PricingPage.jsx`:

**OLD CODE:**
```javascript
onClick={() => {
  if (!user) {
    alert('Please sign in to boost listings')
    return
  }
  onViewChange('equipment')
}}
```

**NEW CODE:**
```javascript
onClick={() => {
  if (!user) {
    alert('Please sign in to boost listings')
    return
  }
  onBoostClick(option.id)
}}
```

### Step 7: Update PricingPage Props

Update the PricingPage component signature (line 7):

**OLD:**
```javascript
const PricingPage = ({ user, onViewChange }) => {
```

**NEW:**
```javascript
const PricingPage = ({ user, onViewChange, onBoostClick }) => {
```

### Step 8: Update App.jsx PricingPage Usage

Find where PricingPage is rendered (around line 2666) and update:

**OLD:**
```javascript
<PricingPage 
  user={user} 
  onUpgrade={(tier) => {
    // TODO: Implement Stripe checkout
    alert(`Upgrading to ${tier}! Stripe integration coming soon.`)
  }}
  onViewChange={setCurrentView}
/>
```

**NEW:**
```javascript
<PricingPage 
  user={user} 
  onViewChange={setCurrentView}
  onBoostClick={(boostType) => {
    setSelectedBoostType(boostType)
    setShowBoostModal(true)
  }}
/>
```

### Step 9: Add Boost Modal to App.jsx Render

Add this modal before the closing `</div>` of the main app (around line 2900):

```javascript
{/* Boost Selection Modal */}
<BoostSelectionModal
  open={showBoostModal}
  onClose={() => setShowBoostModal(false)}
  boostType={selectedBoostType}
  boostPricing={boostPricing}
  myEquipment={myEquipment}
  onSelect={(equipmentId) => {
    setShowBoostModal(false)
    handleBoostPurchase(equipmentId, selectedBoostType)
  }}
/>
```

### Step 10: Import BoostSelectionModal

Add to imports at top of App.jsx:

```javascript
import BoostSelectionModal from './components/BoostSelectionModal'
```

---

## Testing Checklist

### Test in Stripe Test Mode

1. **Setup Stripe Test Keys**
   - Ensure `STRIPE_SECRET_KEY` is set to test key (sk_test_...)
   - Backend should be in test mode

2. **Test Boost Purchase Flow**
   - [ ] Log in as equipment owner
   - [ ] Click "View Boost Options"
   - [ ] Click "Boost a Listing" on $2.99 option
   - [ ] Modal opens showing your equipment
   - [ ] Click "Boost This" on an equipment
   - [ ] Redirects to Stripe checkout page
   - [ ] URL shows `checkout.stripe.com`

3. **Test Stripe Checkout**
   - [ ] Use test card: 4242 4242 4242 4242
   - [ ] Any future expiry date
   - [ ] Any 3-digit CVC
   - [ ] Complete payment
   - [ ] Redirects back to thewildshare.com

4. **Test Success Callback**
   - [ ] After payment, redirects to `/boost/success?session_id=xxx`
   - [ ] Success handler activates boost
   - [ ] Alert shows success message with expiry date
   - [ ] Equipment page shows boosted status
   - [ ] Equipment has blue "Boosted" badge

5. **Test Boost Display**
   - [ ] Boosted equipment appears at top of search results
   - [ ] Homepage featured appears in carousel
   - [ ] Boost expiry date shown in equipment details

6. **Test Edge Cases**
   - [ ] Try to boost without equipment (should show message)
   - [ ] Try to boost while logged out (should show sign-in prompt)
   - [ ] Cancel payment on Stripe (should return to equipment page)
   - [ ] Try to boost already-boosted equipment (should allow, extends boost)

---

## Stripe Test Cards

Use these for testing:

| Card Number | Description |
|-------------|-------------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 9995 | Declined payment |
| 4000 0025 0000 3155 | Requires authentication (3D Secure) |

**Expiry:** Any future date  
**CVC:** Any 3 digits  
**ZIP:** Any 5 digits

---

## Environment Variables

Ensure these are set in Railway:

```bash
STRIPE_SECRET_KEY=sk_test_...  # Your Stripe test secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook signing secret (optional for testing)
FRONTEND_URL=https://thewildshare.com  # For redirect URLs
```

---

## Deployment Steps

1. **Commit Changes**
   ```bash
   git add -A
   git commit -m "Implement Stripe boost purchase integration"
   git push
   ```

2. **Wait for Railway Deployment**
   - Monitor build logs
   - Verify deployment successful

3. **Test on Live Site**
   - Go to thewildshare.com
   - Test full boost purchase flow
   - Verify Stripe redirect works
   - Confirm boost activation

---

## Troubleshooting

### Issue: "Failed to create checkout session"
**Solution:** Check that STRIPE_SECRET_KEY is set in Railway environment variables

### Issue: Redirect doesn't work after payment
**Solution:** Verify FRONTEND_URL is set correctly in backend environment

### Issue: Boost doesn't activate after payment
**Solution:** Check webhook is configured or success callback is working

### Issue: "You can only boost your own equipment"
**Solution:** Ensure you're logged in and the equipment belongs to your account

---

## Files Modified Summary

1. `/rental-site/src/App.jsx` - Add boost state, handlers, modal
2. `/rental-site/src/components/PricingPage.jsx` - Update button onClick
3. `/rental-site/src/components/BoostSelectionModal.jsx` - New file (create this)

---

## Estimated Implementation Time

- **Step 1-4:** 15 minutes (state and handlers)
- **Step 5:** 20 minutes (modal component)
- **Step 6-9:** 10 minutes (integrate modal)
- **Step 10:** 5 minutes (testing)

**Total:** ~50 minutes for experienced developer

---

## Additional Features to Consider

### Future Enhancements
1. **Boost Analytics** - Show views/clicks during boost period
2. **Boost History** - List of past boosts and performance
3. **Auto-renewal** - Option to automatically renew boosts
4. **Bulk Boosting** - Boost multiple items at once
5. **Boost Scheduling** - Schedule boosts for future dates

---

## Support

If you encounter issues:
1. Check browser console for errors
2. Check Railway backend logs
3. Verify Stripe dashboard for checkout sessions
4. Test with Stripe test cards first

---

**Status:** Ready to implement  
**Complexity:** Medium  
**Backend:** ✅ Complete  
**Frontend:** ⏳ Needs implementation  
**Estimated Time:** 1 hour

