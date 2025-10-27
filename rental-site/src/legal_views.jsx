// Legal views for Terms of Service and Privacy Policy
// These are added to App.jsx to fix broken footer links

export const TermsOfServiceView = ({ setCurrentView }) => (
  <div className="max-w-4xl mx-auto py-8">
    <h1 className="text-4xl font-bold text-center text-emerald-600 border-b-4 border-emerald-600 pb-4 mb-6">
      Terms of Service
    </h1>
    <p className="text-center text-sm text-slate-600 mb-8">Last Updated: October 26, 2025</p>

    <div className="space-y-6 text-slate-700">
      <p>Welcome to The Wild Share! These Terms of Service ("Terms") govern your use of our outdoor equipment rental marketplace. By using our platform, you agree to these Terms. Please read them carefully.</p>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">1. The Platform</h2>
        <p>The Wild Share is a peer-to-peer marketplace that connects equipment owners with individuals seeking to rent outdoor gear. We are not a party to any rental agreement between users. We do not own, control, or manage any of the equipment listed on our platform.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">2. User Accounts</h2>
        <p>You must create an account to use most features of The Wild Share. You agree to provide accurate, current, and complete information during registration and to keep your account information updated. You are responsible for all activity that occurs under your account.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">3. User Responsibilities</h2>
        <p>As a user of The Wild Share, you agree to:</p>
        <ul className="list-disc pl-6 mt-2 space-y-1">
          <li>Comply with all applicable laws and regulations.</li>
          <li>Provide accurate and honest information in your listings and communications.</li>
          <li>Treat other users with respect and courtesy.</li>
          <li>Use the platform only for its intended purpose.</li>
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">4. Listings and Bookings</h2>
        <p>Owners are responsible for the accuracy and content of their listings. Renters are responsible for reading the full listing before booking. A booking is a limited license to use the owner's equipment for the agreed-upon period. The owner reserves the right to cancel a booking if the renter violates these Terms or the rental agreement.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">5. Fees and Payments</h2>
        <p>We charge a platform fee for each booking, which is a percentage of the total rental cost. All payments are processed through our third-party payment provider, Stripe. By making or receiving payments on The Wild Share, you agree to Stripe's terms of service.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">6. Cancellations and Refunds</h2>
        <p>Our cancellation and refund policy is outlined in the rental agreement. We encourage users to communicate directly to resolve any issues. The Wild Share may, in its sole discretion, issue refunds or credits.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">7. Damage to Equipment</h2>
        <p>Renters are responsible for returning the equipment in the same condition it was received, normal wear and tear excepted. Renters are liable for any damage to or loss of the equipment during the rental period. The security deposit will be used to cover the cost of repairs or replacement. If the cost exceeds the deposit, the renter is responsible for the remaining amount.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">8. Disclaimers</h2>
        <p>The Wild Share is provided "as is" without any warranties, express or implied. We do not endorse any user, listing, or equipment. We are not responsible for any damage, injury, or loss arising from your use of the platform or rental of equipment.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">9. Limitation of Liability</h2>
        <p>To the maximum extent permitted by law, The Wild Share shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from your use of our platform.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">10. Governing Law</h2>
        <p>These Terms shall be governed by the laws of the State of California, without regard to its conflict of law provisions.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">11. Changes to Terms</h2>
        <p>We may modify these Terms at any time. We will provide notice of any material changes by posting the new Terms on the platform. Your continued use of The Wild Share after the effective date of the new Terms constitutes your acceptance of the new Terms.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">12. Contact Us</h2>
        <p>If you have any questions about these Terms, please contact us at support@thewildshare.com.</p>
      </div>

      <div className="text-center mt-8">
        <button 
          onClick={() => setCurrentView('browse')} 
          className="px-6 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
        >
          Back to Browse
        </button>
      </div>
    </div>
  </div>
);

export const PrivacyPolicyView = ({ setCurrentView }) => (
  <div className="max-w-4xl mx-auto py-8">
    <h1 className="text-4xl font-bold text-center text-emerald-600 border-b-4 border-emerald-600 pb-4 mb-6">
      Privacy Policy
    </h1>
    <p className="text-center text-sm text-slate-600 mb-8">Last Updated: October 26, 2025</p>

    <div className="space-y-6 text-slate-700">
      <p>At The Wild Share, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform.</p>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">1. Information We Collect</h2>
        <p>We collect information that you provide directly to us, including:</p>
        <ul className="list-disc pl-6 mt-2 space-y-1">
          <li>Account information (name, email address, phone number)</li>
          <li>Profile information (bio, profile photo, location)</li>
          <li>Equipment listings (photos, descriptions, pricing)</li>
          <li>Booking and payment information</li>
          <li>Communications between users</li>
          <li>Identity verification information (through Stripe Identity)</li>
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">2. How We Use Your Information</h2>
        <p>We use the information we collect to:</p>
        <ul className="list-disc pl-6 mt-2 space-y-1">
          <li>Provide, maintain, and improve our services</li>
          <li>Process transactions and send related information</li>
          <li>Send you technical notices and support messages</li>
          <li>Respond to your comments and questions</li>
          <li>Detect, prevent, and address fraud and security issues</li>
          <li>Comply with legal obligations</li>
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">3. Information Sharing</h2>
        <p>We may share your information in the following circumstances:</p>
        <ul className="list-disc pl-6 mt-2 space-y-1">
          <li><strong>With other users:</strong> When you create a listing or make a booking, certain information (name, profile photo, location) is shared with other users</li>
          <li><strong>With service providers:</strong> We use third-party services like Stripe for payments and identity verification</li>
          <li><strong>For legal reasons:</strong> We may disclose information if required by law or to protect our rights</li>
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">4. Data Security</h2>
        <p>We implement appropriate technical and organizational measures to protect your personal information. However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">5. Your Rights</h2>
        <p>You have the right to:</p>
        <ul className="list-disc pl-6 mt-2 space-y-1">
          <li>Access and update your personal information</li>
          <li>Delete your account and associated data</li>
          <li>Opt out of marketing communications</li>
          <li>Request a copy of your data</li>
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">6. Cookies and Tracking</h2>
        <p>We use cookies and similar tracking technologies to collect information about your browsing activities. You can control cookies through your browser settings.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">7. Children's Privacy</h2>
        <p>Our platform is not intended for users under the age of 18. We do not knowingly collect personal information from children.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">8. Changes to This Policy</h2>
        <p>We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.</p>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-emerald-700 border-b border-slate-300 pb-2 mb-3">9. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us at privacy@thewildshare.com.</p>
      </div>

      <div className="text-center mt-8">
        <button 
          onClick={() => setCurrentView('browse')} 
          className="px-6 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
        >
          Back to Browse
        </button>
      </div>
    </div>
  </div>
);

