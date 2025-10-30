-- Migration: Add subscription tiers and deposit options
-- Date: 2025-10-29
-- Description: Adds freemium subscription fields to users and deposit options to bookings

-- Add subscription fields to users table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) DEFAULT 'inactive';
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMP;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMP;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP;

-- Add deposit option fields to booking table
ALTER TABLE booking ADD COLUMN IF NOT EXISTS deposit_percentage INTEGER DEFAULT 50;
ALTER TABLE booking ADD COLUMN IF NOT EXISTS remaining_amount FLOAT DEFAULT 0;

-- Update existing bookings to have 50% deposit
UPDATE booking SET deposit_percentage = 50 WHERE deposit_percentage IS NULL;
UPDATE booking SET remaining_amount = (total_cost - deposit_amount) WHERE remaining_amount IS NULL OR remaining_amount = 0;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_subscription_tier ON "user"(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_user_subscription_status ON "user"(subscription_status);
CREATE INDEX IF NOT EXISTS idx_user_stripe_customer_id ON "user"(stripe_customer_id);

-- Verify changes
SELECT 
    'Users with subscription fields' as check_name,
    COUNT(*) as count
FROM "user"
WHERE subscription_tier IS NOT NULL;

SELECT 
    'Bookings with deposit fields' as check_name,
    COUNT(*) as count
FROM booking
WHERE deposit_percentage IS NOT NULL;

-- Show sample data
SELECT 
    email,
    subscription_tier,
    subscription_status,
    created_at
FROM "user"
LIMIT 5;

SELECT 
    id,
    total_cost,
    deposit_amount,
    deposit_percentage,
    remaining_amount
FROM booking
LIMIT 5;

