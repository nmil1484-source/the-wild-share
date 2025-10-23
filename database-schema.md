# Database Schema Design

## Tables

### Users
- id (Primary Key)
- email (Unique)
- password_hash
- first_name
- last_name
- phone
- user_type (owner/renter/both)
- profile_image_url
- created_at
- updated_at

### Equipment
- id (Primary Key)
- owner_id (Foreign Key -> Users)
- name
- description
- category (power/connectivity/recreation)
- daily_price
- capacity_spec
- image_url
- is_available
- created_at
- updated_at

### Bookings
- id (Primary Key)
- equipment_id (Foreign Key -> Equipment)
- renter_id (Foreign Key -> Users)
- start_date
- end_date
- total_days
- daily_rate
- total_cost
- deposit_amount (50% of total_cost)
- status (pending/confirmed/active/completed/cancelled)
- created_at
- updated_at

### Payments
- id (Primary Key)
- booking_id (Foreign Key -> Bookings)
- payment_type (rental/deposit/refund)
- amount
- stripe_payment_id
- status (pending/completed/failed/refunded)
- created_at
- updated_at

### Reviews
- id (Primary Key)
- booking_id (Foreign Key -> Bookings)
- reviewer_id (Foreign Key -> Users)
- rating (1-5)
- comment
- created_at
- updated_at

