import React from 'react'
import { Check, X, Zap, Briefcase, Gift } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const PricingPage = ({ user, onUpgrade, onViewChange }) => {
  const currentTier = user?.subscription_tier || 'free'

  const tiers = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      period: 'forever',
      description: 'Perfect for trying out the platform',
      icon: Gift,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      features: [
        { text: 'List up to 3 items', included: true },
        { text: 'Basic listing photos (3 per item)', included: true },
        { text: 'Standard search visibility', included: true },
        { text: 'Full messaging access', included: true, highlight: true },
        { text: 'Profile reviews (give & receive)', included: true, highlight: true },
        { text: 'Basic rental contract template', included: true, highlight: true },
        { text: '50% deposit option', included: true, highlight: true },
        { text: 'Secure payment processing', included: true },
        { text: '7-day booking window', included: true },
        { text: 'NO transaction fees', included: true, highlight: true },
        { text: 'NO hidden costs', included: true, highlight: true },
        { text: 'Unlimited listings', included: false },
        { text: 'Priority search placement', included: false },
        { text: 'Advanced analytics', included: false },
        { text: 'Premium contracts', included: false }
      ]
    },
    {
      id: 'pro',
      name: 'Pro Owner',
      price: 5,
      period: 'month',
      description: 'For active owners with multiple items',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      popular: true,
      features: [
        { text: 'Everything in Free, PLUS:', included: true, bold: true },
        { text: 'Unlimited listings', included: true, highlight: true },
        { text: 'Priority search placement', included: true, highlight: true },
        { text: 'Up to 10 photos per item', included: true },
        { text: 'Advanced analytics dashboard', included: true },
        { text: 'Featured badge on all listings', included: true },
        { text: 'Flexible pricing options', included: true },
        { text: 'Instant booking option', included: true },
        { text: '30-day booking window', included: true },
        { text: 'Bulk editing tools', included: true },
        { text: 'Priority customer support', included: true },
        { text: 'Revenue insights and reports', included: true },
        { text: 'Promotional tools (discount codes)', included: true },
        { text: 'Keep 100% of your earnings', included: true, highlight: true },
        { text: 'Premium rental contract templates', included: true, highlight: true },
        { text: 'Contract customization tools', included: true, highlight: true },
        { text: 'Legal protection for both parties', included: true, highlight: true }
      ]
    },
    {
      id: 'business',
      name: 'Business',
      price: 20,
      period: 'month',
      description: 'For rental businesses & outfitters',
      icon: Briefcase,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-500',
      features: [
        { text: 'Everything in Pro, PLUS:', included: true, bold: true },
        { text: 'Verified Business Badge', included: true, highlight: true },
        { text: 'Custom branding on listings', included: true },
        { text: 'Multi-user access (team accounts)', included: true },
        { text: 'Advanced inventory management', included: true },
        { text: 'Automated pricing suggestions', included: true },
        { text: 'Dedicated account manager', included: true },
        { text: 'Custom insurance options', included: true },
        { text: 'Priority placement in all searches', included: true },
        { text: 'Featured homepage placement', included: true },
        { text: 'Keep 100% of your earnings', included: true, highlight: true },
        { text: 'Premium contract templates (customizable)', included: true, highlight: true },
        { text: 'Liability waivers included', included: true, highlight: true },
        { text: 'Insurance documentation support', included: true },
        { text: 'Dispute resolution assistance', included: true },
        { text: 'Legal consultation (1 hour/year)', included: true, highlight: true }
      ]
    }
  ]

  const handleSelectPlan = (tierId) => {
    if (!user) {
      alert('Please sign in to subscribe')
      return
    }

    if (tierId === 'free') {
      alert('You\'re already on the free plan!')
      return
    }

    if (tierId === currentTier) {
      alert(`You're already subscribed to ${tierId === 'pro' ? 'Pro' : 'Business'}!`)
      return
    }

    onUpgrade(tierId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Choose the plan that's right for you. No hidden fees, ever.
          </p>
          <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-6 py-3 rounded-full font-semibold">
            <Check className="w-5 h-5" />
            <span>NO Transaction Fees • Keep 100% of Your Earnings</span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {tiers.map((tier) => {
            const Icon = tier.icon
            const isCurrentTier = currentTier === tier.id

            return (
              <Card 
                key={tier.id}
                className={`relative ${tier.popular ? 'ring-2 ring-blue-500 shadow-xl scale-105' : 'shadow-lg'} ${tier.borderColor} transition-all hover:shadow-2xl`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-500 text-white px-4 py-1 text-sm font-semibold">
                      MOST POPULAR
                    </Badge>
                  </div>
                )}

                {isCurrentTier && (
                  <div className="absolute -top-4 right-4">
                    <Badge className="bg-green-500 text-white px-3 py-1 text-xs font-semibold">
                      CURRENT PLAN
                    </Badge>
                  </div>
                )}

                <CardHeader className={`${tier.bgColor} rounded-t-lg`}>
                  <div className="flex items-center gap-3 mb-2">
                    <Icon className={`w-8 h-8 ${tier.color}`} />
                    <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  </div>
                  <CardDescription className="text-base">{tier.description}</CardDescription>
                  
                  <div className="mt-6">
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold">${tier.price}</span>
                      <span className="text-gray-600">/{tier.period}</span>
                    </div>
                    {tier.id === 'pro' && (
                      <p className="text-sm text-gray-600 mt-2">
                        Pays for itself with just 1-2 rentals!
                      </p>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="pt-6">
                  <ul className="space-y-3">
                    {tier.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        {feature.included ? (
                          <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 ${feature.highlight ? 'text-green-600' : 'text-gray-400'}`} />
                        ) : (
                          <X className="w-5 h-5 flex-shrink-0 mt-0.5 text-gray-300" />
                        )}
                        <span className={`text-sm ${feature.bold ? 'font-semibold text-gray-900' : 'text-gray-600'} ${feature.highlight ? 'text-green-700 font-medium' : ''} ${!feature.included ? 'text-gray-400 line-through' : ''}`}>
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>
                </CardContent>

                <CardFooter>
                  <Button
                    onClick={() => handleSelectPlan(tier.id)}
                    disabled={isCurrentTier}
                    className={`w-full ${
                      tier.popular 
                        ? 'bg-blue-600 hover:bg-blue-700' 
                        : tier.id === 'business'
                        ? 'bg-purple-600 hover:bg-purple-700'
                        : 'bg-gray-600 hover:bg-gray-700'
                    } ${isCurrentTier ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isCurrentTier ? 'Current Plan' : tier.id === 'free' ? 'Get Started Free' : `Upgrade to ${tier.name}`}
                  </Button>
                </CardFooter>
              </Card>
            )
          })}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Are there really no transaction fees?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Yes! Unlike other platforms that charge 10-20% per transaction, we charge ZERO fees. 
                  You keep 100% of what you earn. We only charge a simple monthly subscription.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Can I cancel anytime?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Absolutely! You can cancel your Pro or Business subscription at any time. 
                  Your plan will remain active until the end of your billing period, then you'll be moved to the Free plan.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">What happens if I downgrade?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  If you downgrade from Pro/Business to Free, you'll keep all your existing listings, 
                  but you won't be able to add more than 3 items. Your analytics and premium features will be disabled, 
                  but your data is safe and will be restored if you upgrade again.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">How does the 50% deposit option work?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Renters can choose to pay 50% when booking and 50% at pickup. This makes expensive items 
                  more accessible and increases booking rates. You're still fully protected, and the remaining 
                  payment is automatically charged at the start date.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">What's included in the rental contracts?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Free users get a basic rental agreement template. Pro users get premium templates with 
                  customization options. Business users get fully customizable contracts, liability waivers, 
                  and insurance documentation. All contracts include damage protection, late return policies, 
                  and cancellation terms.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Can I try Pro before committing?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Yes! We offer a 30-day free trial for Pro subscriptions. Try all the premium features 
                  risk-free, and cancel anytime during the trial with no charges.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-none">
            <CardContent className="py-12">
              <h2 className="text-3xl font-bold mb-4">Ready to Start Earning?</h2>
              <p className="text-xl mb-8 opacity-90">
                Join hundreds of outdoor enthusiasts making money from gear sitting in their garage.
              </p>
              <div className="flex gap-4 justify-center">
                <Button 
                  onClick={() => onViewChange('equipment')}
                  size="lg"
                  className="bg-white text-blue-600 hover:bg-gray-100"
                >
                  List Your First Item
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

