# The Wild Share - Outdoor Equipment Rental Marketplace

## Platform Overview

**The Wild Share** is a full-stack marketplace platform that enables outdoor enthusiasts to rent premium equipment or list their own gear for others to rent. The platform features user authentication, equipment management, booking systems, and integrated payment processing with automatic 50% security deposits.

**Live URL:** https://g8h3ilcq7pxe.manus.space

---

## Key Features

### For Renters
- **Browse Equipment**: Search and filter outdoor gear by category (Power & Energy, Connectivity, Recreation)
- **Instant Booking**: Book equipment with automatic date validation and conflict checking
- **Secure Payments**: Integrated payment processing with Stripe
- **50% Deposit Protection**: Automatic security deposit (50% of rental cost) refunded after equipment return
- **Booking Management**: View and track all your rentals in one dashboard

### For Equipment Owners
- **List Equipment**: Create detailed equipment listings with photos, descriptions, and pricing
- **Manage Inventory**: Edit, update, or remove equipment listings
- **Track Bookings**: View all bookings for your equipment
- **Deposit Management**: Approve returns and refund deposits to renters
- **Flexible Pricing**: Set your own daily rental rates

### Platform Features
- **User Authentication**: Secure registration and login system
- **Dual Account Types**: Users can be renters, owners, or both
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Availability**: Automatic booking conflict detection
- **Professional UI**: Modern design with smooth animations and interactions

---

## Technology Stack

### Frontend
- **React 19.1.0** - Modern JavaScript framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality UI components
- **Lucide Icons** - Beautiful icon library
- **Axios** - HTTP client for API calls

### Backend
- **Flask 3.1.1** - Python web framework
- **SQLAlchemy 2.0.41** - Database ORM
- **SQLite** - Lightweight database
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **Werkzeug Security** - Password hashing
- **Stripe 13.0.1** - Payment processing integration

---

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique user email
- `password_hash` - Encrypted password
- `first_name` - User's first name
- `last_name` - User's last name
- `phone` - Contact phone number
- `user_type` - Account type (renter, owner, both)
- `created_at` - Registration timestamp

### Equipment Table
- `id` - Primary key
- `owner_id` - Foreign key to Users
- `name` - Equipment name
- `description` - Detailed description
- `category` - Equipment category (power, connectivity, recreation)
- `daily_price` - Daily rental rate
- `capacity_spec` - Capacity or specifications
- `image_url` - Product image URL
- `is_available` - Availability status
- `created_at` - Listing timestamp

### Bookings Table
- `id` - Primary key
- `equipment_id` - Foreign key to Equipment
- `renter_id` - Foreign key to Users
- `start_date` - Rental start date
- `end_date` - Rental end date
- `total_days` - Duration in days
- `daily_rate` - Rate at time of booking
- `total_cost` - Total rental cost
- `deposit_amount` - Security deposit (50% of total)
- `status` - Booking status (pending, confirmed, active, completed, cancelled)
- `created_at` - Booking timestamp

### Payments Table
- `id` - Primary key
- `booking_id` - Foreign key to Bookings
- `payment_type` - Type (rental, deposit, refund)
- `amount` - Payment amount
- `stripe_payment_id` - Stripe transaction ID
- `status` - Payment status (pending, completed, refunded)
- `created_at` - Payment timestamp

---

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Create new user account
- `POST /login` - Authenticate and receive JWT token
- `GET /me` - Get current user profile (requires auth)
- `PUT /profile` - Update user profile (requires auth)

### Equipment (`/api`)
- `GET /equipment` - Get all available equipment (optional ?category filter)
- `GET /equipment/:id` - Get specific equipment details
- `POST /equipment` - Create new equipment listing (owner only)
- `PUT /equipment/:id` - Update equipment listing (owner only)
- `DELETE /equipment/:id` - Delete equipment listing (owner only)
- `GET /my-equipment` - Get current user's equipment listings (requires auth)

### Bookings (`/api`)
- `POST /bookings` - Create new booking (requires auth)
- `GET /bookings/:id` - Get specific booking details (requires auth)
- `GET /my-bookings` - Get current user's bookings (requires auth)
- `GET /equipment/:id/bookings` - Get all bookings for equipment (owner only)
- `PUT /bookings/:id/status` - Update booking status (requires auth)

### Payments (`/api`)
- `POST /create-payment-intent` - Create Stripe payment intent (requires auth)
- `POST /confirm-payment` - Confirm payment completion (requires auth)
- `POST /refund-deposit` - Refund security deposit (owner only)
- `GET /bookings/:id/payments` - Get all payments for booking (requires auth)

---

## User Workflows

### Renter Workflow
1. **Sign Up**: Create account as "Renter" or "Both"
2. **Browse**: Explore equipment by category
3. **Book**: Select equipment and choose rental dates
4. **Pay**: Complete payment (rental cost + 50% deposit)
5. **Use**: Pick up and use equipment during rental period
6. **Return**: Return equipment to owner
7. **Refund**: Receive deposit refund after owner confirms return

