import React from 'react'
import { Check, Zap, TrendingUp, Home, Gift } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const PricingPage = ({ user, onViewChange }) => {
  const boostOptions = [
    {
      id: 'boost_7_days',
      name: 'Boost 7 Days',
      price: 2.99,
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      popular: true,
      features: [
        'Top of search results for 7 days',
        'Increased visibility',
        'More inquiries and bookings',
        'Perfect for quick rentals',
        'Best value for short-term boost'
      ]
    },
    {
      id: 'boost_30_days',
      name: 'Boost 30 Days',
      price: 9.99,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-500',
      features: [
        'Top of search results for 30 days',
        'Maximum visibility all month',
        'Consistent bookings',
        'Best for high-value items',
        'Save 66% vs. daily boosting'
      ]
    },
    {
      id: 'homepage_featured',
      name: 'Homepage Featured',
      price: 19.99,
      icon: Home,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-500',
      features: [
        'Featured on homepage carousel',
        'Maximum exposure to all visitors',
        'Premium placement for 7 days',
        'Best for unique/premium items',
        'Highest conversion rate'
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-6 py-2 rounded-full font-semibold mb-6">
            <Gift className="w-5 h-5" />
            <span>Everything is FREE!</span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            List for Free, Boost When You Want
          </h1>
          <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto">
            Create unlimited listings at no cost. Only pay when you want to boost your listing to the top. 
            No subscriptions, no transaction fees, no hidden costs.
          </p>
          
          <div className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-green-500">
              <Check className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">Unlimited Listings</h3>
              <p className="text-sm text-gray-600">List as many items as you want, forever free</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-green-500">
              <Check className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">No Transaction Fees</h3>
              <p className="text-sm text-gray-600">Keep 100% of your earnings, always</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-green-500">
              <Check className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">Pay Only to Boost</h3>
              <p className="text-sm text-gray-600">Boost individual listings when you need visibility</p>
            </div>
          </div>
        </div>

        {/* What's Free Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">Everything You Need, Completely Free</h2>
          <Card className="max-w-4xl mx-auto">
            <CardContent className="pt-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Unlimited Listings</p>
                      <p className="text-sm text-gray-600">List as much gear as you want</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Full Messaging</p>
                      <p className="text-sm text-gray-600">Chat with renters unlimited</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Profile Reviews</p>
                      <p className="text-sm text-gray-600">Build your reputation</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Rental Contracts</p>
                      <p className="text-sm text-gray-600">Legal protection included</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">50% Deposit Option</p>
                      <p className="text-sm text-gray-600">Flexible payment for renters</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Secure Payments</p>
                      <p className="text-sm text-gray-600">Stripe-powered processing</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">Calendar Management</p>
                      <p className="text-sm text-gray-600">Track bookings easily</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold">NO Transaction Fees</p>
                      <p className="text-sm text-gray-600">Keep 100% of earnings</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Boost Options */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-4">Boost Your Listings When You Need Visibility</h2>
          <p className="text-center text-gray-600 mb-8 max-w-2xl mx-auto">
            Your listings are always visible. Boost them to the top of search results when you want more bookings.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8">
            {boostOptions.map((option) => {
              const Icon = option.icon

              return (
                <Card 
                  key={option.id}
                  className={`relative ${option.popular ? 'ring-2 ring-blue-500 shadow-xl scale-105' : 'shadow-lg'} ${option.borderColor} transition-all hover:shadow-2xl`}
                >
                  {option.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-blue-500 text-white px-4 py-1 text-sm font-semibold">
                        MOST POPULAR
                      </Badge>
                    </div>
                  )}

                  <CardHeader className={`${option.bgColor} rounded-t-lg`}>
                    <div className="flex items-center gap-3 mb-2">
                      <Icon className={`w-8 h-8 ${option.color}`} />
                      <CardTitle className="text-2xl">{option.name}</CardTitle>
                    </div>
                    
                    <div className="mt-6">
                      <div className="flex items-baseline gap-2">
                        <span className="text-5xl font-bold">${option.price}</span>
                        <span className="text-gray-600">one-time</span>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-6">
                    <ul className="space-y-3">
                      {option.features.map((feature, index) => (
                        <li key={index} className="flex items-start gap-3">
                          <Check className="w-5 h-5 flex-shrink-0 mt-0.5 text-green-600" />
                          <span className="text-sm text-gray-600">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>

                  <CardFooter>
                    <Button
                      onClick={() => {
                        if (!user) {
                          alert('Please sign in to boost listings')
                          return
                        }
                        onViewChange('equipment')
                      }}
                      className={`w-full ${
                        option.id === 'boost_7_days'
                          ? 'bg-blue-600 hover:bg-blue-700'
                          : option.id === 'boost_30_days'
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-purple-600 hover:bg-purple-700'
                      }`}
                    >
                      Boost a Listing
                    </Button>
                  </CardFooter>
                </Card>
              )
            })}
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                </div>
                <CardTitle className="text-lg">List Your Gear</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Create unlimited listings for free. Add photos, descriptions, and pricing.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-green-600">2</span>
                </div>
                <CardTitle className="text-lg">Get Bookings</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Renters find your gear, message you, and book. You keep 100% of earnings.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-purple-600">3</span>
                </div>
                <CardTitle className="text-lg">Boost When Needed</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Want more visibility? Boost your listing to the top for just a few dollars.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-orange-600">4</span>
                </div>
                <CardTitle className="text-lg">Earn More</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Boosted listings get 3-5x more views and bookings. Pay only when you need it.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Is it really completely free to list?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Yes! You can create unlimited listings, message renters, get reviews, and use rental contracts 
                  completely free. We only charge when you choose to boost a listing for extra visibility.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Do you take a percentage of my earnings?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  No! Unlike other platforms that take 10-20% of every rental, we charge ZERO transaction fees. 
                  You keep 100% of what you earn. We only make money when you choose to boost listings.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">When should I boost my listing?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Boost when you want more bookings! Great times to boost: new listings, slow seasons, 
                  high-value items, or when you have availability and want to fill it quickly.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">How much more visibility do boosted listings get?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Boosted listings appear at the top of search results and get 3-5x more views on average. 
                  Homepage featured listings get even more exposure, appearing on the homepage to all visitors.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Can I boost multiple listings?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Absolutely! You can boost as many listings as you want. Each boost is independent, 
                  so you can boost different items for different durations based on your needs.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">What happens when my boost expires?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Your listing returns to normal search results. It's still visible and bookable, 
                  just not at the top. You can boost it again anytime if you want more visibility.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-none">
            <CardContent className="py-12">
              <h2 className="text-3xl font-bold mb-4">Start Listing for Free Today</h2>
              <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
                Join hundreds of outdoor enthusiasts earning money from gear sitting in their garage. 
                No subscriptions, no fees, just pure earnings.
              </p>
              <div className="flex gap-4 justify-center">
                <Button 
                  onClick={() => onViewChange('equipment')}
                  size="lg"
                  className="bg-white text-blue-600 hover:bg-gray-100"
                >
                  List Your First Item Free
                </Button>
                <Button 
                  onClick={() => onViewChange('browse')}
                  size="lg"
                  variant="outline"
                  className="border-white text-white hover:bg-white/10"
                >
                  Browse Equipment
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default PricingPage

