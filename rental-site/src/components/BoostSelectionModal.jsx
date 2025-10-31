import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Zap, CheckCircle } from 'lucide-react'

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
              <Card 
                key={equipment.id} 
                className="cursor-pointer hover:bg-gray-50 transition-colors hover:shadow-md"
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{equipment.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{equipment.description}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        <span className="font-medium">${equipment.daily_price}/day</span>
                        {' • '}
                        <span>{equipment.location}</span>
                      </p>
                      {equipment.is_boosted && equipment.boost_expires_at && (
                        <p className="text-xs text-blue-600 mt-2 flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          Currently boosted until {new Date(equipment.boost_expires_at).toLocaleDateString()}
                        </p>
                      )}
                      {equipment.is_homepage_featured && equipment.homepage_featured_expires_at && (
                        <p className="text-xs text-purple-600 mt-2 flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          Homepage featured until {new Date(equipment.homepage_featured_expires_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <Button
                      onClick={() => onSelect(equipment.id)}
                      className="ml-4 bg-blue-600 hover:bg-blue-700"
                    >
                      Boost This
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Zap className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium mb-2">No Equipment Listed Yet</p>
              <p className="text-sm mb-4">You need to create an equipment listing before you can boost it.</p>
              <Button
                onClick={() => {
                  onClose()
                  // The parent component should handle navigation to equipment page
                }}
                className="mt-2"
              >
                Create Your First Listing
              </Button>
            </div>
          )}
        </div>
        
        {myEquipment && myEquipment.length > 0 && (
          <div className="border-t pt-4 mt-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-900 mb-1">How Boosting Works</p>
                  <ul className="text-blue-700 space-y-1">
                    <li>• Your equipment appears at the top of search results</li>
                    <li>• Increased visibility leads to more bookings</li>
                    <li>• Boost duration: {boost.duration_days} days</li>
                    <li>• One-time payment of ${boost.price}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

export default BoostSelectionModal

