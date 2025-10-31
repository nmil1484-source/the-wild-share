# PayPal Boost Purchase - Simple Implementation Guide

## Why PayPal is Better for Boosts

**Advantages:**
- ✅ Simpler integration (no backend session creation needed)
- ✅ Faster implementation (15-20 minutes vs 1 hour)
- ✅ Widely trusted by users
- ✅ No PCI compliance concerns
- ✅ Automatic payment confirmation
- ✅ Works in sandbox mode for testing

**Disadvantages:**
- ❌ Slightly higher fees than Stripe (2.9% + $0.30 vs 2.9% + $0.30... actually same!)
- ❌ Less customizable checkout experience

## Implementation Approach

We'll use **PayPal Smart Buttons** - the easiest and most modern approach.

### How It Works

1. User clicks "Boost a Listing" → Opens equipment selection modal
2. User selects equipment → PayPal button appears
3. User clicks PayPal button → PayPal popup opens
4. User completes payment → PayPal calls our success handler
5. Success handler → Calls backend API to activate boost
6. Backend → Updates equipment with boost status

---

## Step-by-Step Implementation

### Step 1: Add PayPal SDK to index.html

Add this to `/rental-site/index.html` before closing `</body>` tag:

```html
<!-- PayPal SDK -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_PAYPAL_CLIENT_ID&currency=USD"></script>
```

**For testing, use sandbox client ID:**
```html
<script src="https://www.paypal.com/sdk/js?client-id=sb&currency=USD"></script>
```

### Step 2: Create PayPal Boost Component

Create `/rental-site/src/components/PayPalBoostButton.jsx`:

```javascript
import React, { useEffect, useRef } from 'react'

const PayPalBoostButton = ({ amount, boostType, equipmentId, onSuccess, onError }) => {
  const paypalRef = useRef()

  useEffect(() => {
    if (window.paypal && paypalRef.current) {
      window.paypal.Buttons({
        createOrder: (data, actions) => {
          return actions.order.create({
            purchase_units: [{
              amount: {
                value: amount.toFixed(2),
                currency_code: 'USD'
              },
              description: `Boost: ${boostType}`,
              custom_id: `${equipmentId}_${boostType}_${Date.now()}`
            }]
          })
        },
        onApprove: async (data, actions) => {
          const order = await actions.order.capture()
          console.log('Payment successful:', order)
          
          // Call success handler
          if (onSuccess) {
            onSuccess(order, equipmentId, boostType)
          }
        },
        onError: (err) => {
          console.error('PayPal error:', err)
          if (onError) {
            onError(err)
          }
        },
        onCancel: () => {
          console.log('Payment cancelled')
          alert('Payment cancelled')
        },
        style: {
          layout: 'vertical',
          color: 'blue',
          shape: 'rect',
          label: 'paypal'
        }
      }).render(paypalRef.current)
    }
  }, [amount, boostType, equipmentId, onSuccess, onError])

  return <div ref={paypalRef} className="w-full"></div>
}

export default PayPalBoostButton
```

### Step 3: Create Boost Selection Modal with PayPal

Create `/rental-site/src/components/BoostPayPalModal.jsx`:

