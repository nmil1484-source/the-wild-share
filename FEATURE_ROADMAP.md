# The Wild Share - Feature Roadmap & Implementation Plan

## ✅ Completed (Just Now)

### 1. Required Equipment Fields
- ✅ Made all equipment form fields required
- ✅ Made specifications field required
- ✅ Made photo upload required (at least 1 photo)
- ✅ Updated label to show asterisk for required photos

### 2. Deposit Messaging Update
- ✅ Changed homepage feature from "50% Deposit Protection" to "Deposit Protection"
- ✅ Made description more general to allow flexibility

### 3. Address Privacy
- ✅ Verified that full addresses are NOT shown on public listings
- ✅ Only city/state location is shown publicly
- ✅ Full address is only in owner's private profile

---

## 🚧 High Priority Features to Implement

### 1. Digital Rental Contracts & E-Signatures

**Purpose:** Protect both owners and renters with legally binding agreements

**Implementation Plan:**

#### A. Contract Templates
Create standardized rental agreement templates including:
- **Equipment description and condition**
- **Rental period and pricing**
- **Liability waiver** (renter assumes responsibility for damage/loss)
- **Insurance requirements**
- **Return conditions**
- **Dispute resolution process**
- **Platform terms of service**

#### B. E-Signature Integration
**Recommended Service:** DocuSign API or HelloSign (Dropbox Sign)

**Workflow:**
1. When booking is created, generate contract PDF with booking details
2. Send to both renter and owner for e-signature
3. Store signed contract in database
4. Require signed contract before payment processing
5. Email copies to both parties

**Database Changes Needed:**
```sql
CREATE TABLE rental_contracts (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    contract_template_id INTEGER,
    contract_pdf_url TEXT,
    renter_signed_at TIMESTAMP,
    owner_signed_at TIMESTAMP,
    docusign_envelope_id TEXT,
    status VARCHAR(50), -- 'pending', 'partially_signed', 'fully_signed'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE contract_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    version VARCHAR(50),
    content TEXT, -- HTML template with variables
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints Needed:**
- `POST /api/contracts/generate` - Generate contract for booking
- `GET /api/contracts/:id` - View contract
- `POST /api/contracts/:id/sign` - Initiate signing process
- `GET /api/contracts/:id/status` - Check signing status

**Frontend Changes:**
- Add contract review step before payment
- Show contract status in booking details
- Add "View Contract" button for completed bookings

---

### 2. Identity Verification System

**Purpose:** Verify user identities to prevent fraud and build trust

**Implementation Options:**

#### Option A: Stripe Identity (Recommended)
- **Pros:** Already using Stripe, seamless integration, compliant
- **Cons:** Costs $1.50 per verification
- **Features:** 
  - Government ID verification
  - Selfie verification
  - Liveness detection
  - Instant results

#### Option B: Persona (persona.com)
- **Pros:** More customizable, good for complex workflows
- **Cons:** More expensive, additional vendor
- **Features:**
  - ID + selfie verification
  - Database checks
  - Watchlist screening

#### Recommended Approach: Stripe Identity

**Implementation:**

**Database Changes:**
```sql
ALTER TABLE users ADD COLUMN identity_verified BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN identity_verification_id TEXT;
ALTER TABLE users ADD COLUMN identity_verified_at TIMESTAMP;
ALTER TABLE users ADD COLUMN verification_status VARCHAR(50); -- 'unverified', 'pending', 'verified', 'failed'
```

**Workflow:**
1. Add "Verify Identity" button in user profile
2. Redirect to Stripe Identity verification flow
3. User uploads government ID (driver's license, passport)
4. User takes selfie for liveness check
5. Stripe verifies and returns result via webhook
6. Update user verification status
7. Show verification badge on profile

**Requirements:**
- Require verification for:
  - Equipment owners before listing
  - Renters before booking high-value items (>$500)
- Optional for low-value rentals to reduce friction

**API Endpoints:**
- `POST /api/users/verify/start` - Initiate verification
- `POST /api/users/verify/webhook` - Handle Stripe webhook
- `GET /api/users/:id/verification-status` - Check status

**Frontend:**
- Verification badge on profiles
- "Verified" indicator on equipment listings
- Prompt unverified users to verify

---

### 3. In-App Messaging System

**Purpose:** Allow renters and owners to communicate securely without sharing personal contact info until after booking

**Implementation:**

**Database Schema:**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    renter_id INTEGER REFERENCES users(id),
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender_id INTEGER REFERENCES users(id),
    message_text TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_unread ON messages(is_read) WHERE is_read = false;
```

