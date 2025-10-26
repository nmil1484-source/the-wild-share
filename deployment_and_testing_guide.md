# The Wild Share: Stripe Payment Integration & Testing Guide

**Author: Manus AI**

**Date: October 25, 2025**

---

## 1. Introduction

This document provides a comprehensive guide to deploying and testing the newly integrated Stripe payment system for **The Wild Share** outdoor equipment rental platform. The system is now fully implemented, including a 10% platform fee, a complete booking and checkout flow, and a secure payment processing backend.

Following this guide will ensure that your environment is correctly configured and allow you to perform end-to-end tests of the entire rental and payment process.

## 2. Environment Variables

Correctly setting up your environment variables is crucial for the application to function. You will need to configure variables for both the backend (on Railway) and the frontend (locally).

### 2.1. Backend Environment Variables (Railway)

These variables must be set in your Railway project environment. You have already provided the Stripe keys, but please ensure they are correctly set up as follows:

| Variable Name             | Value                                                                                                | Description                                                                                                                               |
| ------------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `STRIPE_SECRET_KEY`       | `sk_test_...`                                                                                        | Your Stripe secret key for test mode. **Keep this secret and never expose it on the frontend.**                                             |
| `STRIPE_PUBLISHABLE_KEY`  | `pk_test_...`                                                                                        | Your Stripe publishable key for test mode. This will be used on the frontend.                                                             |
| `PLATFORM_FEE_PERCENT`    | `10`                                                                                                 | The commission percentage the platform takes from each rental. This is now set to 10%.                                                    |

**Note:** Your other existing variables (`DATABASE_URL`, `AWS_ACCESS_KEY_ID`, etc.) should remain unchanged.

### 2.2. Frontend Environment Variables (Local)

For the frontend application to communicate with Stripe, you need to create a `.env` file in the `rental-site` directory. I have already created this for you with the correct test key.

**File Path:** `/home/ubuntu/outdoor-rental-website/rental-site/.env`

```
# Stripe Publishable Key (Test Mode)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_51SJPdQGW9js9GVkoZfMrWFNQkyGJGyW9Ls6Aisq4tGlYN2UNLG9HvS36YwjO51kHNTKvIgx5ImLK6I8PpjEV2zg700WKXnDRQ5
```

This file is included in the `.gitignore` and will not be committed to your repository, ensuring your keys remain secure.

## 3. Running the Application

### 3.1. Backend (Railway)

Your backend is configured for auto-deployment from your GitHub repository. Any changes I have made will be automatically deployed to Railway. You can monitor the deployment status in your Railway dashboard.

### 3.2. Frontend (Local)

To run the frontend and see the new checkout flow, follow these steps:

1.  **Navigate to the frontend directory:**

    ```bash
    cd /home/ubuntu/outdoor-rental-website/rental-site
    ```

2.  **Install dependencies (if you haven't already):**

    ```bash
    pnpm install
    ```

3.  **Start the development server:**

    ```bash
    pnpm dev
    ```

4.  **Access the application:**

    Open your browser and navigate to the local URL provided by Vite (usually `http://localhost:5173`).

## 4. Testing the Complete Payment Flow

This end-to-end test will simulate the entire user journey, from listing equipment to booking and payment.

### Step 1: Create Test Users

1.  **Register an "Owner" account:** Create a new user who will own and list equipment.
2.  **Register a "Renter" account:** Create a second user who will rent the equipment.

### Step 2: Complete Stripe Onboarding (as the Owner)

Before an owner can receive payments, they must complete the Stripe Connect onboarding process. I have created a temporary way to do this for testing:

1.  **Log in as the Owner.**
2.  In your browser, navigate to `YOUR_RAILWAY_APP_URL/api/stripe/create-account-link` (replace `YOUR_RAILWAY_APP_URL` with your actual Railway deployment URL).
3.  This will redirect you to a Stripe onboarding page. **Use Stripe's test data** to fill out the form. You can find test data and information in the [Stripe Connect documentation](https://stripe.com/docs/connect/testing).
4.  Once onboarding is complete, you will be redirected back to your application.

### Step 3: List Equipment (as the Owner)

1.  While logged in as the Owner, go to the "My Equipment" page.
2.  Click "Add Equipment" and fill out the form to list a new item for rent.

### Step 4: Book and Pay (as the Renter)

1.  **Log out from the Owner account and log in as the Renter.**
2.  Find the equipment you just listed on the "Browse" page.
3.  Click the **"Book Now"** button.
4.  A dialog will appear. Select a start and end date for the rental.
5.  Click **"Continue to Payment"**. This will create the booking and open the Stripe Checkout form.
6.  In the checkout form, you will see a summary of the charges, including the rental cost, security deposit, and platform fee breakdown.
7.  Use one of Stripe's test cards to complete the payment. You can find a list of test cards in the [Stripe documentation](https://stripe.com/docs/testing#cards).

### Step 5: Verify the Transaction

1.  **On the frontend:** After a successful payment, you will be redirected to your "My Bookings" page, where you should see the new booking with a "Confirmed" status.
2.  **In your Stripe Dashboard:**
    *   Log in to your Stripe account.
    *   Go to the "Payments" section. You should see the payment you just made.
    *   Click on the payment to see the details. You will see that the platform fee (10%) has been deducted and the remaining amount is allocated to the connected owner account.

## 5. Conclusion

Congratulations! You have successfully tested the complete rental and payment flow. The system is now ready for further development and, eventually, production launch.

**Next Steps:**

*   **Request Production Access:** Before going live, you will need to request production access for both AWS SES and Stripe.
*   **Stripe Connect Payouts:** The current implementation uses Stripe's automatic payouts. You may want to configure payout schedules in your Stripe dashboard.

If you have any questions or issues, please let me know.

