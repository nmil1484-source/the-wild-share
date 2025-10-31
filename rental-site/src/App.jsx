import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Mountain, Zap, Wifi, Sun, Waves, Tent, ChevronRight, ChevronLeft, Calendar, Shield, Clock, User, LogOut, Plus, Edit, Trash2, Settings, Upload, AlertTriangle, Bike, Backpack, Droplet, FileText, Download, Mail, Send, Star } from 'lucide-react'
import './App.css'
import { authAPI, equipmentAPI, bookingsAPI, identityAPI, messagesAPI, reviewsAPI } from './lib/api'
import StripeCheckout from './components/StripeCheckout'
import AdminDashboard from './components/AdminDashboard'
import PricingPage from './components/PricingPage'
import BoostSelectionModal from './components/BoostSelectionModal'
import { TermsOfServiceView, PrivacyPolicyView } from './legal_views'

function App() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [user, setUser] = useState(null)
  const [equipment, setEquipment] = useState([])
  const [myEquipment, setMyEquipment] = useState([])
  const [myBookings, setMyBookings] = useState([])
  const [showAuthDialog, setShowAuthDialog] = useState(false)
  const [authMode, setAuthMode] = useState('login') // 'login', 'register', 'forgot-password', 'reset-password'
  const [resetToken, setResetToken] = useState('')
  const [resetEmail, setResetEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentView, setCurrentView] = useState('home')
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [editingEquipment, setEditingEquipment] = useState(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [locationFilter, setLocationFilter] = useState('all')
  const [carouselIndexes, setCarouselIndexes] = useState({}) // Track current image for each equipment

  // Auth form state
  const [authForm, setAuthForm] = useState({
    terms_agreed: false,
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    user_type: 'both'
  })

  // Equipment form state
  const [equipmentForm, setEquipmentForm] = useState({
    name: '',
    description: '',
    category: 'bikes',
    daily_price: '',
    weekly_price: '',
    monthly_price: '',
    capacity_spec: '',
    image_url: '',
    location: '',
    security_deposit: ''
  })
  const [equipmentImages, setEquipmentImages] = useState([])
  const [imagePreviewUrls, setImagePreviewUrls] = useState([])
  const [uploadingImages, setUploadingImages] = useState(false)

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    bio: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    profile_image_url: ''
  })
  const [profileImage, setProfileImage] = useState(null)
  const [profileImagePreview, setProfileImagePreview] = useState('')

  // Booking form state
  const [bookingForm, setBookingForm] = useState({
    equipment_id: null,
    start_date: '',
    end_date: ''
  })
  const [showBookingDialog, setShowBookingDialog] = useState(false)
  const [selectedEquipment, setSelectedEquipment] = useState(null)
  const [currentBooking, setCurrentBooking] = useState(null)
  const [showCheckout, setShowCheckout] = useState(false)
  const [conversations, setConversations] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [conversationMessages, setConversationMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [showReviewDialog, setShowReviewDialog] = useState(false)
  const [reviewingBooking, setReviewingBooking] = useState(null)
  const [reviewForm, setReviewForm] = useState({
    equipment_rating: 5,
    owner_rating: 5,
    equipment_review: '',
    owner_review: ''
  })

  // Boost purchase states
  const [showBoostModal, setShowBoostModal] = useState(false)
  const [selectedBoostType, setSelectedBoostType] = useState(null)
  const [boostPricing] = useState({
    boost_7_days: { name: 'Boost 7 Days', price: 2.99, duration_days: 7 },
    boost_30_days: { name: 'Boost 30 Days', price: 9.99, duration_days: 30 },
    homepage_featured: { name: 'Homepage Featured', price: 19.99, duration_days: 7 }
  })

  const categories = [
    { id: 'all', name: 'All Equipment', icon: Mountain },
    { id: 'bikes', name: 'Bikes & Racks', icon: Bike },
    { id: 'water', name: 'Water Sports', icon: Droplet },
    { id: 'camping', name: 'Camping', icon: Tent },
    { id: 'power', name: 'Power & Solar', icon: Zap },
    { id: 'gear', name: 'Gear & Accessories', icon: Backpack }
  ]

  const features = [
    {
      icon: Calendar,
      title: 'Flexible Rentals',
      description: 'Daily, weekly, and monthly rental options available'
    },
    {
      icon: Shield,
      title: 'Deposit Protection',
      description: 'Secure deposits held and refunded after equipment return'
    },
    {
      icon: Clock,
      title: 'Instant Booking',
      description: 'Book equipment instantly and manage your rentals online'
    }
  ]

  // Load user and equipment on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    
    // Load user from localStorage first for immediate display
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (e) {
        console.error('Failed to parse saved user:', e)
      }
    }
    
    // Then refresh from API if we have a token
    if (token) {
      loadUser()
    }
    loadEquipment()
    
    // Check for password reset token in URL
    const urlParams = new URLSearchParams(window.location.search)
    const resetTokenParam = urlParams.get('token')
    if (resetTokenParam) {
      setResetToken(resetTokenParam)
      setAuthMode('reset-password')
      setShowAuthDialog(true)
      // Clear the token from URL for security
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  // Load equipment when category changes
  useEffect(() => {
    loadEquipment()
  }, [selectedCategory])

  // Update profile form when user changes
  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        email: user.email || '',
        bio: user.bio || '',
        address: user.address || '',
        city: user.city || '',
        state: user.state || '',
        zip_code: user.zip_code || '',
        profile_image_url: user.profile_image_url || ''
      })
    }
  }, [user])

  // Check for Stripe boost success callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const sessionId = urlParams.get('session_id')
    
    if (sessionId && window.location.pathname.includes('/boost/success')) {
      handleBoostSuccess(sessionId)
      // Clean up URL
      window.history.replaceState({}, document.title, '/equipment')
    }
  }, [])

  const loadUser = async () => {
    try {
      const response = await authAPI.getProfile()
      localStorage.setItem('user', JSON.stringify(response.data))
      setUser(response.data)
      if (response.data.user_type === 'owner' || response.data.user_type === 'both') {
        loadMyEquipment()
      }
      loadMyBookings()
      loadMessages()
      loadUnreadCount()
    } catch (error) {
      console.error('Failed to load user:', error)
      localStorage.removeItem('access_token')
    }
  }

  const loadEquipment = async () => {
    try {
      const response = await equipmentAPI.getAll(selectedCategory)
      // API returns {equipment: [...], total_count: N}
      const equipmentData = response.data.equipment || response.data
      setEquipment(Array.isArray(equipmentData) ? equipmentData : [])
    } catch (error) {
      console.error('Failed to load equipment:', error)
      setEquipment([])
    }
  }

  const loadMyEquipment = async () => {
    try {
      const response = await equipmentAPI.getMyEquipment()
      setMyEquipment(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Failed to load my equipment:', error)
      setMyEquipment([])
    }
  }

  const loadMessages = async () => {
    try {
      const response = await messagesAPI.getMyMessages();
      setConversations(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setConversations([]);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await messagesAPI.getUnreadCount();
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  const loadConversationMessages = async (equipmentId) => {
    try {
      const response = await messagesAPI.getEquipmentMessages(equipmentId);
      setConversationMessages(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      setConversationMessages([]);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!reviewingBooking) return;
    
    setLoading(true);
    try {
      await reviewsAPI.createReview(reviewingBooking.id, reviewForm);
      alert('Review submitted successfully!');
      setShowReviewDialog(false);
      setReviewingBooking(null);
      setReviewForm({
        equipment_rating: 5,
        owner_rating: 5,
        equipment_review: '',
        owner_review: ''
      });
      await loadMyBookings();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;
    
    setLoading(true);
    try {
      await messagesAPI.sendMessage(selectedConversation.equipment_id, newMessage);
      setNewMessage('');
      await loadConversationMessages(selectedConversation.equipment_id);
      await loadMessages();
      await loadUnreadCount();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const loadMyBookings = async () => {
    try {
      const response = await bookingsAPI.getMyBookings()
      setMyBookings(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Failed to load bookings:', error)
      setMyBookings([])
    }
  }

  const handleAuth = async (e) => {
    if (authMode === 'register' && !authForm.terms_agreed) {
      alert('You must agree to the Terms of Service and Privacy Policy to create an account.');
      return;
    }
    e.preventDefault()
    setLoading(true)
    try {
      if (authMode === 'forgot-password') {
        // Request password reset
        const response = await authAPI.requestPasswordReset({ email: authForm.email })
        alert(response.data.message)
        // In development, show the reset link
        if (response.data.reset_link) {
          console.log('Reset link:', response.data.reset_link)
          console.log('Reset token:', response.data.token)
          // Auto-fill token for testing
          setResetToken(response.data.token)
          setResetEmail(authForm.email)
          setAuthMode('reset-password')
        } else {
          setShowAuthDialog(false)
        }
      } else if (authMode === 'reset-password') {
        // Reset password with token
        await authAPI.resetPassword({ token: resetToken, new_password: authForm.password })
        alert('Password reset successful! You can now log in with your new password.')
        setAuthMode('login')
        setResetToken('')
        setAuthForm({ email: resetEmail, password: '', first_name: '', last_name: '', phone: '', user_type: 'both' })
      } else {
        // Normal login or register
        const response = authMode === 'login' 
          ? await authAPI.login({ email: authForm.email, password: authForm.password })
          : await authAPI.register(authForm)
        
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        setUser(response.data.user)
        setShowAuthDialog(false)
        setAuthForm({ email: '', password: '', first_name: '', last_name: '', phone: '', user_type: 'both' })
        loadEquipment()
        if (response.data.user.user_type === 'owner' || response.data.user.user_type === 'both') {
          loadMyEquipment()
        }
        loadMyBookings()
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  const handleStartVerification = async () => {
    setLoading(true);
    try {
      const response = await identityAPI.createVerificationSession();
      // Open Stripe Identity verification in new window
      window.open(response.data.url, '_blank');
      alert('Verification window opened! Complete the verification process and then refresh this page.');
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to start verification');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
    setMyEquipment([])
    setMyBookings([])
    setEquipment([])  // Clear equipment list
    // Clear all form state to prevent data leakage
    setEquipmentForm({ name: '', description: '', category: 'bikes', daily_price: '', weekly_price: '', monthly_price: '', capacity_spec: '', image_url: '', location: '' })
    setEquipmentImages([])
    setImagePreviewUrls([])
    setProfileForm({ first_name: '', last_name: '', phone: '', email: '', bio: '', address: '', city: '', state: '', zip_code: '', profile_image_url: '' })
    setBookingForm({ equipment_id: null, start_date: '', end_date: '' })
    setAuthForm({ email: '', password: '', first_name: '', last_name: '', phone: '', user_type: 'both' })
    setCurrentView('browse')
    // Reload all equipment after logout
    setTimeout(() => loadEquipment(), 100)
  }

  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files)
    
    // Check if adding these files would exceed the limit
    if (equipmentImages.length + files.length > 5) {
      alert(`Maximum 5 images allowed. You can add ${5 - equipmentImages.length} more image(s).`)
      return
    }
    
    // Append new files to existing images
    setEquipmentImages(prev => [...prev, ...files])
    
    // Create preview URLs for new files and append to existing previews
    const newPreviews = files.map(file => URL.createObjectURL(file))
    setImagePreviewUrls(prev => [...prev, ...newPreviews])
    
    // Clear the input so the same file can be selected again if needed
    e.target.value = ''
  }

  const handleRemoveImage = (index) => {
    const newImages = equipmentImages.filter((_, i) => i !== index)
    const newPreviews = imagePreviewUrls.filter((_, i) => i !== index)
    setEquipmentImages(newImages)
    setImagePreviewUrls(newPreviews)
  }

  const handleCarouselNext = (equipmentId, totalImages) => {
    setCarouselIndexes(prev => ({
      ...prev,
      [equipmentId]: ((prev[equipmentId] || 0) + 1) % totalImages
    }))
  }

  const handleCarouselPrev = (equipmentId, totalImages) => {
    setCarouselIndexes(prev => ({
      ...prev,
      [equipmentId]: ((prev[equipmentId] || 0) - 1 + totalImages) % totalImages
    }))
  }

  const handleProfileImageSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Please upload PNG, JPG, GIF, or WEBP')
      return
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File too large. Maximum size is 5MB')
      return
    }
    
    setProfileImage(file)
    setProfileImagePreview(URL.createObjectURL(file))
  }

  const handleCreateEquipment = async (e) => {
    e.preventDefault()
    setLoading(true)
    setUploadingImages(true)
    
    try {
      let imageUrls = []
      
      // Upload images if any
      if (equipmentImages.length > 0) {
        const formData = new FormData()
        equipmentImages.forEach(file => {
          formData.append('files', file)
        })
        
        const uploadResponse = await fetch('/api/upload/images', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: formData
        })
        
        if (!uploadResponse.ok) {
          throw new Error('Failed to upload images')
        }
        
        const uploadData = await uploadResponse.json()
        imageUrls = uploadData.image_urls
      }
      
      setUploadingImages(false)
      
      // Create equipment with image URLs
      await equipmentAPI.create({
        ...equipmentForm,
        image_urls: imageUrls
      })
      
      // Reset form
      setEquipmentForm({ name: '', description: '', category: 'bikes', daily_price: '', weekly_price: '', monthly_price: '', capacity_spec: '', image_url: '', location: '', security_deposit: '' })
      setEquipmentImages([])
      setImagePreviewUrls([])
      
      loadMyEquipment()
      loadEquipment()
      alert('Equipment created successfully!')
    } catch (error) {
      alert(error.response?.data?.error || error.message || 'Failed to create equipment')
    } finally {
      setLoading(false)
      setUploadingImages(false)
    }
  }

  const handleEditEquipment = (item) => {
    setEditingEquipment(item)
    setEquipmentForm({
      name: item.name,
      description: item.description,
      category: item.category,
      daily_price: item.daily_price,
      weekly_price: item.weekly_price,
      monthly_price: item.monthly_price,
      capacity_spec: item.capacity_spec,
      image_url: item.image_url,
      location: item.location,
      security_deposit: item.security_deposit || ''
    })
    // Reset image states when opening edit modal
    setEquipmentImages([])
    setImagePreviewUrls([])
    setShowEditDialog(true)
  }

  const handleUpdateEquipment = async (e) => {
    e.preventDefault()
    setLoading(true)
    setUploadingImages(true)
    
    try {
      let updateData = { ...equipmentForm }
      
      // Upload new images if any were selected
      if (equipmentImages.length > 0) {
        const formData = new FormData()
        equipmentImages.forEach(file => {
          formData.append('files', file)
        })
        
        const uploadResponse = await fetch('/api/upload/images', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: formData
        })
        
        if (!uploadResponse.ok) {
          throw new Error('Failed to upload images')
        }
        
        const uploadData = await uploadResponse.json()
        updateData.image_urls = uploadData.image_urls
      }
      
      setUploadingImages(false)
      
      await equipmentAPI.update(editingEquipment.id, updateData)
      setShowEditDialog(false)
      setEditingEquipment(null)
      setEquipmentForm({ name: '', description: '', category: 'power', daily_price: '', weekly_price: '', monthly_price: '', capacity_spec: '', image_url: '', location: '', security_deposit: '' })
      setEquipmentImages([])
      setImagePreviewUrls([])
      loadMyEquipment()
      loadEquipment()
      alert('Equipment updated successfully!')
    } catch (error) {
      alert(error.response?.data?.error || error.message || 'Failed to update equipment')
    } finally {
      setLoading(false)
      setUploadingImages(false)
    }
  }

  const handleDeleteEquipment = async (id) => {
    if (!confirm('Are you sure you want to delete this equipment?')) return
    try {
      await equipmentAPI.delete(id)
      loadMyEquipment()
      loadEquipment()
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to delete equipment')
    }
  }

  const handleCreateBooking = async (equipmentId) => {
    if (!user) {
      alert('Please sign in to book equipment')
      setShowAuthDialog(true)
      return
    }

    const equipment = filteredEquipment.find(e => e.id === equipmentId)
    setSelectedEquipment(equipment)
    setBookingForm({ ...bookingForm, equipment_id: equipmentId })
    setShowBookingDialog(true)
  }

  const handleSubmitBooking = async (e) => {
    e.preventDefault()
    
    if (!bookingForm.start_date || !bookingForm.end_date) {
      alert('Please select both start and end dates')
      return
    }

    setLoading(true)
    try {
      const response = await bookingsAPI.create({
        equipment_id: bookingForm.equipment_id,
        start_date: bookingForm.start_date,
        end_date: bookingForm.end_date
      })
      
      setCurrentBooking(response.data.booking)
      setShowBookingDialog(false)
      setShowCheckout(true)
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to create booking')
    } finally {
      setLoading(false)
    }
  }

  const handlePaymentSuccess = async () => {
    setShowCheckout(false)
    setCurrentBooking(null)
    setSelectedEquipment(null)
    setBookingForm({ equipment_id: null, start_date: '', end_date: '' })
    alert('Payment successful! Your booking is confirmed.')
    await loadMyBookings()
    setCurrentView('bookings')
  }

  const handleCancelCheckout = () => {
    setShowCheckout(false)
    setCurrentBooking(null)
    setSelectedEquipment(null)
    setBookingForm({ equipment_id: null, start_date: '', end_date: '' })
  }

  // Boost purchase handler
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
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
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

  // Handle boost success callback from Stripe
  const handleBoostSuccess = async (sessionId) => {
    setLoading(true)
    
    try {
      const response = await fetch(`${API_URL}/api/boost/success`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        alert(`🎉 Boost activated successfully! Your equipment will be featured until ${new Date(data.expires_at).toLocaleDateString()}`)
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

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      let updatedProfileData = { ...profileForm }
      
      // Upload profile image if selected
      if (profileImage) {
        const formData = new FormData()
        formData.append('file', profileImage)
        
        const uploadResponse = await fetch('/api/upload/image', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: formData
        })
        
        if (uploadResponse.ok) {
          const uploadData = await uploadResponse.json()
          updatedProfileData.profile_image_url = uploadData.image_url
        }
      }
      
      const response = await authAPI.updateProfile(updatedProfileData)
      setUser(response.data.user)
      setProfileImage(null)
      setProfileImagePreview('')
      alert('Profile updated successfully!')
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone and will delete all your equipment and bookings.')) {
      return
    }
    
    setLoading(true)
    try {
      await authAPI.deleteAccount()
      localStorage.removeItem('access_token')
      setUser(null)
      setMyEquipment([])
      setMyBookings([])
      setCurrentView('browse')
      setShowDeleteConfirm(false)
      alert('Account deleted successfully')
      loadEquipment()
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to delete account')
    } finally {
      setLoading(false)
    }
  }

  // Get unique locations from equipment
  const uniqueLocations = [...new Set((Array.isArray(equipment) ? equipment : []).map(item => item.location).filter(Boolean))]

  // Filter equipment by category, search, and location
  const filteredEquipment = (Array.isArray(equipment) ? equipment : [])
    .filter(item => {
      // Category filter
      if (selectedCategory !== 'all' && item.category !== selectedCategory) return false
      
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesName = item.name?.toLowerCase().includes(query)
        const matchesDescription = item.description?.toLowerCase().includes(query)
        const matchesLocation = item.location?.toLowerCase().includes(query)
        if (!matchesName && !matchesDescription && !matchesLocation) return false
      }
      
      // Location filter
      if (locationFilter !== 'all' && item.location !== locationFilter) return false
      
      return true
    })

  // If admin view, show admin dashboard only
  console.log('Current view:', currentView, 'User:', user, 'Is admin:', user?.is_admin);
  if (currentView === 'admin' && user && user.is_admin) {
    console.log('Rendering AdminDashboard');
    return <AdminDashboard user={user} onLogout={handleLogout} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Hero Section */}
      <header className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => setCurrentView('home')}>
            <Mountain className="h-8 w-8" />
            <h1 className="text-2xl font-bold">The Wild Share</h1>
          </div>
          <div className="flex gap-4 items-center">
            {user ? (
              <>
                <Button variant="ghost" className="text-white hover:bg-white/20" onClick={() => setCurrentView('browse')}>
                  Browse
                </Button>
                <Button variant="ghost" className="text-white hover:bg-white/20" onClick={() => setCurrentView('pricing')}>
                  Pricing
                </Button>
                <Button variant="ghost" className="text-white hover:bg-white/20" onClick={() => setCurrentView('bookings')}>
                  My Bookings
                </Button>
                <Button variant="ghost" className="text-white hover:bg-white/20 relative" onClick={() => setCurrentView('messages')}>
                  <Mail className="h-4 w-4 mr-2" />
                  Messages
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </Button>
                {(user.user_type === 'owner' || user.user_type === 'both') && (
                  <Button variant="ghost" className="text-white hover:bg-white/20" onClick={() => setCurrentView('equipment')}>
                    My Equipment
                  </Button>
                )}
                <button 
                  className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-white/20 transition-colors cursor-pointer"
                  onClick={() => setCurrentView('profile')}
                >
                  <User className="h-5 w-5" />
                  <span>{user.first_name}</span>
                </button>
                {user.is_admin && (
                  <Button variant="outline" className="text-white border-white hover:bg-white/20" onClick={() => { console.log('Admin button clicked, setting view to admin'); setCurrentView('admin'); }}>
                    <Shield className="h-4 w-4 mr-2" />
                    Admin
                  </Button>
                )}
                <Button variant="secondary" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <Dialog open={showAuthDialog} onOpenChange={setShowAuthDialog}>
                <DialogTrigger asChild>
                  <Button variant="secondary">Sign In</Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>
                      {authMode === 'login' && 'Sign In'}
                      {authMode === 'register' && 'Create Account'}
                      {authMode === 'forgot-password' && 'Reset Password'}
                      {authMode === 'reset-password' && 'Set New Password'}
                    </DialogTitle>
                    <DialogDescription>
                      {authMode === 'login' && 'Sign in to book equipment'}
                      {authMode === 'register' && 'Create an account to get started'}
                      {authMode === 'forgot-password' && 'Enter your email to receive a password reset link'}
                      {authMode === 'reset-password' && 'Enter your new password'}
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleAuth} className="space-y-4">
                    {authMode === 'register' && (
                      <>
                        <div>
                          <Label htmlFor="first_name">First Name</Label>
                          <Input
                            id="first_name"
                            value={authForm.first_name}
                            onChange={(e) => setAuthForm({...authForm, first_name: e.target.value})}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="last_name">Last Name</Label>
                          <Input
                            id="last_name"
                            value={authForm.last_name}
                            onChange={(e) => setAuthForm({...authForm, last_name: e.target.value})}
                            required
                          />
                        </div>
                      </>
                    )}
                    {(authMode === 'login' || authMode === 'register' || authMode === 'forgot-password') && (
                      <div>
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={authForm.email}
                          onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                          required
                          disabled={authMode === 'reset-password'}
                        />
                      </div>
                    )}
                    {(authMode === 'login' || authMode === 'register' || authMode === 'reset-password') && (
                      <div>
                        <Label htmlFor="password">{authMode === 'reset-password' ? 'New Password' : 'Password'}</Label>
                        <Input
                          id="password"
                          type="password"
                          value={authForm.password}
                          onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                          required
                          minLength={authMode === 'reset-password' ? 8 : undefined}
                        />
                        {authMode === 'reset-password' && (
                          <p className="text-sm text-gray-500 mt-1">Password must be at least 8 characters</p>
                        )}
                      </div>
                    )}
                    <Button type="submit" className="w-full" disabled={loading}>
                      {loading ? 'Loading...' : (
                        authMode === 'login' ? 'Sign In' :
                        authMode === 'register' ? 'Create Account' :
                        authMode === 'forgot-password' ? 'Send Reset Link' :
                        'Reset Password'
                      )}
                    </Button>
                    {authMode === 'login' && (
                      <Button
                        type="button"
                        variant="link"
                        className="w-full text-sm"
                        onClick={() => setAuthMode('forgot-password')}
                      >
                        Forgot password?
                      </Button>
                    )}
                                        {authMode === 'register' && (
                      <div className="flex items-center space-x-2 mt-4">
                        <input type="checkbox" id="terms" checked={authForm.terms_agreed} onChange={(e) => setAuthForm({ ...authForm, terms_agreed: e.target.checked })} />
                        <Label htmlFor="terms" className="text-sm font-normal text-muted-foreground">
                          I agree to the{" "}
                          <button type="button" onClick={() => { setShowAuthDialog(false); setCurrentView('terms-of-service'); }} className="underline hover:text-emerald-600">Terms of Service</button> and{" "}
                          <button type="button" onClick={() => { setShowAuthDialog(false); setCurrentView('privacy-policy'); }} className="underline hover:text-emerald-600">Privacy Policy</button>.
                        </Label>
                      </div>
                    )}
                    <Button
                      type="button"
                      variant="link"
                      className="w-full"
                      onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                    >
                      {authMode === 'login' ? 'Need an account? Register' : 
                       authMode === 'register' ? 'Already have an account? Sign in' :
                       'Back to Sign In'}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </nav>
        
        {currentView === 'home' && (
          <div className="container mx-auto px-4 py-20 text-center">
            <h2 className="text-5xl font-bold mb-6 animate-fade-in">
              Share the Wild, Rent the Adventure
            </h2>
            <p className="text-xl mb-8 text-emerald-50 max-w-2xl mx-auto">
              Rent premium outdoor equipment or list your own gear for others to rent. 
              From bikes and camping gear to water sports equipment.
            </p>
            <Button size="lg" className="bg-white text-emerald-600 hover:bg-emerald-50 shadow-lg" onClick={() => setCurrentView('browse')}>
              Browse Equipment <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {currentView === 'home' && (
          <>
            {/* Features Section */}
            <div className="grid md:grid-cols-3 gap-8 mb-16">
              {features.map((feature, index) => (
                <Card key={index} className="text-center">
                  <CardHeader>
                    <div className="mx-auto w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
                      <feature.icon className="h-6 w-6 text-emerald-600" />
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>

            {/* Contract Protection Banner */}
            <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-lg p-8 mb-16">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-emerald-600 rounded-full flex items-center justify-center">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-emerald-900 mb-2">Protected by Legal Rental Contracts</h3>
                  <p className="text-emerald-800 mb-4">
                    Every rental on The Wild Share is protected by a comprehensive 3-page legal contract that safeguards both renters and owners. 
                    Our contracts include clear terms for equipment condition, security deposits, liability, insurance requirements, and dispute resolution.
                  </p>
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-start gap-2">
                      <FileText className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-emerald-900">Automatic Contract Generation</p>
                        <p className="text-emerald-700">Every booking creates a legally binding contract</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <Shield className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-emerald-900">Security Deposits</p>
                        <p className="text-emerald-700">Owner-set refundable deposits protect equipment</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <Download className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-emerald-900">Download Anytime</p>
                        <p className="text-emerald-700">Access your contracts from your bookings</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Featured Equipment Section */}
            {equipment && equipment.length > 0 && (
              <div className="mb-16">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-3xl font-bold">Available Equipment</h2>
                  <Button 
                    variant="outline" 
                    onClick={() => setCurrentView('browse')}
                    className="text-emerald-600 border-emerald-600 hover:bg-emerald-50"
                  >
                    View All
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                  {equipment.slice(0, 6).map((item) => {
                    const images = item.image_urls && item.image_urls.length > 0 ? item.image_urls : (item.image_url ? [item.image_url] : [])
                    return (
                      <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer" onClick={() => { setCurrentView('browse'); }}>
                        <div className="aspect-video bg-slate-200 relative">
                          {images.length > 0 ? (
                            <img src={images[0]} alt={item.name} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <Mountain className="h-16 w-16 text-slate-400" />
                            </div>
                          )}
                          <Badge className="absolute top-2 right-2 bg-emerald-600">
                            {categories.find(c => c.id === item.category)?.name}
                          </Badge>
                        </div>
                        <CardHeader>
                          <CardTitle className="text-lg">{item.name}</CardTitle>
                          <CardDescription className="line-clamp-2">{item.description}</CardDescription>
                          {item.location && (
                            <p className="text-sm text-muted-foreground mt-2">📍 {item.location}</p>
                          )}
                        </CardHeader>
                        <CardFooter className="flex justify-between items-center">
                          <span className="text-lg font-bold text-emerald-600">${item.daily_price}/day</span>
                          <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                            View Details
                          </Button>
                        </CardFooter>
                      </Card>
                    )
                  })}
                </div>
              </div>
            )}
          </>
        )}

        {currentView === 'browse' && (
          <>
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-6">Browse Equipment</h2>
              
              {/* Search and Filters */}
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="md:col-span-1">
                  <Label htmlFor="search">Search</Label>
                  <Input
                    id="search"
                    type="text"
                    placeholder="Search by name, description, or location..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="category-filter">Category</Label>
                  <select
                    id="category-filter"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    <option value="all">All Categories</option>
                    {categories.filter(c => c.id !== 'all').map((category) => (
                      <option key={category.id} value={category.id}>{category.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="location-filter">Location</Label>
                  <select
                    id="location-filter"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    value={locationFilter}
                    onChange={(e) => setLocationFilter(e.target.value)}
                  >
                    <option value="all">All Locations</option>
                    {uniqueLocations.map((location) => (
                      <option key={location} value={location}>{location}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Results count */}
              <p className="text-sm text-muted-foreground mb-4">
                Showing {filteredEquipment.length} {filteredEquipment.length === 1 ? 'item' : 'items'}
              </p>
            </div>

            {/* Equipment Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEquipment.map((item) => {
                const images = item.image_urls && item.image_urls.length > 0 ? item.image_urls : (item.image_url ? [item.image_url] : [])
                const currentIndex = carouselIndexes[item.id] || 0
                const hasMultipleImages = images.length > 1
                
                return (
                <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="aspect-video bg-slate-200 relative group">
                    {images.length > 0 ? (
                      <>
                        <img src={images[currentIndex]} alt={item.name} className="w-full h-full object-cover" />
                        
                        {/* Carousel Navigation */}
                        {hasMultipleImages && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleCarouselPrev(item.id, images.length)
                              }}
                              className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <ChevronLeft className="h-4 w-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleCarouselNext(item.id, images.length)
                              }}
                              className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <ChevronRight className="h-4 w-4" />
                            </button>
                            
                            {/* Image Indicators */}
                            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                              {images.map((_, idx) => (
                                <div
                                  key={idx}
                                  className={`h-1.5 rounded-full transition-all ${
                                    idx === currentIndex ? 'w-6 bg-white' : 'w-1.5 bg-white/50'
                                  }`}
                                />
                              ))}
                            </div>
                          </>
                        )}
                      </>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Mountain className="h-16 w-16 text-slate-400" />
                      </div>
                    )}
                    <Badge className="absolute top-2 right-2 bg-emerald-600">
                      {categories.find(c => c.id === item.category)?.name}
                    </Badge>
                  </div>
                  <CardHeader>
                    <CardTitle>{item.name}</CardTitle>
                    <CardDescription>{item.description}</CardDescription>
                    {item.location && (
                      <p className="text-sm text-muted-foreground mt-2">📍 {item.location}</p>
                    )}
                    {/* Owner Info */}
                    {item.owner && (
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t">
                        {item.owner.profile_image_url ? (
                          <img 
                            src={item.owner.profile_image_url} 
                            alt={item.owner.name}
                            className="w-8 h-8 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                            <User className="h-4 w-4 text-slate-500" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5">
                            <p className="text-sm font-medium truncate">{item.owner.name}</p>
                            {item.owner.is_identity_verified && (
                              <Shield className="h-3.5 w-3.5 text-emerald-600" title="Verified" />
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span className="capitalize">{item.owner.trust_level || 'New'} Member</span>
                            {item.owner.member_since && (
                              <span>• Since {new Date(item.owner.member_since).getFullYear()}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Daily:</span>
                        <span className="font-semibold">${item.daily_price}/day</span>
                      </div>
                      {item.weekly_price && (
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Weekly:</span>
                          <span className="font-semibold">${item.weekly_price}/week</span>
                        </div>
                      )}
                      {item.monthly_price && (
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Monthly:</span>
                          <span className="font-semibold">${item.monthly_price}/month</span>
                        </div>
                      )}
                      {item.capacity_spec && (
                        <div className="text-sm text-muted-foreground mt-2">
                          <strong>Specs:</strong> {item.capacity_spec}
                        </div>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button 
                      className="w-full bg-emerald-600 hover:bg-emerald-700" 
                      onClick={() => handleCreateBooking(item.id)}
                      disabled={!user}
                    >
                      {user ? 'Book Now' : 'Sign In to Book'}
                    </Button>
                  </CardFooter>
                </Card>
              )
              })}
            </div>

            {filteredEquipment.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No equipment found matching your filters.</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedCategory('all')
                    setLocationFilter('all')
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            )}
          </>
        )}

        {currentView === 'equipment' && user && (
          <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold">My Equipment</h2>
            </div>

            {/* Info Banner - No Stripe Connect Required */}
            <Card className="mb-8 border-blue-500 bg-blue-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <Zap className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">List for Free, Boost When You Want</h3>
                    <p className="text-sm text-slate-600 mb-2">
                      Create unlimited listings at no cost. No transaction fees, no subscriptions. 
                      Want more visibility? Boost your listing to the top for just $2.99!
                    </p>
                    <Button 
                      onClick={() => setCurrentView('pricing')}
                      variant="outline"
                      className="border-blue-600 text-blue-600 hover:bg-blue-100"
                    >
                      View Boost Options
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Create Equipment Form - Always show (no Stripe required) */}
            {true ? (
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle>List New Equipment</CardTitle>
                  <CardDescription>Add equipment to rent out to others</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreateEquipment} className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="name">Equipment Name</Label>
                      <Input
                        id="name"
                        value={equipmentForm.name}
                        onChange={(e) => setEquipmentForm({...equipmentForm, name: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Category</Label>
                      <select
                        id="category"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={equipmentForm.category}
                        onChange={(e) => setEquipmentForm({...equipmentForm, category: e.target.value})}
                      >
                        <option value="bikes">Bikes & Racks</option>
                        <option value="water">Water Sports</option>
                        <option value="camping">Camping</option>
                        <option value="power">Power & Solar</option>
                        <option value="gear">Gear & Accessories</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={equipmentForm.description}
                      onChange={(e) => setEquipmentForm({...equipmentForm, description: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="location">Location (City, State)</Label>
                    <Input
                      id="location"
                      placeholder="e.g., San Diego, CA"
                      value={equipmentForm.location}
                      onChange={(e) => setEquipmentForm({...equipmentForm, location: e.target.value})}
                      required
                    />
                  </div>
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="daily_price">Daily Price ($)</Label>
                      <Input
                        id="daily_price"
                        type="number"
                        step="0.01"
                        value={equipmentForm.daily_price}
                        onChange={(e) => setEquipmentForm({...equipmentForm, daily_price: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="weekly_price">Weekly Price ($)</Label>
                      <Input
                        id="weekly_price"
                        type="number"
                        step="0.01"
                        value={equipmentForm.weekly_price}
                        onChange={(e) => setEquipmentForm({...equipmentForm, weekly_price: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="monthly_price">Monthly Price ($)</Label>
                      <Input
                        id="monthly_price"
                        type="number"
                        step="0.01"
                        value={equipmentForm.monthly_price}
                        onChange={(e) => setEquipmentForm({...equipmentForm, monthly_price: e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="security_deposit">Refundable Security Deposit ($)</Label>
                    <Input
                      id="security_deposit"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={equipmentForm.security_deposit || ''}
                      onChange={(e) => setEquipmentForm({...equipmentForm, security_deposit: e.target.value})}
                    />
                    <p className="text-sm text-gray-500 mt-1">Optional: Amount renters must pay as a refundable deposit</p>
                  </div>
                  <div>
                    <Label htmlFor="capacity_spec">Specifications</Label>
                    <Input
                      id="capacity_spec"
                      placeholder="e.g., 1000Wh capacity, 2000W output"
                      value={equipmentForm.capacity_spec}
                      onChange={(e) => setEquipmentForm({...equipmentForm, capacity_spec: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="equipment_images">Equipment Photos (Up to 5) *</Label>
                    <div className="mt-2">
                      <Input
                        id="equipment_images"
                        type="file"
                        accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                        multiple
                        onChange={handleImageSelect}
                        className="cursor-pointer"
                        required={imagePreviewUrls.length === 0}
                      />
                      <p className="text-sm text-slate-500 mt-1">Max 5 images, 5MB each (PNG, JPG, GIF, WEBP)</p>
                    </div>
                    
                    {/* Image Previews */}
                    {imagePreviewUrls.length > 0 && (
                      <div className="mt-4 grid grid-cols-5 gap-2">
                        {imagePreviewUrls.map((url, index) => (
                          <div key={index} className="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-200">
                            <img src={url} alt={`Preview ${index + 1}`} className="w-full h-full object-cover" />
                            <button
                              type="button"
                              onClick={() => handleRemoveImage(index)}
                              className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                            >
                              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    <Plus className="h-4 w-4 mr-2" />
                    {loading ? 'Creating...' : 'List Equipment'}
                  </Button>
                </form>
              </CardContent>
            </Card>
            ) : null}

            {/* My Equipment List */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Your Listed Equipment</h3>
              {myEquipment.map((item) => (
                <Card key={item.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{item.name}</CardTitle>
                        <CardDescription>{item.description}</CardDescription>
                        {item.location && (
                          <p className="text-sm text-muted-foreground mt-2">📍 {item.location}</p>
                        )}
                        <div className="mt-2 space-y-1">
                          <p className="text-sm">
                            <strong>Daily:</strong> ${item.daily_price}
                            {item.weekly_price && <> | <strong>Weekly:</strong> ${item.weekly_price}</>}
                            {item.monthly_price && <> | <strong>Monthly:</strong> ${item.monthly_price}</>}
                          </p>
                          {item.capacity_spec && (
                            <p className="text-sm"><strong>Specs:</strong> {item.capacity_spec}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleEditEquipment(item)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleDeleteEquipment(item.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}
              {myEquipment.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No equipment listed yet. Create your first listing above!
                </p>
              )}
            </div>
          </div>
        )}

        {/* Edit Equipment Dialog */}
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogContent className="sm:max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Equipment</DialogTitle>
              <DialogDescription>Update your equipment details</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleUpdateEquipment} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-name">Equipment Name</Label>
                  <Input
                    id="edit-name"
                    value={equipmentForm.name}
                    onChange={(e) => setEquipmentForm({...equipmentForm, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="edit-category">Category</Label>
                  <select
                    id="edit-category"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    value={equipmentForm.category}
                    onChange={(e) => setEquipmentForm({...equipmentForm, category: e.target.value})}
                  >
                    <option value="bikes">Bikes & Racks</option>
                    <option value="water">Water Sports</option>
                    <option value="camping">Camping</option>
                    <option value="power">Power & Solar</option>
                    <option value="gear">Gear & Accessories</option>
                  </select>
                </div>
              </div>
              <div>
                <Label htmlFor="edit-description">Description</Label>
                <Input
                  id="edit-description"
                  value={equipmentForm.description}
                  onChange={(e) => setEquipmentForm({...equipmentForm, description: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="edit-location">Location (City, State)</Label>
                <Input
                  id="edit-location"
                  placeholder="e.g., San Diego, CA"
                  value={equipmentForm.location}
                  onChange={(e) => setEquipmentForm({...equipmentForm, location: e.target.value})}
                  required
                />
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="edit-daily_price">Daily Price ($)</Label>
                  <Input
                    id="edit-daily_price"
                    type="number"
                    step="0.01"
                    value={equipmentForm.daily_price}
                    onChange={(e) => setEquipmentForm({...equipmentForm, daily_price: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="edit-weekly_price">Weekly Price ($)</Label>
                  <Input
                    id="edit-weekly_price"
                    type="number"
                    step="0.01"
                    value={equipmentForm.weekly_price}
                    onChange={(e) => setEquipmentForm({...equipmentForm, weekly_price: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="edit-monthly_price">Monthly Price ($)</Label>
                  <Input
                    id="edit-monthly_price"
                    type="number"
                    step="0.01"
                    value={equipmentForm.monthly_price}
                    onChange={(e) => setEquipmentForm({...equipmentForm, monthly_price: e.target.value})}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="edit-security_deposit">Refundable Security Deposit ($)</Label>
                <Input
                  id="edit-security_deposit"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={equipmentForm.security_deposit || ''}
                  onChange={(e) => setEquipmentForm({...equipmentForm, security_deposit: e.target.value})}
                />
                <p className="text-sm text-gray-500 mt-1">Optional: Amount renters must pay as a refundable deposit</p>
              </div>
              <div>
                <Label htmlFor="edit-capacity_spec">Specifications</Label>
                <Input
                  id="edit-capacity_spec"
                  placeholder="e.g., 1000Wh capacity, 2000W output"
                  value={equipmentForm.capacity_spec}
                  onChange={(e) => setEquipmentForm({...equipmentForm, capacity_spec: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="edit-equipment_images">Equipment Photos (Up to 5)</Label>
                <div className="mt-2">
                  <Input
                    id="edit-equipment_images"
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                    multiple
                    onChange={handleImageSelect}
                    className="cursor-pointer"
                  />
                  <p className="text-sm text-slate-500 mt-1">Max 5 images, 5MB each (PNG, JPG, GIF, WEBP)</p>
                </div>
                
                {/* Image Previews */}
                {imagePreviewUrls.length > 0 && (
                  <div className="mt-4 grid grid-cols-5 gap-2">
                    {imagePreviewUrls.map((url, index) => (
                      <div key={index} className="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-200">
                        <img src={url} alt={`Preview ${index + 1}`} className="w-full h-full object-cover" />
                        <button
                          type="button"
                          onClick={() => handleRemoveImage(index)}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Show current images if no new images selected */}
                {imagePreviewUrls.length === 0 && editingEquipment?.image_urls && editingEquipment.image_urls.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-slate-600 mb-2">Current images:</p>
                    <div className="grid grid-cols-5 gap-2">
                      {editingEquipment.image_urls.map((url, index) => (
                        <div key={index} className="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-200">
                          <img src={url} alt={`Current ${index + 1}`} className="w-full h-full object-cover" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button type="submit" className="flex-1" disabled={loading}>
                  {loading ? 'Updating...' : 'Update Equipment'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowEditDialog(false)
                    setEditingEquipment(null)
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>

        {currentView === 'bookings' && user && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-8">My Bookings</h2>
            <div className="space-y-4">
              {myBookings.map((booking) => (
                <Card key={booking.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{booking.equipment?.name}</CardTitle>
                        <CardDescription>
                          {booking.start_date} to {booking.end_date} ({booking.total_days} days)
                        </CardDescription>
                        <div className="mt-2 space-y-1">
                          <p className="text-sm">
                            <strong>Total Cost:</strong> ${booking.total_cost.toFixed(2)}
                          </p>
                          <p className="text-sm">
                            <strong>Deposit:</strong> ${booking.deposit_amount.toFixed(2)} (50%)
                          </p>
                          <Badge className={
                            booking.status === 'completed' ? 'bg-green-600' :
                            booking.status === 'active' ? 'bg-blue-600' :
                            booking.status === 'confirmed' ? 'bg-emerald-600' :
                            booking.status === 'cancelled' ? 'bg-red-600' :
                            'bg-yellow-600'
                          }>
                            {booking.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardFooter className="flex gap-2 flex-wrap">
                    {booking.status === 'completed' && !booking.has_review && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => {
                          setReviewingBooking(booking);
                          setShowReviewDialog(true);
                        }}
                      >
                        <Star className="h-4 w-4 mr-2" />
                        Leave Review
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`/api/contracts/rental-agreement/${booking.id}`, '_blank')}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Rental Agreement
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`/api/contracts/liability-waiver/${booking.id}`, '_blank')}
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      Liability Waiver
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`/api/contracts/all/${booking.id}`, '_blank')}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download All
                    </Button>
                  </CardFooter>
                </Card>
              ))}
              {myBookings.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No bookings yet. Browse equipment to make your first booking!
                </p>
              )}
            </div>
          </div>
        )}

        {currentView === 'messages' && user && (
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold mb-8">Messages</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {/* Conversations List */}
              <div className="md:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle>Conversations</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    {conversations.length === 0 ? (
                      <p className="text-center text-muted-foreground py-8 px-4">No messages yet</p>
                    ) : (
                      <div className="divide-y">
                        {conversations.map((conv) => (
                          <button
                            key={`${conv.equipment_id}_${conv.partner_id}`}
                            onClick={() => {
                              setSelectedConversation(conv);
                              loadConversationMessages(conv.equipment_id);
                            }}
                            className={`w-full text-left p-4 hover:bg-slate-50 transition-colors ${
                              selectedConversation?.equipment_id === conv.equipment_id && selectedConversation?.partner_id === conv.partner_id
                                ? 'bg-emerald-50'
                                : ''
                            }`}
                          >
                            <div className="flex justify-between items-start mb-1">
                              <p className="font-semibold text-sm">{conv.partner_name}</p>
                              {conv.unread_count > 0 && (
                                <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                  {conv.unread_count}
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground mb-1">{conv.equipment_name}</p>
                            <p className="text-xs text-muted-foreground truncate">{conv.last_message}</p>
                          </button>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Message Thread */}
              <div className="md:col-span-2">
                <Card className="h-[600px] flex flex-col">
                  {selectedConversation ? (
                    <>
                      <CardHeader>
                        <CardTitle>{selectedConversation.partner_name}</CardTitle>
                        <CardDescription>About: {selectedConversation.equipment_name}</CardDescription>
                      </CardHeader>
                      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                        {conversationMessages.map((msg) => (
                          <div
                            key={msg.id}
                            className={`flex ${
                              msg.sender_id === user.id ? 'justify-end' : 'justify-start'
                            }`}
                          >
                            <div
                              className={`max-w-[70%] rounded-lg p-3 ${
                                msg.sender_id === user.id
                                  ? 'bg-emerald-600 text-white'
                                  : 'bg-slate-100 text-slate-900'
                              }`}
                            >
                              <p className="text-sm">{msg.message}</p>
                              <p className="text-xs mt-1 opacity-70">
                                {new Date(msg.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        ))}
                      </CardContent>
                      <CardFooter>
                        <form onSubmit={handleSendMessage} className="flex w-full gap-2">
                          <Input
                            placeholder="Type your message..."
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            disabled={loading}
                          />
                          <Button type="submit" disabled={loading || !newMessage.trim()}>
                            <Send className="h-4 w-4" />
                          </Button>
                        </form>
                      </CardFooter>
                    </>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-muted-foreground">Select a conversation to start messaging</p>
                    </div>
                  )}
                </Card>
              </div>
            </div>
          </div>
        )}

        {currentView === 'profile' && user && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-8">Profile Settings</h2>
            
            {/* Profile Information Card */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your personal information and profile details</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpdateProfile} className="space-y-6">
                  {/* Profile Photo Section */}
                  <div className="flex items-center gap-6 pb-6 border-b">
                    <div className="w-24 h-24 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden">
                      {profileForm.profile_image_url ? (
                        <img src={profileForm.profile_image_url} alt="Profile" className="w-full h-full object-cover" />
                      ) : (
                        <User className="h-12 w-12 text-slate-400" />
                      )}
                    </div>
                    <div className="flex-1">
                      <Label htmlFor="profile_image">Profile Photo</Label>
                      <div className="mt-2">
                        <Input
                          id="profile_image"
                          type="file"
                          accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                          onChange={handleProfileImageSelect}
                          className="cursor-pointer"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Max 5MB (PNG, JPG, GIF, WEBP)</p>
                        {profileImagePreview && (
                          <div className="mt-3">
                            <p className="text-sm font-medium mb-2">New Photo Preview:</p>
                            <div className="w-32 h-32 rounded-full overflow-hidden border-2 border-emerald-500">
                              <img src={profileImagePreview} alt="Preview" className="w-full h-full object-cover" />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Basic Information */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Basic Information</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="profile-first_name">First Name</Label>
                        <Input
                          id="profile-first_name"
                          value={profileForm.first_name}
                          onChange={(e) => setProfileForm({...profileForm, first_name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="profile-last_name">Last Name</Label>
                        <Input
                          id="profile-last_name"
                          value={profileForm.last_name}
                          onChange={(e) => setProfileForm({...profileForm, last_name: e.target.value})}
                          required
                        />
                      </div>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="profile-email">Email</Label>
                        <Input
                          id="profile-email"
                          type="email"
                          value={profileForm.email}
                          disabled
                          className="bg-slate-100"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
                      </div>
                      <div>
                        <Label htmlFor="profile-phone">Phone Number</Label>
                        <Input
                          id="profile-phone"
                          type="tel"
                          placeholder="(555) 123-4567"
                          value={profileForm.phone}
                          onChange={(e) => setProfileForm({...profileForm, phone: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Bio Section */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">About You</h3>
                    <div>
                      <Label htmlFor="profile-bio">Bio</Label>
                      <Textarea
                        id="profile-bio"
                        placeholder="Tell others about yourself, your outdoor interests, and what equipment you have..."
                        value={profileForm.bio}
                        onChange={(e) => setProfileForm({...profileForm, bio: e.target.value})}
                        rows={4}
                        className="resize-none"
                      />
                      <p className="text-xs text-muted-foreground mt-1">This will be visible on your public profile</p>
                    </div>
                  </div>

                  {/* Address Section */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Address</h3>
                    <div>
                      <Label htmlFor="profile-address">Street Address</Label>
                      <Input
                        id="profile-address"
                        placeholder="123 Main St"
                        value={profileForm.address}
                        onChange={(e) => setProfileForm({...profileForm, address: e.target.value})}
                      />
                    </div>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="md:col-span-1">
                        <Label htmlFor="profile-city">City</Label>
                        <Input
                          id="profile-city"
                          placeholder="San Diego"
                          value={profileForm.city}
                          onChange={(e) => setProfileForm({...profileForm, city: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label htmlFor="profile-state">State</Label>
                        <Input
                          id="profile-state"
                          placeholder="CA"
                          value={profileForm.state}
                          onChange={(e) => setProfileForm({...profileForm, state: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label htmlFor="profile-zip_code">ZIP Code</Label>
                        <Input
                          id="profile-zip_code"
                          placeholder="92101"
                          value={profileForm.zip_code}
                          onChange={(e) => setProfileForm({...profileForm, zip_code: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Saving...' : 'Save Profile Changes'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Identity Verification Card */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Identity Verification</CardTitle>
                <CardDescription>
                  {user.is_identity_verified 
                    ? 'Your identity has been verified'
                    : 'Verify your identity to build trust and unlock premium features'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {user.is_identity_verified ? (
                  <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
                    <Shield className="h-6 w-6 text-emerald-600" />
                    <div>
                      <p className="font-semibold text-emerald-900">Identity Verified</p>
                      <p className="text-sm text-emerald-700">Your identity has been confirmed</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-900 font-semibold mb-2">Why verify your identity?</p>
                      <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                        <li>Build trust with equipment owners</li>
                        <li>Required for high-value rentals ($500+)</li>
                        <li>Get priority in booking requests</li>
                        <li>Unlock verified badge on your profile</li>
                      </ul>
                    </div>
                    <Button 
                      onClick={handleStartVerification}
                      disabled={loading}
                      className="w-full"
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      {loading ? 'Starting Verification...' : 'Verify My Identity'}
                    </Button>
                    <p className="text-xs text-muted-foreground text-center">
                      Powered by Stripe Identity • Secure & Private • Takes 2-3 minutes
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Account Management Card */}
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-red-600">Danger Zone</CardTitle>
                <CardDescription>Irreversible account actions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-4 p-4 bg-red-50 rounded-lg border border-red-200">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-red-900">Delete Account</h4>
                      <p className="text-sm text-red-700 mt-1">
                        Once you delete your account, there is no going back. This will permanently delete all your equipment listings, bookings, and personal information.
                      </p>
                      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
                        <DialogTrigger asChild>
                          <Button variant="destructive" className="mt-4">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete My Account
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Are you absolutely sure?</DialogTitle>
                            <DialogDescription>
                              This action cannot be undone. This will permanently delete your account and remove all your data from our servers.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                              <p className="text-sm text-red-900 font-semibold">This will delete:</p>
                              <ul className="text-sm text-red-700 mt-2 space-y-1 list-disc list-inside">
                                <li>Your profile and personal information</li>
                                <li>All your equipment listings</li>
                                <li>All your booking history</li>
                                <li>All associated data</li>
                              </ul>
                            </div>
                            <div className="flex gap-2">
                              <Button 
                                variant="destructive" 
                                className="flex-1"
                                onClick={handleDeleteAccount}
                                disabled={loading}
                              >
                                {loading ? 'Deleting...' : 'Yes, Delete My Account'}
                              </Button>
                              <Button 
                                variant="outline" 
                                className="flex-1"
                                onClick={() => setShowDeleteConfirm(false)}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'about' && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">About The Wild Share</h2>
            
            <div className="prose prose-lg max-w-none space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Our Story</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p>
                    The Wild Share was born from a simple idea: outdoor adventures shouldn't be limited by the cost of equipment. Whether you're a seasoned adventurer or just starting to explore the great outdoors, everyone deserves access to quality gear.
                  </p>
                  <p>
                    We created a community-driven platform where outdoor enthusiasts can share their equipment with others, making adventures more accessible and affordable for everyone. From bikes and camping gear to water sports equipment and power solutions, The Wild Share connects people who have gear with those who need it.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Our Mission</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p>
                    We believe in the power of sharing. By enabling people to rent equipment from their neighbors and local community members, we're not just making outdoor activities more affordable—we're building connections, reducing waste, and encouraging more people to get outside and explore.
                  </p>
                  <p>
                    Our mission is to make outdoor adventures accessible to everyone while promoting sustainable consumption and community building.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How It Works</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-lg mb-2">For Renters</h4>
                      <p>Browse available equipment, book what you need, and enjoy your adventure. Return the gear in the same condition, and your deposit is refunded.</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-lg mb-2">For Owners</h4>
                      <p>List your equipment, set your prices, and earn money from gear that would otherwise sit unused. We handle the bookings and payments securely.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Our Values</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    <li><strong>Community:</strong> Building connections between outdoor enthusiasts</li>
                    <li><strong>Accessibility:</strong> Making outdoor adventures available to everyone</li>
                    <li><strong>Sustainability:</strong> Promoting equipment sharing to reduce waste</li>
                    <li><strong>Trust:</strong> Creating a safe and reliable platform for both renters and owners</li>
                    <li><strong>Adventure:</strong> Encouraging people to explore and experience the outdoors</li>
                  </ul>
                </CardContent>
              </Card>

              <div className="text-center mt-8">
                <Button size="lg" onClick={() => setCurrentView('browse')} className="bg-emerald-600 hover:bg-emerald-700">
                  Start Browsing Equipment
                </Button>
              </div>
            </div>
          </div>
        )}

        {currentView === 'contact' && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">Contact Us</h2>
            
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold mb-4">Get in Touch</h3>
                    <p className="text-muted-foreground mb-4">
                      Have questions, feedback, or need help? We'd love to hear from you!
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label className="text-lg">Email</Label>
                      <p className="mt-2">
                        <a href="mailto:thewildshare@gmail.com" className="text-emerald-600 hover:text-emerald-700 text-lg">
                          thewildshare@gmail.com
                        </a>
                      </p>
                    </div>

                    <div className="pt-4 border-t">
                      <h4 className="font-semibold mb-2">Response Time</h4>
                      <p className="text-muted-foreground">
                        We typically respond within 24-48 hours during business days.
                      </p>
                    </div>

                    <div className="pt-4 border-t">
                      <h4 className="font-semibold mb-2">For Urgent Issues</h4>
                      <p className="text-muted-foreground">
                        If you have an urgent issue with an active rental, please include your booking ID in your email subject line.
                      </p>
                    </div>
                  </div>

                  <div className="text-center pt-6">
                    <Button onClick={() => setCurrentView('browse')} variant="outline">
                      Back to Browse
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'terms' && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">Rental Terms & Conditions</h2>
            
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Agreement Overview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p>
                    By using The Wild Share platform and booking equipment, you agree to the following terms and conditions. Please read carefully before proceeding with any rental.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>1. Renter Responsibilities</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h4 className="font-semibold">Liability</h4>
                    <p className="text-muted-foreground">The renter assumes ALL responsibility for the equipment during the rental period. This includes any damage, loss, theft, or accidents involving the equipment.</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Proper Use</h4>
                    <p className="text-muted-foreground">Equipment must be used only for its intended purpose and in accordance with all safety guidelines and manufacturer instructions.</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Care and Maintenance</h4>
                    <p className="text-muted-foreground">Renters must take reasonable care of the equipment and protect it from damage, theft, and misuse.</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>2. Damage and Loss</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p>The renter is responsible for:</p>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Any damage to the equipment beyond normal wear and tear</li>
                    <li>Full replacement cost if equipment is lost or stolen</li>
                    <li>Repair costs for damaged equipment</li>
                    <li>Any costs incurred due to improper use or negligence</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>3. Security Deposit</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h4 className="font-semibold">Deposit Amount</h4>
                    <p className="text-muted-foreground">Equipment owners may require a refundable security deposit at the time of booking. The deposit amount is set by the owner and shown on the equipment listing.</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Refund Policy</h4>
                    <p className="text-muted-foreground">The deposit will be refunded in full upon safe return of the equipment in its original condition (normal wear and tear excepted).</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Deductions</h4>
                    <p className="text-muted-foreground">Deposits may be partially or fully retained to cover damage, cleaning fees, late returns, or other violations of these terms.</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>4. Insurance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    The renter is responsible for obtaining appropriate insurance coverage if desired. The Wild Share and equipment owners do not provide insurance coverage for rented equipment.
                  </p>
                  <p className="text-muted-foreground">
                    We strongly recommend renters verify their personal insurance policies or obtain rental insurance to cover potential damages, loss, or liability.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>5. Rental Period and Returns</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <h4 className="font-semibold">On-Time Returns</h4>
                    <p className="text-muted-foreground">Equipment must be returned on time and in the same condition as received. Late returns may incur additional fees.</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Inspection</h4>
                    <p className="text-muted-foreground">Equipment will be inspected upon return. Any damage or issues will be documented and may result in charges.</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Cleaning</h4>
                    <p className="text-muted-foreground">Equipment should be returned clean and ready for the next renter. Excessive cleaning fees may apply.</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>6. Cancellation Policy</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Cancellations more than 48 hours before rental start: Full refund</li>
                    <li>Cancellations 24-48 hours before rental start: 50% refund</li>
                    <li>Cancellations less than 24 hours before rental start: No refund</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>7. Safety and Compliance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    Renters must comply with all applicable laws, regulations, and safety requirements when using rented equipment. This includes but is not limited to:
                  </p>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Wearing appropriate safety gear</li>
                    <li>Following manufacturer guidelines</li>
                    <li>Obtaining necessary permits or licenses</li>
                    <li>Respecting property rights and environmental regulations</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>8. Limitation of Liability</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    The Wild Share acts as a platform connecting equipment owners with renters. We are not responsible for:
                  </p>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>Equipment condition, quality, or suitability</li>
                    <li>Injuries or accidents resulting from equipment use</li>
                    <li>Disputes between renters and owners</li>
                    <li>Loss or damage to personal property</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>9. Dispute Resolution</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    In case of disputes regarding equipment condition, damage, or other rental issues, both parties agree to:
                  </p>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li>First attempt to resolve the issue directly</li>
                    <li>Contact The Wild Share support for mediation if needed</li>
                    <li>Provide documentation (photos, receipts, etc.) to support claims</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>10. Acceptance of Terms</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    By proceeding with a booking, you acknowledge that you have read, understood, and agree to be bound by these rental terms and conditions.
                  </p>
                </CardContent>
              </Card>

              <div className="text-center mt-8">
                <Button onClick={() => setCurrentView('browse')} variant="outline">
                  Back to Browse
                </Button>
              </div>
            </div>
          </div>
        )}

        {currentView === 'faq' && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">Frequently Asked Questions</h2>
            
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>How does The Wild Share work?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    The Wild Share is a peer-to-peer rental platform. Equipment owners list their gear, set prices, and make it available for rent. Renters browse available equipment, book what they need, and return it after use. We handle secure payments and provide a platform for the community to connect.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How do I rent equipment?</CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="list-decimal pl-6 space-y-2 text-muted-foreground">
                    <li>Create an account or sign in</li>
                    <li>Browse available equipment using search and filters</li>
                    <li>Click "Book Now" on the equipment you want</li>
                    <li>Review and accept the rental agreement</li>
                    <li>Enter your rental dates</li>
                    <li>Complete payment (rental cost + owner's security deposit if required)</li>
                    <li>Coordinate pickup with the owner</li>
                    <li>Enjoy your adventure!</li>
                    <li>Return equipment on time in good condition</li>
                    <li>Get your deposit refunded</li>
                  </ol>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How do I list my equipment?</CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="list-decimal pl-6 space-y-2 text-muted-foreground">
                    <li>Create an account as an owner or "both" (renter and owner)</li>
                    <li>Go to "My Equipment" in the navigation</li>
                    <li>Click "Add Equipment"</li>
                    <li>Fill in details: name, description, category, prices, location, photos</li>
                    <li>Submit your listing</li>
                    <li>Your equipment will appear in browse results</li>
                    <li>Manage bookings through "My Equipment"</li>
                  </ol>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What is the security deposit?</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    Equipment owners may require a refundable security deposit when booking their equipment. The deposit amount is set by each owner and displayed on their listing. This protects owners against damage or loss.
                  </p>
                  <p className="text-muted-foreground">
                    The deposit is fully refunded when you return the equipment in good condition (normal wear and tear is expected). Refunds are typically processed within 2-3 business days after equipment return and inspection.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What if the equipment gets damaged?</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-muted-foreground">
                    Renters are responsible for any damage beyond normal wear and tear. Minor damage may result in partial deposit retention to cover repairs. Major damage or loss may require full replacement cost.
                  </p>
                  <p className="text-muted-foreground">
                    We recommend taking photos of the equipment before and after use, and communicating openly with the owner about any issues.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Is insurance included?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    No, insurance is not included. Renters are responsible for obtaining their own insurance coverage if desired. We recommend checking your personal insurance policies (homeowners, renters, auto) to see if they cover rental equipment. You may also want to purchase separate rental insurance.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How are payments processed?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    All payments are processed securely through Stripe. When you book equipment, you pay the rental cost plus any security deposit required by the owner. The rental payment goes to the equipment owner, and the deposit (if required) is held until the equipment is returned in good condition.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What is the cancellation policy?</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li><strong>More than 48 hours before rental:</strong> Full refund</li>
                    <li><strong>24-48 hours before rental:</strong> 50% refund</li>
                    <li><strong>Less than 24 hours before rental:</strong> No refund</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How do I coordinate pickup and return?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    After booking, you'll receive the owner's contact information. Coordinate directly with them to arrange pickup location, time, and any special instructions. The same applies for returns. We recommend being flexible and communicating clearly.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What categories of equipment are available?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-3">We have five main categories:</p>
                  <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                    <li><strong>Bikes & Racks:</strong> Bikes, bike racks, roof rack luggage carriers</li>
                    <li><strong>Water Sports:</strong> Paddleboards, kayaks, inflatable rafts</li>
                    <li><strong>Camping:</strong> Tents, sleeping pads, chairs, coolers, EZ ups</li>
                    <li><strong>Power & Solar:</strong> Solar panels, diesel heaters, power stations</li>
                    <li><strong>Gear & Accessories:</strong> Backpacks, hiking gear, and more</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Can I rent equipment for multiple days?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Yes! Most equipment is available for daily, weekly, or monthly rentals. Longer rentals often come with discounted rates. Check the equipment listing for available pricing options.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What if I need to return equipment late?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Contact the owner as soon as possible if you need to extend your rental. Late returns without prior approval may result in additional fees and could affect your deposit refund. Communication is key!
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How do I search for specific equipment?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Use the search bar on the Browse page to search by equipment name, description, or location. You can also filter by category and location using the dropdown menus. All three filters work together to help you find exactly what you need.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Can I message the owner before booking?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Currently, you'll receive owner contact information after booking. We recommend asking any questions during the pickup coordination. A messaging system is planned for future updates.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>How do I earn money as an equipment owner?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    List your equipment with competitive pricing, provide accurate descriptions and good photos, keep your calendar updated, respond promptly to bookings, and maintain your equipment in good condition. The more professional and reliable you are, the more bookings you'll receive!
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>What if I have a dispute with a renter or owner?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    First, try to resolve the issue directly through respectful communication. If that doesn't work, contact us at thewildshare@gmail.com with details and documentation (photos, messages, receipts). We'll help mediate and find a fair resolution.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Is my personal information safe?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Yes. We use industry-standard security measures to protect your data. Payment information is processed through Stripe and never stored on our servers. Your contact information is only shared with users you're actively transacting with.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Still have questions?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Contact us at <a href="mailto:thewildshare@gmail.com" className="text-emerald-600 hover:text-emerald-700">thewildshare@gmail.com</a> and we'll be happy to help!
                  </p>
                </CardContent>
              </Card>

              <div className="text-center mt-8">
                <Button onClick={() => setCurrentView('browse')} variant="outline">
                  Back to Browse
                </Button>
              </div>
            </div>
          </div>
        )}

        {currentView === 'pricing' && (
          <PricingPage 
            user={user} 
            onViewChange={setCurrentView}
            onBoostClick={(boostType) => {
              setSelectedBoostType(boostType)
              setShowBoostModal(true)
            }}
          />
        )}

        {currentView === 'terms-of-service' && (
          <TermsOfServiceView setCurrentView={setCurrentView} />
        )}

        {currentView === 'privacy-policy' && (
          <PrivacyPolicyView setCurrentView={setCurrentView} />
        )}
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Mountain className="h-6 w-6" />
                <span className="text-xl font-bold">The Wild Share</span>
              </div>
              <p className="text-slate-400">
                Share the adventure. Rent premium outdoor gear or list your equipment.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Equipment</h4>
              <ul className="space-y-2 text-slate-400">
                <li>Power Solutions</li>
                <li>Connectivity</li>
                <li>Recreation Gear</li>
                <li>Camping Equipment</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400">
                <li><button onClick={() => setCurrentView('about')} className="hover:text-white transition-colors">About Us</button></li>
                <li><button onClick={() => setCurrentView('contact')} className="hover:text-white transition-colors">Contact</button></li>
                <li><button onClick={() => setCurrentView('terms')} className="hover:text-white transition-colors">Rental Terms</button></li>
                <li><button onClick={() => setCurrentView('faq')} className="hover:text-white transition-colors">FAQ</button></li>
                <li><button onClick={() => setCurrentView('terms-of-service')} className="hover:text-white transition-colors">Terms of Service</button></li>
                <li><button onClick={() => setCurrentView('privacy-policy')} className="hover:text-white transition-colors">Privacy Policy</button></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="mailto:thewildshare@gmail.com" className="hover:text-white transition-colors">thewildshare@gmail.com</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 The Wild Share. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Booking Dialog */}
      <Dialog open={showBookingDialog} onOpenChange={setShowBookingDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Book {selectedEquipment?.name}</DialogTitle>
            <DialogDescription>
              Select your rental dates
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmitBooking} className="space-y-4">
            <div>
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={bookingForm.start_date}
                onChange={(e) => setBookingForm({...bookingForm, start_date: e.target.value})}
                required
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div>
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={bookingForm.end_date}
                onChange={(e) => setBookingForm({...bookingForm, end_date: e.target.value})}
                required
                min={bookingForm.start_date || new Date().toISOString().split('T')[0]}
              />
            </div>
            {selectedEquipment && (
              <div className="bg-muted p-4 rounded-lg space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Daily Rate:</span>
                  <span className="font-medium">${selectedEquipment.daily_price}/day</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Total cost will be calculated based on rental duration + 50% security deposit
                </div>
              </div>
            )}
            <div className="flex gap-3">
              <Button type="button" variant="outline" onClick={() => setShowBookingDialog(false)} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" disabled={loading} className="flex-1">
                {loading ? 'Creating...' : 'Continue to Payment'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Checkout Dialog */}
      {/* Review Dialog */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Leave a Review</DialogTitle>
            <DialogDescription>
              Share your experience with this equipment and owner
            </DialogDescription>
          </DialogHeader>
          {reviewingBooking && (
            <form onSubmit={handleSubmitReview} className="space-y-6">
              {/* Equipment Rating */}
              <div>
                <Label>Equipment Rating</Label>
                <div className="flex items-center gap-2 mt-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      onClick={() => setReviewForm({...reviewForm, equipment_rating: rating})}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`h-8 w-8 ${
                          rating <= reviewForm.equipment_rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                  <span className="ml-2 text-sm text-muted-foreground">
                    {reviewForm.equipment_rating} / 5
                  </span>
                </div>
              </div>

              {/* Equipment Review Text */}
              <div>
                <Label htmlFor="equipment_review">Equipment Review (Optional)</Label>
                <Textarea
                  id="equipment_review"
                  placeholder="Tell others about the equipment condition, quality, etc."
                  value={reviewForm.equipment_review}
                  onChange={(e) => setReviewForm({...reviewForm, equipment_review: e.target.value})}
                  rows={3}
                />
              </div>

              {/* Owner Rating */}
              <div>
                <Label>Owner Rating</Label>
                <div className="flex items-center gap-2 mt-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      onClick={() => setReviewForm({...reviewForm, owner_rating: rating})}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`h-8 w-8 ${
                          rating <= reviewForm.owner_rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                  <span className="ml-2 text-sm text-muted-foreground">
                    {reviewForm.owner_rating} / 5
                  </span>
                </div>
              </div>

              {/* Owner Review Text */}
              <div>
                <Label htmlFor="owner_review">Owner Review (Optional)</Label>
                <Textarea
                  id="owner_review"
                  placeholder="Tell others about your experience with the owner (communication, pickup, etc.)"
                  value={reviewForm.owner_review}
                  onChange={(e) => setReviewForm({...reviewForm, owner_review: e.target.value})}
                  rows={3}
                />
              </div>

              {/* Submit Button */}
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setShowReviewDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? 'Submitting...' : 'Submit Review'}
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={showCheckout} onOpenChange={setShowCheckout}>
        <DialogContent className="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>Complete Payment</DialogTitle>
          </DialogHeader>
          {currentBooking && selectedEquipment && (
            <StripeCheckout
              booking={currentBooking}
              equipment={selectedEquipment}
              onSuccess={handlePaymentSuccess}
              onCancel={handleCancelCheckout}
            />
          )}
        </DialogContent>
      </Dialog>

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

    </div>
  )
}

export default App
