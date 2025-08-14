# NGO Platform - Complete Code Package

## Overview
This is a comprehensive Flask-based NGO volunteer management platform with role-based access control for volunteers, NGOs, donors, and administrators.

## Key Features
- **User Roles**: Volunteers, NGOs, Donors, Admins with strict access control
- **Time Slot System**: 2-hour volunteer time slots with booking management
- **Verification System**: Photo upload verification for completed volunteer work
- **Achievement System**: Points-based achievements with leaderboards
- **Donation Tracking**: Financial contribution management with anonymity options
- **Admin Panel**: Platform oversight with user management and analytics

## Project Structure
```
ngo-platform/
├── app.py                 # Flask application configuration
├── main.py                # Application entry point
├── models.py              # Database models and relationships
├── routes.py              # All route handlers and business logic
├── forms.py               # Flask-WTF form definitions
├── utils.py               # Utility functions and helpers
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template with Bootstrap styling
│   ├── index.html        # Landing page
│   ├── auth/             # Authentication templates
│   ├── volunteer/        # Volunteer dashboard and features
│   ├── ngo/              # NGO management interface
│   ├── donor/            # Donor features and impact reports
│   ├── admin/            # Administrative interface
│   └── errors/           # Error pages
├── static/               # CSS and JavaScript files
└── uploads/              # Verification photo storage
```

## Database Models
1. **User** - Multi-role user system with profile data
2. **Project** - NGO projects with time slots
3. **TimeSlot** - 2-hour volunteer time slots
4. **Booking** - Volunteer bookings for time slots
5. **VerificationUpload** - Photo verification system
6. **Donation** - Donation tracking with project links
7. **Achievement** - Gamification achievements
8. **UserAchievement** - User achievement tracking

## Technology Stack
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (configurable via DATABASE_URL)
- **Frontend**: Bootstrap with dark theme styling
- **Authentication**: Flask-Login with password hashing
- **File Handling**: Werkzeug secure uploads

## Installation & Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SESSION_SECRET`: Flask session secret key
3. Run: `python main.py` or `gunicorn main:app`

## Environment Configuration
The application uses environment-based configuration:
- Development: SQLite fallback if no DATABASE_URL
- Production: PostgreSQL via DATABASE_URL
- Session security via SESSION_SECRET

## Role-Based Features

### Volunteers
- Dashboard with stats and upcoming slots
- Project browsing and time slot booking
- Verification photo uploads for completed work
- Achievement tracking and leaderboards

### NGOs
- Project creation and management
- Time slot scheduling (2-hour increments)
- Volunteer management and verification review
- Performance analytics

### Donors
- Project browsing for donations
- Donation history and impact reports
- Anonymous donation options

### Administrators
- Platform-wide user management
- Verification queue monitoring
- Platform analytics and reporting
- User activation/deactivation controls

## Security Features
- Password hashing with Werkzeug
- Role-based route protection
- Secure file upload handling
- CSRF protection via Flask-WTF
- Session management with configurable secrets

## Deployment Ready
- Production WSGI configuration with Gunicorn
- Environment-based database configuration
- Error handling with custom error pages
- Bootstrap responsive design for all devices

The platform is designed for scalability and can handle multiple NGOs, thousands of volunteers, and comprehensive donation tracking.