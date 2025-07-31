# Creator Subscription Platform

A complete creator subscription platform built with Django REST Framework and React. Creators can monetize their content through monthly subscriptions, one-time tips, and direct messaging with subscribers.

## 🚀 Features

### Core Features
- **User Registration System**: Two account types - Creators and Subscribers
- **Creator Profiles**: Bio, profile picture, cover image, and content feed
- **Subscription System**: Monthly pricing tiers ($4.99, $9.99, $19.99, $49.99)
- **Content Management**: Text, image, and video posts with paywall protection
- **Direct Messaging**: Real-time messaging between creators and subscribers
- **Tipping System**: One-time payments ($1, $5, $10, $25, $50, $100)

### Monetization
- **Platform Fee**: 12% on all transactions
- **Stripe Integration**: Secure payment processing
- **Creator Earnings Dashboard**: Track total earnings and payouts
- **Weekly Payouts**: Automated payment system to creators
- **Subscription Management**: Upgrade, downgrade, cancel subscriptions

### Content Categories
- Fitness & Health
- Cooking & Recipes
- Art & Design
- Music & Entertainment
- Lifestyle & Fashion
- Education & Tutorials
- Adult Content (18+ verified section)

### User Interface
- **Homepage**: Featured creators and trending content
- **Creator Discovery**: Search and filter by categories
- **Personal Feed**: Subscribed content feed
- **Account Settings**: Payment methods and preferences
- **Mobile Responsive**: Works on all devices

## 🛠 Tech Stack

### Backend
- **Django 5.2.4**: Python web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Redis**: Caching and real-time messaging
- **Celery**: Background task processing
- **Stripe**: Payment processing
- **Channels**: WebSocket support for real-time features

### Frontend
- **React 18**: JavaScript framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Tailwind CSS**: Styling
- **Stripe.js**: Payment integration

## 📦 Installation

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL 17+
- Redis 7+

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd creator-platform
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database setup**
   ```bash
   # Install PostgreSQL and create database
   sudo apt install postgresql postgresql-contrib
   sudo -u postgres createdb creator_platform
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start services**
   ```bash
   # Start Redis
   sudo service redis-server start
   
   # Start Django server
   python manage.py runserver
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 🔧 Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DB_NAME=creator_platform
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Stripe Keys
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Stripe Configuration

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Set up webhooks for subscription events
4. Add keys to your .env file

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile

### Creators
- `GET /api/creators/` - List creators
- `GET /api/creators/{id}/` - Get creator details
- `POST /api/creators/create/` - Create creator profile
- `GET /api/creators/featured/` - Featured creators
- `GET /api/creators/categories/` - Content categories

### Subscriptions
- `GET /api/subscriptions/` - User's subscriptions
- `POST /api/subscriptions/create/` - Create subscription
- `POST /api/subscriptions/{id}/cancel/` - Cancel subscription

### Content
- `GET /api/content/posts/` - List posts
- `POST /api/content/posts/` - Create post
- `POST /api/content/posts/{id}/like/` - Like post

### Payments
- `POST /api/payments/tips/` - Send tip
- `GET /api/payments/earnings/` - Creator earnings
- `POST /api/payments/payouts/` - Request payout

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Database**
   - Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
   - Update database credentials in .env

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Web Server**
   - Use Nginx + Gunicorn for Django
   - Deploy React build to CDN

5. **Background Tasks**
   ```bash
   celery -A creator_platform worker --loglevel=info
   celery -A creator_platform beat --loglevel=info
   ```

## 💰 Business Model

- **Platform Fee**: 12% on all transactions
- **Revenue Streams**:
  - Subscription fees
  - One-time tips
  - Premium features (future)
  - Advertisement (future)

## 🔒 Security Features

- JWT token authentication
- CORS protection
- SQL injection prevention
- XSS protection
- CSRF protection
- Age verification for adult content
- Secure payment processing with Stripe

## 📊 Analytics & Monitoring

- User engagement tracking
- Creator performance metrics
- Revenue analytics
- Subscription lifecycle tracking
- Payment success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support, email support@creatorplatform.com or join our Discord community.

---

**Built with ❤️ for creators worldwide**