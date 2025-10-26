import axios from 'axios';

// Use relative path for API calls - works in both dev and production
const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
  deleteAccount: () => api.delete('/auth/delete-account'),
  requestPasswordReset: (data) => api.post('/auth/request-password-reset', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};

// Equipment API
export const equipmentAPI = {
  getAll: (category) => api.get('/equipment', { params: { category } }),
  getById: (id) => api.get(`/equipment/${id}`),
  create: (data) => api.post('/equipment', data),
  update: (id, data) => api.put(`/equipment/${id}`, data),
  delete: (id) => api.delete(`/equipment/${id}`),
  getMyEquipment: () => api.get('/my-equipment'),
};

// Bookings API
export const bookingsAPI = {
  create: (data) => api.post('/bookings', data),
  getById: (id) => api.get(`/bookings/${id}`),
  getMyBookings: () => api.get('/my-bookings'),
  getEquipmentBookings: (equipmentId) => api.get(`/equipment/${equipmentId}/bookings`),
  updateStatus: (id, status) => api.put(`/bookings/${id}/status`, { status }),
};

// Payments API
export const paymentsAPI = {
  createPaymentIntent: (bookingId) => api.post('/create-payment-intent', { booking_id: bookingId }),
  confirmPayment: (paymentIntentId) => api.post('/confirm-payment', { payment_intent_id: paymentIntentId }),
  refundDeposit: (bookingId) => api.post('/refund-deposit', { booking_id: bookingId }),
  getBookingPayments: (bookingId) => api.get(`/bookings/${bookingId}/payments`),
};

// Messages API
export const messagesAPI = {
  sendMessage: (equipmentId, message) => api.post(`/equipment/${equipmentId}/messages`, { message }),
  getEquipmentMessages: (equipmentId) => api.get(`/equipment/${equipmentId}/messages`),
  getMyMessages: () => api.get('/messages'),
  getUnreadCount: () => api.get('/messages/unread-count'),
  markAsRead: (messageId) => api.put(`/messages/${messageId}/read`),
};

// Reviews API
export const reviewsAPI = {
  createReview: (bookingId, data) => api.post(`/bookings/${bookingId}/review`, data),
  getEquipmentReviews: (equipmentId) => api.get(`/equipment/${equipmentId}/reviews`),
  getUserReviews: (userId) => api.get(`/users/${userId}/reviews`),
  getMyReviews: () => api.get('/my-reviews'),
  canReview: (bookingId) => api.get(`/bookings/${bookingId}/can-review`),
};

// Identity Verification API
export const identityAPI = {
  createVerificationSession: () => api.post('/identity/create-verification-session'),
  getVerificationStatus: () => api.get('/identity/verification-status'),
};

export default api;