```javascript
import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Zap, CheckCircle } from 'lucide-react'
import PayPalBoostButton from './PayPalBoostButton'

const BoostPayPalModal = ({ open, onClose, boostType, boostPricing, myEquipment, onSuccess }) => {
  const [selectedEquipmentId, setSelectedEquipmentId] = useState(null)
  const [showPayPal, setShowPayPal] = useState(false)

  if (!boostType || !boostPricing[boostType]) return null

  const boost = boostPricing[boostType]
  const selectedEquipment = myEquipment?.find(e => e.id === selectedEquipmentId)

  const handlePaymentSuccess = async (order, equipmentId, boostType) => {
    console.log('Payment completed:', order.id)
    
    // Call backend to activate boost
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://web-production-cb94.up.railway.app'}/api/boost/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          equipment_id: equipmentId,
          boost_type: boostType,
          payment_id: order.id,
          payer_email: order.payer.email_address,
          amount: order.purchase_units[0].amount.value
        })
      })

      const data = await response.json()

      if (response.ok) {
        alert(`🎉 Boost activated! Your equipment will be featured until ${new Date(data.expires_at).toLocaleDateString()}`)
        if (onSuccess) {
          onSuccess()
        }
        onClose()
      } else {
        alert('Payment received but boost activation failed. Please contact support.')
      }
    } catch (error) {
      console.error('Boost activation error:', error)
      alert('Payment received but boost activation failed. Please contact support.')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            {boost.name} - ${boost.price}
          </DialogTitle>
          <DialogDescription>
            {!showPayPal ? (
              `Select which equipment you want to boost for ${boost.duration_days} days`
            ) : (
              `Complete payment to boost "${selectedEquipment?.name}"`
            )}
          </DialogDescription>
        </DialogHeader>

        {!showPayPal ? (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {myEquipment && myEquipment.length > 0 ? (
              myEquipment.map((equipment) => (
                <Card 
                  key={equipment.id} 
                  className={`cursor-pointer transition-all ${
                    selectedEquipmentId === equipment.id 
                      ? 'ring-2 ring-blue-500 bg-blue-50' 
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedEquipmentId(equipment.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold">{equipment.name}</h3>
                        <p className="text-sm text-gray-600">{equipment.description}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          ${equipment.daily_price}/day | {equipment.location}
                        </p>
                        {equipment.is_boosted && (
                          <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                            <CheckCircle className="h-3 w-3" />
                            Already boosted until {new Date(equipment.boost_expires_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      {selectedEquipmentId === equipment.id && (
                        <CheckCircle className="h-6 w-6 text-blue-600 ml-4" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>You don't have any equipment listed yet.</p>
                <Button
                  onClick={() => onClose()}
                  className="mt-4"
                >
                  Create Your First Listing
                </Button>
              </div>
            )}

            {myEquipment && myEquipment.length > 0 && (
              <div className="flex gap-3 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => onClose()}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button 
                  onClick={() => setShowPayPal(true)}
                  disabled={!selectedEquipmentId}
                  className="flex-1"
                >
                  Continue to Payment
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Summary */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Equipment:</span>
                    <span>{selectedEquipment?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Boost Type:</span>
                    <span>{boost.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Duration:</span>
                    <span>{boost.duration_days} days</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total:</span>
                    <span>${boost.price}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* PayPal Button */}
            <PayPalBoostButton
              amount={boost.price}
              boostType={boostType}
              equipmentId={selectedEquipmentId}
              onSuccess={handlePaymentSuccess}
              onError={(err) => {
                console.error('Payment error:', err)
                alert('Payment failed. Please try again.')
              }}
            />

            <Button 
              variant="outline" 
              onClick={() => setShowPayPal(false)}
              className="w-full"
            >
              ← Back to Equipment Selection
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

export default BoostPayPalModal
```

### Step 4: Add Backend Boost Activation Endpoint

Create `/backend/src/routes/boost_paypal.py`:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.equipment import Equipment
from datetime import datetime, timedelta

boost_paypal_bp = Blueprint('boost_paypal', __name__)

# Boost pricing
BOOST_PRICING = {
    'boost_7_days': {
        'name': 'Boost 7 Days',
        'price': 2.99,
        'duration_days': 7
    },
    'boost_30_days': {
        'name': 'Boost 30 Days',
        'price': 9.99,
        'duration_days': 30
    },
    'homepage_featured': {
        'name': 'Homepage Featured',
        'price': 19.99,
        'duration_days': 7
    }
}

@boost_paypal_bp.route('/activate', methods=['POST'])
@jwt_required()
def activate_boost():
    """Activate boost after PayPal payment"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    boost_type = data.get('boost_type')
    payment_id = data.get('payment_id')
    payer_email = data.get('payer_email')
    amount = float(data.get('amount', 0))
    
    if not all([equipment_id, boost_type, payment_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if boost_type not in BOOST_PRICING:
        return jsonify({'error': 'Invalid boost type'}), 400
    
    # Verify equipment exists and belongs to user
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    if equipment.owner_id != user_id:
        return jsonify({'error': 'You can only boost your own equipment'}), 403
    
    boost_info = BOOST_PRICING[boost_type]
    
    # Verify amount matches
    if abs(amount - boost_info['price']) > 0.01:
        return jsonify({'error': 'Payment amount mismatch'}), 400
    
    # Apply the boost
    duration_days = boost_info['duration_days']
    
    if boost_type == 'homepage_featured':
        equipment.is_homepage_featured = True
        equipment.homepage_featured_expires_at = datetime.utcnow() + timedelta(days=duration_days)
        expires_at = equipment.homepage_featured_expires_at
    else:
        equipment.is_boosted = True
        equipment.boost_expires_at = datetime.utcnow() + timedelta(days=duration_days)
        expires_at = equipment.boost_expires_at
    
    equipment.total_boosts_purchased = (equipment.total_boosts_purchased or 0) + 1
    
    # TODO: Store payment record in database for accounting
    # payment_record = Payment(
    #     user_id=user_id,
    #     equipment_id=equipment_id,
    #     amount=amount,
    #     payment_provider='paypal',
    #     payment_id=payment_id,
    #     payer_email=payer_email
    # )
    # db.session.add(payment_record)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Boost activated successfully',
        'equipment': equipment.to_dict(),
        'expires_at': expires_at.isoformat()
    }), 200
```

### Step 5: Register PayPal Boost Route

Add to `/backend/src/main.py`:

```python
from src.routes.boost_paypal import boost_paypal_bp
app.register_blueprint(boost_paypal_bp, url_prefix='/api/boost')
```

### Step 6: Update App.jsx

Add boost state and import:

```javascript
// Add to imports
import BoostPayPalModal from './components/BoostPayPalModal'

// Add to state (after line 103)
const [showBoostModal, setShowBoostModal] = useState(false)
const [selectedBoostType, setSelectedBoostType] = useState(null)
const [boostPricing] = useState({
  boost_7_days: { name: 'Boost 7 Days', price: 2.99, duration_days: 7 },
  boost_30_days: { name: 'Boost 30 Days', price: 9.99, duration_days: 30 },
  homepage_featured: { name: 'Homepage Featured', price: 19.99, duration_days: 7 }
})

// Add modal before closing </div> (around line 2900)
<BoostPayPalModal
  open={showBoostModal}
  onClose={() => setShowBoostModal(false)}
  boostType={selectedBoostType}
  boostPricing={boostPricing}
  myEquipment={myEquipment}
  onSuccess={() => {
    fetchMyEquipment() // Refresh equipment list
    setCurrentView('equipment')
  }}
/>
```

### Step 7: Update PricingPage.jsx

Update button onClick (line 218-225):

```javascript
onClick={() => {
  if (!user) {
    alert('Please sign in to boost listings')
    return
  }
  onBoostClick(option.id)
}}
```

Update component props (line 7):

```javascript
const PricingPage = ({ user, onViewChange, onBoostClick }) => {
```

### Step 8: Update PricingPage Usage in App.jsx

Find PricingPage render (line 2666):

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

---

## Testing with PayPal Sandbox

### 1. Create PayPal Sandbox Account
- Go to https://developer.paypal.com
- Sign in or create account
- Go to Dashboard → Apps & Credentials
- Create app to get Client ID

### 2. Test Accounts
PayPal provides test accounts:
- **Buyer account:** Use to make test payments
- **Seller account:** Receives test payments

### 3. Test Flow
1. Click "Boost a Listing"
2. Select equipment
3. Click "Continue to Payment"
4. PayPal popup opens
5. Log in with test buyer account
6. Complete payment
7. Success callback activates boost

---

## Environment Variables

Add to Railway:

```bash
PAYPAL_CLIENT_ID=your_live_client_id
PAYPAL_SECRET=your_live_secret
PAYPAL_MODE=sandbox  # or 'live' for production
```

---

## Deployment

1. Commit changes
2. Push to GitHub
3. Railway auto-deploys
4. Test on live site

---

## Advantages of This Approach

✅ **Simple** - No complex backend session creation  
✅ **Fast** - 15-20 minute implementation  
✅ **Secure** - PayPal handles all payment data  
✅ **Reliable** - PayPal's proven infrastructure  
✅ **Testable** - Sandbox mode for development  

---

## Total Implementation Time

- Step 1-3: 10 minutes (components)
- Step 4-5: 5 minutes (backend)
- Step 6-8: 5 minutes (integration)
- **Total: 20 minutes**

Much faster than Stripe! 🚀

