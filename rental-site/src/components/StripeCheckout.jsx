import { useState, useEffect } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'
import CheckoutForm from './CheckoutForm'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Loader2 } from 'lucide-react'
import { paymentsAPI } from '../lib/api'

// Initialize Stripe with your publishable key
// This will be loaded from environment variable
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_placeholder')

export default function StripeCheckout({ booking, equipment, onSuccess, onCancel }) {
  const [clientSecret, setClientSecret] = useState('')
  const [paymentIntentId, setPaymentIntentId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Create payment intent when component mounts
    const createPaymentIntent = async () => {
      try {
        setLoading(true)
        setError(null)

        // Call your backend to create a payment intent
        const response = await paymentsAPI.createPaymentIntent(booking.id)
        
        setClientSecret(response.data.client_secret)
        setPaymentIntentId(response.data.payment_intent_id)
        setLoading(false)
      } catch (err) {
        console.error('Error creating payment intent:', err)
        setError(err.response?.data?.message || 'Failed to initialize payment. Please try again.')
        setLoading(false)
      }
    }

    if (booking?.id) {
      createPaymentIntent()
    }
  }, [booking?.id])

  const handleSuccess = async (paymentIntentId) => {
    try {
      // Confirm payment with backend
      await paymentsAPI.confirmPayment(paymentIntentId)
      onSuccess()
    } catch (err) {
      console.error('Error confirming payment:', err)
      setError('Payment succeeded but confirmation failed. Please contact support.')
    }
  }

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
          <p className="text-muted-foreground">Initializing secure payment...</p>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="py-8">
          <div className="text-center space-y-4">
            <p className="text-destructive font-medium">{error}</p>
            <button
              onClick={onCancel}
              className="text-sm text-muted-foreground hover:text-foreground underline"
            >
              Go back
            </button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const bookingData = {
    ...booking,
    equipmentName: equipment?.name || 'Equipment',
    clientSecret,
    paymentIntentId,
  }

  const appearance = {
    theme: 'stripe',
    variables: {
      colorPrimary: '#0F172A',
    },
  }

  return (
    <Elements stripe={stripePromise} options={{ clientSecret, appearance }}>
      <CheckoutForm
        booking={bookingData}
        onSuccess={handleSuccess}
        onCancel={onCancel}
      />
    </Elements>
  )
}

