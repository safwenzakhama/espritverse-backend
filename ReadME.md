# EspritVerse Backend

A comprehensive Django REST API backend for the EspritVerse social platform, designed specifically for ESPRIT School of Business students. This platform enables students to connect, share content, manage clubs, find housing, and communicate through various specialized sections.

## 🌟 Features

### Core Functionality
- **User Authentication & Management**: JWT-based authentication with role-based permissions
- **Social Networking**: Friend requests, profiles, and user connections
- **Content Management**: Posts, comments, likes, and media uploads
- **Direct Messaging**: Real-time chat with image support
- **Notifications**: Real-time notifications for various activities
- **AI Content Moderation**: Google Gemini-powered content filtering

### Platform Sections
- **Committee Hub**: Official announcements and campus news
- **Club Space**: Student club management and activities
- **Lost & Found**: Item recovery and community help
- **Colocation**: Housing and roommate finding
- **Profile Walls**: Personal messaging and interactions

### Technical Features
- **RESTful API**: Comprehensive API with Swagger documentation
- **File Upload**: Image handling for avatars, posts, and messages
- **Role-Based Access**: Student, Admin, Committee Admin, Club Manager roles
- **Content Moderation**: AI-powered content filtering by section
- **Real-time Updates**: WebSocket support for live notifications
- **Production Ready**: Docker, Railway deployment, and security configurations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip (Python package manager)
- Git
- (Optional) Docker & Docker Compose for containerized setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd espritverse
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
copy env.example .env  # Windows
cp env.example .env    # macOS/Linux

# Edit .env file with your configuration
```

**Required Environment Variables:**
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Gemini AI (for content moderation)
GEMINI_API_KEY=your-gemini-api-key-here

# Database (SQLite for development)
# No additional database configuration needed for local development
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`

### Key API Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

#### User Management
- `GET /api/users/me/` - Get current user profile
- `PATCH /api/profiles/me/` - Update user profile
- `GET /api/users/` - List users (with search)

#### Social Features
- `GET /api/posts/` - List posts (with filtering)
- `POST /api/posts/` - Create new post
- `GET /api/posts/{id}/comments/` - Get post comments
- `POST /api/posts/{id}/comments/` - Add comment

#### Direct Messaging
- `GET /api/dm/conversations/` - List conversations
- `POST /api/dm/conversations/open/` - Start new conversation
- `GET /api/dm/messages/` - Get messages
- `POST /api/dm/messages/` - Send message

#### Notifications
- `GET /api/notifications/` - List notifications
- `PATCH /api/notifications/{id}/read/` - Mark as read

## 🏗️ Project Structure

```
espritverse/
├── accounts/              # User management and authentication
│   ├── models.py         # User model and friend requests
│   ├── views.py          # Auth views (login, register, profile)
│   ├── serializers.py    # User data serialization
│   └── permissions.py    # Role-based permissions
├── social/               # Posts, comments, and social features
│   ├── models.py         # Post, Comment, Like models
│   ├── views.py          # Post and comment views
│   ├── serializers.py    # Content serialization
│   ├── permissions.py    # Content creation permissions
│   └── content_moderation.py  # AI content filtering
├── dm/                   # Direct messaging system
│   ├── models.py         # Conversation and Message models
│   ├── views.py          # Chat views
│   └── serializers.py    # Message serialization
├── notifications/        # Notification system
│   ├── models.py         # Notification model
│   ├── views.py          # Notification views
│   └── signals.py        # Auto-notification triggers
├── config/               # Django configuration
│   ├── settings.py       # Development settings
│   ├── settings_production.py  # Production settings
│   └── urls.py          # URL routing
├── media/                # User uploaded files
│   ├── avatars/         # User profile pictures
│   ├── posts/           # Post images
│   ├── comments/        # Comment images
│   └── messages/        # DM images
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Development Settings
The project uses different settings for development and production:

- **Development**: `config/settings.py` (SQLite, debug enabled)
- **Production**: `config/settings_production.py` (PostgreSQL, security enabled)

### Key Configuration Areas

#### Database
- **Development**: SQLite (no additional setup required)
- **Production**: PostgreSQL (configured via DATABASE_URL)

#### Media Files
- **Local**: Files stored in `media/` directory
- **Production**: Can be configured for cloud storage

#### CORS Settings
```python
# Development
CORS_ALLOW_ALL_ORIGINS = True

