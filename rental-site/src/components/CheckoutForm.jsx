import { useState } from 'react'
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Loader2, CreditCard, Shield, CheckCircle2 } from 'lucide-react'

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  },
}

export default function CheckoutForm({ booking, onSuccess, onCancel }) {
  const stripe = useStripe()
  const elements = useElements()
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [succeeded, setSucceeded] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setProcessing(true)
    setError(null)

    try {
      // Get the CardElement
      const cardElement = elements.getElement(CardElement)

      // Create payment method
      const { error: methodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
      })

      if (methodError) {
        throw new Error(methodError.message)
      }

      // Confirm the payment with the server
      const { error: confirmError } = await stripe.confirmCardPayment(booking.clientSecret, {
        payment_method: paymentMethod.id,
      })

      if (confirmError) {
        throw new Error(confirmError.message)
      }

      setSucceeded(true)
      setTimeout(() => {
        onSuccess(booking.paymentIntentId)
      }, 1500)

    } catch (err) {
      setError(err.message)
      setProcessing(false)
    }
  }

  const totalAmount = booking.rentalCost + booking.depositAmount
  const platformFee = booking.platformFee
  const ownerReceives = booking.rentalCost - platformFee

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Complete Your Booking
        </CardTitle>
        <CardDescription>
          Enter your payment information to confirm your rental
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Booking Summary */}
        <div className="bg-muted/50 p-4 rounded-lg space-y-3">
          <h3 className="font-semibold text-sm text-muted-foreground uppercase">Booking Summary</h3>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Equipment:</span>
              <span className="font-medium">{booking.equipmentName}</span>
            </div>
            <div className="flex justify-between">
              <span>Rental Period:</span>
              <span className="font-medium">{booking.totalDays} days</span>
            </div>
            <div className="flex justify-between">
              <span>Daily Rate:</span>
              <span className="font-medium">${booking.dailyRate.toFixed(2)}</span>
            </div>
          </div>

          <div className="border-t pt-3 space-y-2">
            <div className="flex justify-between">
              <span>Rental Cost:</span>
              <span className="font-medium">${booking.rentalCost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Platform Fee (10%):</span>
              <span className="text-muted-foreground">${platformFee.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Owner Receives (90%):</span>
              <span className="text-muted-foreground">${ownerReceives.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Security Deposit (50%):</span>
              <span className="font-medium">${booking.depositAmount.toFixed(2)}</span>
            </div>
          </div>

          <div className="border-t pt-3">
            <div className="flex justify-between text-lg font-bold">
              <span>Total Due Today:</span>
              <span>${totalAmount.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Security Deposit Info */}
        <Alert>
          <Shield className="h-4 w-4" />
          <AlertDescription>
            <strong>Security Deposit:</strong> The ${booking.depositAmount.toFixed(2)} deposit will be refunded in full when you return the equipment in good condition.
          </AlertDescription>
        </Alert>

        {/* Payment Form */}
        {!succeeded && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="border rounded-lg p-4 bg-background">
              <label className="block text-sm font-medium mb-2">
                Card Information
              </label>
              <CardElement options={CARD_ELEMENT_OPTIONS} />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={processing}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!stripe || processing}
                className="flex-1"
              >
                {processing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>Pay ${totalAmount.toFixed(2)}</>
                )}
              </Button>
            </div>
          </form>
        )}

        {/* Success State */}
        {succeeded && (
          <div className="text-center py-8 space-y-4">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto" />
            <div>
              <h3 className="text-xl font-semibold text-green-600">Payment Successful!</h3>
              <p className="text-muted-foreground mt-2">
                Your booking has been confirmed. Redirecting...
              </p>
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="text-xs text-muted-foreground border-t pt-4">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4" />
          <span>Payments are securely processed by Stripe. Your card information is never stored on our servers.</span>
        </div>
      </CardFooter>
    </Card>
  )
}