### Owner Workflow
1. **Sign Up**: Create account as "Owner" or "Both"
2. **List Equipment**: Add equipment with details, photos, and pricing
3. **Manage**: Update availability and pricing as needed
4. **Receive Bookings**: Get notified of new booking requests
5. **Confirm**: Approve bookings and coordinate pickup
6. **Track**: Monitor active rentals
7. **Process Return**: Inspect equipment and refund deposit

---

## Payment Processing

### Stripe Integration
The platform uses Stripe for secure payment processing. To enable payments in production:

1. **Get Stripe API Keys**: Sign up at https://stripe.com
2. **Set Environment Variable**: `export STRIPE_SECRET_KEY=sk_live_...`
3. **Test Mode**: Use `sk_test_...` keys for testing
4. **Production**: Use `sk_live_...` keys for real transactions

### Deposit System
- **Calculation**: Deposit = 50% of total rental cost
- **Charge**: Collected at booking time along with rental fee
- **Hold**: Held until equipment is returned
- **Refund**: Processed by owner after confirming equipment condition
- **Protection**: Covers potential damage or loss

---

## Security Features

### Authentication
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: Werkzeug security for encrypted passwords
- **Token Expiration**: 7-day access token validity
- **Protected Routes**: API endpoints require valid JWT

### Data Protection
- **CORS**: Configured for secure cross-origin requests
- **Input Validation**: Required field validation on all forms
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **XSS Protection**: React's built-in sanitization

---

## Deployment Information

### Current Deployment
- **Platform**: Manus Cloud
- **URL**: https://g8h3ilcq7pxe.manus.space
- **Framework**: Flask backend serving React frontend
- **Database**: SQLite (persisted in deployment)
- **Environment**: Production-ready with CORS enabled

### Local Development
```bash
# Backend
cd ~/outdoor-rental-website/backend
source venv/bin/activate
python src/main.py
# Runs on http://localhost:5000

# Frontend (for development)
cd ~/outdoor-rental-website/rental-site
pnpm run dev
# Runs on http://localhost:5173
```

### Building for Production
```bash
# Build frontend
cd ~/outdoor-rental-website/rental-site
pnpm run build

# Copy to backend static folder
cp -r dist/* ../backend/src/static/

# Deploy backend (serves both API and frontend)
# Use Manus deploy tools or your preferred hosting
```

---

## Future Enhancements

### Recommended Features
1. **Image Upload**: Allow owners to upload equipment photos directly
2. **Reviews & Ratings**: Let renters review equipment and owners
3. **Messaging System**: In-app communication between renters and owners
4. **Calendar Integration**: Visual availability calendar
5. **Email Notifications**: Booking confirmations and reminders
6. **Search & Filters**: Advanced search with price range, location, etc.
7. **Insurance Options**: Optional damage insurance for high-value items
8. **Multi-day Discounts**: Automatic pricing for weekly/monthly rentals
9. **Location Services**: GPS-based equipment search
10. **Mobile App**: Native iOS/Android applications

### Technical Improvements
- **PostgreSQL**: Migrate from SQLite for better scalability
- **Redis**: Add caching for improved performance
- **Celery**: Background tasks for email notifications
- **S3 Storage**: Cloud storage for equipment images
- **Analytics**: Track usage patterns and popular equipment
- **Admin Dashboard**: Platform management and moderation tools

---

## Equipment Categories

### Power & Energy
- Portable power stations
- Generators
- Solar panels
- Battery packs
- Inverters

### Connectivity
- Starlink satellite internet
- Mobile hotspots
- Signal boosters
- Communication radios

### Recreation
- Paddle boards (SUP)
- Kayaks
- Camping hammocks
- Tents
- Coolers
- Camping stoves

---

## Support & Contact

### Platform Information
- **Name**: The Wild Share
- **Tagline**: Share the Wild, Rent the Adventure
- **Mission**: Connect outdoor enthusiasts with quality equipment rentals

### Technical Support
For technical issues, feature requests, or questions:
- Review this documentation
- Check API endpoint responses for error messages
- Verify Stripe API key configuration for payment issues
- Ensure JWT tokens are properly stored and sent with requests

---

## License & Copyright

© 2025 The Wild Share. All rights reserved.

---

## Quick Start Guide

### For New Users
1. Visit https://g8h3ilcq7pxe.manus.space
2. Click "Sign In" → "Need an account? Register"
3. Choose account type (Renter, Owner, or Both)
4. Fill in your details and create account
5. Start browsing equipment or list your own!

### For Owners
1. Sign in and navigate to "My Equipment"
2. Click "Add Equipment" button
3. Fill in equipment details:
   - Name and description
   - Category
   - Daily price
   - Capacity/specifications
   - Image URL
4. Submit to create listing
5. Manage bookings from your dashboard

### For Renters
1. Browse equipment on the home page
2. Filter by category if desired
3. Click "Book Now" on desired equipment
4. Enter rental dates (YYYY-MM-DD format)
5. Complete payment (rental + 50% deposit)
6. View booking in "My Bookings"

---

**Built with ❤️ for outdoor adventurers everywhere**

