# Boost Purchase Implementation Plan

## Current Status
- ✅ Backend API fully implemented (`/api/boost/purchase`)
- ✅ Stripe checkout session creation working
- ✅ Boost pricing defined ($2.99, $9.99, $19.99)
- ✅ Success/webhook handlers implemented
- ❌ Frontend not calling the API (just shows alert)

## Implementation Steps

### 1. Update App.jsx
Add boost state and handlers:
```javascript
const [showBoostModal, setShowBoostModal] = useState(false)
const [selectedBoostType, setSelectedBoostType] = useState(null)
const [boostingEquipment, setBoostingEquipment] = useState(null)
```

### 2. Create handleBoostPurchase function
```javascript
const handleBoostPurchase = async (equipmentId, boostType) => {
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
    }
  } catch (error) {
    alert('Error: ' + error.message)
  }
}
```

### 3. Update PricingPage.jsx
Replace the button onClick handler:
```javascript
onClick={() => {
  if (!user) {
    alert('Please sign in to boost listings')
    return
  }
  // Open modal to select equipment
  setSelectedBoostType(option.id)
  setShowBoostModal(true)
}}
```

### 4. Create BoostSelectionModal component
Modal to select which equipment to boost:
- Show list of user's equipment
- Display selected boost type and price
- Confirm button to proceed to Stripe checkout

### 5. Handle success callback
Add route handler for `/boost/success?session_id=xxx`:
- Call `/api/boost/success` with session_id
- Show success message
- Redirect to equipment page

### 6. Update Equipment model fields (if needed)
Check if Equipment model has:
- `is_boosted` (Boolean)
- `boost_expires_at` (DateTime)
- `is_homepage_featured` (Boolean)
- `homepage_featured_expires_at` (DateTime)
- `total_boosts_purchased` (Integer)

## Files to Modify
1. `/rental-site/src/App.jsx` - Add boost handlers and modal
2. `/rental-site/src/components/PricingPage.jsx` - Update button onClick
3. Create `/rental-site/src/components/BoostSelectionModal.jsx` - New component

## Testing Checklist
- [ ] Click boost button opens equipment selection modal
- [ ] Select equipment and confirm redirects to Stripe
- [ ] Complete payment on Stripe test mode
- [ ] Success callback activates boost on equipment
- [ ] Equipment shows as boosted in listings
- [ ] Boost expires after duration

