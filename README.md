# The Wild Share

**Share the Wild, Rent the Adventure**

A full-stack outdoor equipment rental marketplace built with Flask and React.

![The Wild Share](https://img.shields.io/badge/Flask-3.1.1-green) ![React](https://img.shields.io/badge/React-19.1.0-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

- 🔐 **User Authentication** - Secure registration and login
- 📦 **Equipment Listings** - Browse and list outdoor gear
- 📅 **Booking System** - Reserve equipment with date validation
- 💳 **Payment Processing** - Stripe integration with 50% deposits
- 👥 **Dual User Types** - Renters and equipment owners
- 📱 **Responsive Design** - Works on all devices

## Tech Stack

**Backend:**
- Flask 3.1.1
- SQLAlchemy
- Flask-JWT-Extended
- Stripe API

**Frontend:**
- React 19.1.0
- Tailwind CSS
- shadcn/ui components
- Axios

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/the-wild-share.git
cd the-wild-share

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

Visit `http://localhost:5000` to see the app.

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Or follow the [detailed deployment guide](DEPLOYMENT_GUIDE.md).

## Environment Variables

```
FLASK_APP=src/main.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=sk_test_... (optional)
```

## Equipment Categories

- ⚡ **Power & Energy** - Power stations, generators, solar panels
- 📡 **Connectivity** - Starlink, mobile hotspots, signal boosters  
- 🏄 **Recreation** - Paddle boards, kayaks, camping gear

## Documentation

- [Full Documentation](THE_WILD_SHARE_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Documentation](docs/API.md)

## License

MIT License - feel free to use this project for your own purposes.

## Support

For questions or issues, please open an issue on GitHub.

---

Built with ❤️ for outdoor adventurers everywhere

# Deployment Thu Oct 23 17:49:41 EDT 2025
# Trigger deployment