**Features:**
- Real-time messaging using WebSockets (Socket.io)
- Unread message notifications
- Message history for each booking
- Automatic conversation creation when booking is made
- Option to share phone number after booking confirmed

**API Endpoints:**
- `GET /api/conversations` - List user's conversations
- `GET /api/conversations/:id/messages` - Get messages
- `POST /api/conversations/:id/messages` - Send message
- `PUT /api/messages/:id/read` - Mark as read
- `WS /api/socket` - WebSocket connection for real-time

**Frontend:**
- Messages icon in navigation with unread count badge
- Conversation list page
- Message thread view
- Real-time message updates
- Push notifications for new messages

---

### 4. Enhanced Liability Protection

**Contract Clauses to Include:**

#### A. Liability Waiver
```
ASSUMPTION OF RISK AND RELEASE OF LIABILITY

The Renter acknowledges and agrees that:

1. Use of the Equipment involves inherent risks including but not limited to 
   property damage, personal injury, or death.

2. The Renter assumes all risks associated with the use of the Equipment.

3. The Renter releases and holds harmless the Equipment Owner and The Wild Share 
   platform from any and all claims, damages, losses, or expenses arising from 
   the use of the Equipment.

4. The Renter is solely responsible for any damage to or loss of the Equipment 
   during the rental period.

5. The Renter agrees to return the Equipment in the same condition as received, 
   normal wear and tear excepted.
```

#### B. Insurance Requirements
```
INSURANCE

1. The Renter is required to maintain adequate insurance coverage for the 
   Equipment during the rental period.

2. For equipment valued over $1,000, proof of insurance may be required.

3. The Renter's insurance shall be primary and non-contributory.

4. The Wild Share and Equipment Owner shall be named as additional insured.
```

#### C. Indemnification
```
INDEMNIFICATION

The Renter agrees to indemnify, defend, and hold harmless the Equipment Owner 
and The Wild Share from and against any and all claims, liabilities, damages, 
losses, costs, and expenses (including reasonable attorneys' fees) arising out 
of or resulting from:

1. Renter's use or misuse of the Equipment
2. Renter's breach of this Agreement
3. Renter's negligence or willful misconduct
4. Any third-party claims related to Renter's use of the Equipment
```

---

## 📋 Implementation Priority Order

### Phase 1: Essential Security (Week 1-2)
1. ✅ Required equipment fields and photos
2. ✅ Deposit messaging updates
3. Digital rental contracts with e-signatures
4. Basic liability waiver in contracts

### Phase 2: Trust & Safety (Week 3-4)
1. Identity verification (Stripe Identity)
2. Verification badges on profiles
3. Enhanced contract templates with full liability protection

### Phase 3: Communication (Week 5-6)
1. In-app messaging system
2. Real-time notifications
3. Contact info sharing after booking confirmation

### Phase 4: Polish & Optimization (Week 7-8)
1. Contract template customization
2. Automated contract generation
3. Message templates and quick replies
4. Enhanced verification requirements based on equipment value

---

## 💰 Cost Estimates

### Third-Party Services
- **DocuSign:** ~$25/month + $0.50 per envelope (or HelloSign: $15/month)
- **Stripe Identity:** $1.50 per verification
- **Socket.io hosting:** Included in current infrastructure
- **File storage (contracts, IDs):** AWS S3 ~$5-10/month

### Development Time Estimates
- **Digital Contracts:** 20-25 hours
- **Identity Verification:** 15-20 hours
- **Messaging System:** 30-35 hours
- **Enhanced Contracts/Liability:** 10-15 hours

**Total:** ~75-95 hours of development

---

## 🔒 Security Considerations

1. **Data Encryption:** All contracts and ID documents encrypted at rest
2. **Access Control:** Only parties to the contract can view it
3. **Audit Trail:** Log all contract views, signatures, and modifications
4. **GDPR/Privacy:** Allow users to request data deletion
5. **PII Protection:** Redact sensitive info in logs and error messages

---

## 📝 Legal Considerations

**Recommend consulting with a lawyer for:**
- Contract template review and state-specific requirements
- Liability waiver enforceability
- Insurance requirements
- Terms of service updates
- Privacy policy updates for ID verification and messaging

---

## Next Steps

1. **Review this plan** and prioritize features
2. **Choose e-signature provider** (DocuSign vs HelloSign)
3. **Consult lawyer** for contract templates
4. **Set up Stripe Identity** in test mode
5. **Begin Phase 1 implementation**

Would you like me to start implementing any of these features now?

