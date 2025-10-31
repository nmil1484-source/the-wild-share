import { useEffect, useRef } from 'react'

const PayPalBoostButton = ({ amount, boostType, equipmentId, onSuccess, onError }) => {
  const paypalRef = useRef()

  useEffect(() => {
    // Check if PayPal SDK is loaded
    if (window.paypal && paypalRef.current) {
      // Clear any existing buttons
      paypalRef.current.innerHTML = ''
      
      window.paypal.Buttons({
        createOrder: (data, actions) => {
          return actions.order.create({
            purchase_units: [{
              amount: {
                value: amount.toFixed(2),
                currency_code: 'USD'
              },
              description: `Boost: ${boostType.replace('_', ' ')}`,
              custom_id: `${equipmentId}_${boostType}_${Date.now()}`
            }]
          })
        },
        onApprove: async (data, actions) => {
          try {
            const order = await actions.order.capture()
            console.log('Payment successful:', order)
            
            // Call success handler
            if (onSuccess) {
              onSuccess(order, equipmentId, boostType)
            }
          } catch (error) {
            console.error('Error capturing order:', error)
            if (onError) {
              onError(error)
            }
          }
        },
        onError: (err) => {
          console.error('PayPal error:', err)
          if (onError) {
            onError(err)
          }
        },
        onCancel: () => {
          console.log('Payment cancelled by user')
          alert('Payment cancelled. You can try again anytime.')
        },
        style: {
          layout: 'vertical',
          color: 'blue',
          shape: 'rect',
          label: 'paypal',
          height: 45
        }
      }).render(paypalRef.current)
    }
  }, [amount, boostType, equipmentId, onSuccess, onError])

  return (
    <div>
      <div ref={paypalRef} className="w-full min-h-[50px]"></div>
      <p className="text-xs text-gray-500 text-center mt-2">
        Secure payment powered by PayPal
      </p>
    </div>
  )
}

export default PayPalBoostButton