# Production
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.vercel.app"
]
```

## 🐳 Docker Setup (Alternative)

### Using Docker Compose
```bash
# Start all services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down
```

### Docker Services
- **Web**: Django application
- **Database**: PostgreSQL (for production-like environment)
- **Redis**: For caching and sessions

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test social
python manage.py test dm
python manage.py test notifications
```

### Test Content Moderation
```bash
python test_moderation.py
```

## 🚀 Deployment

### Railway Deployment
The project is configured for Railway deployment:

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Environment Variables**: Set production environment variables
3. **Database**: Railway automatically provides PostgreSQL
4. **Build**: Railway automatically builds and deploys

### Required Production Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=postgresql://... (provided by Railway)
ALLOWED_HOSTS=your-app.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Manual Deployment Steps
```bash
# Install production dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 🔐 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Different permissions for different user roles
- **Content Permissions**: Section-specific posting permissions

### Content Security
- **AI Moderation**: Google Gemini-powered content filtering
- **File Validation**: Image type and size validation
- **CORS Protection**: Configurable cross-origin resource sharing

### Production Security
- **HTTPS Enforcement**: SSL redirect in production
- **Secure Cookies**: HttpOnly and Secure cookie flags
- **CSRF Protection**: Cross-site request forgery protection

## 📊 User Roles & Permissions

### Student (Default)
- Create posts in Lost & Found and Colocation
- Comment on posts
- Send direct messages
- Manage profile

### Club Manager
- All student permissions
- Create posts in Club section
- Manage club-related content

### Committee Admin
- All student permissions
- Create posts in ESPRIT Committee section
- Official announcements

### Admin
- All permissions
- User management
- Content moderation
- System administration

## 🤖 AI Content Moderation

The platform uses Google Gemini AI for intelligent content moderation:

### Features
- **Section-Specific Guidelines**: Different rules for each platform section
- **Automatic Filtering**: Posts are analyzed before publication
- **User Feedback**: Clear explanations for rejected content
- **Admin Notifications**: Alerts for moderation actions

### Supported Sections
- **Committee Hub**: Official announcements only
- **Club Space**: Club-related activities
- **Lost & Found**: Item recovery posts
- **Colocation**: Housing-related content
- **Profile Walls**: Personal interactions

## 🛠️ Development Tools

### Useful Commands
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Run shell
python manage.py shell

# Check project
python manage.py check
```

### Database Management
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📝 API Usage Examples

### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student123",
    "email": "student@esprit.tn",
    "password": "securepassword",
    "display_name": "John Doe",
    "role": "student"
  }'
```

### Create Post
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Looking for Roommate",
    "content": "Need a roommate for 2-bedroom apartment near ESPRIT",
    "section": "colocation"
  }'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/dm/messages/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "conversation=1" \
  -F "content=Hello!" \
  -F "image=@/path/to/image.jpg"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Solution: Run migrations
python manage.py migrate
```

#### 2. Static Files Not Loading
```bash
# Solution: Collect static files
python manage.py collectstatic
```

#### 3. Permission Denied Errors
- Check user roles and permissions
- Verify JWT token is valid
- Ensure user has appropriate role for the action

#### 4. Content Moderation Errors
- Verify GEMINI_API_KEY is set correctly
- Check internet connection
- Review content moderation logs

#### 5. CORS Errors
- Update CORS_ALLOWED_ORIGINS in settings
- Check frontend URL configuration

### Debug Mode
Enable debug mode for detailed error information:
```python
# In settings.py
DEBUG = True
```

### Logging
Check Django logs for detailed error information:
```bash
# View logs in development
python manage.py runserver --verbosity=2
```

## 📞 Support

### Getting Help
1. **Check Documentation**: Review this README and API docs
2. **Test Environment**: Use the test scripts provided
3. **Debug Mode**: Enable debug mode for detailed errors
4. **Logs**: Check application logs for error details

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is developed for ESPRIT School of Business. Please refer to the institution's guidelines for usage and distribution.

---

**EspritVerse Backend** - Connecting ESPRIT students through technology 🎓✨
