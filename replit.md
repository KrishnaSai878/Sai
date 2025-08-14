# NGO Platform

## Overview

This is a comprehensive NGO volunteer management platform built with Flask that connects volunteers, NGOs, donors, and administrators in a unified ecosystem. The platform facilitates volunteer project management, time slot booking, donation processing, and achievement tracking with role-based access control.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme for responsive UI
- **CSS Framework**: Bootstrap with custom CSS overrides for role-specific styling
- **JavaScript**: Vanilla JavaScript for interactive features including modal management, file uploads, form validation, and real-time notifications
- **Icon System**: Feather icons for consistent visual elements

### Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Authentication**: Flask-Login for session management with role-based access control
- **Database ORM**: SQLAlchemy with declarative base model structure
- **Form Handling**: Flask-WTF with comprehensive form validation
- **File Management**: Werkzeug secure filename handling for verification photo uploads

### Role-Based System Design
The platform implements four distinct user roles with specific access patterns:
- **Volunteers**: Browse projects, book time slots, upload verification photos, track achievements
- **NGOs**: Create projects, manage time slots, review verifications, track volunteer engagement
- **Donors**: Browse projects, make donations, view impact reports
- **Administrators**: Platform oversight, user management, verification queue monitoring

### Data Storage Solutions
- **Primary Database**: SQLAlchemy ORM with configurable database URI (defaults to SQLite for development)
- **File Storage**: Local filesystem for verification photo uploads with organized folder structure
- **Session Management**: Flask session handling with configurable secret keys

### Key Data Models
- **User Management**: Comprehensive user profiles with role-based permissions
- **Project System**: NGO-created projects with detailed metadata and skill requirements
- **Booking System**: Time slot management with capacity controls and status tracking
- **Verification System**: Photo upload and review workflow for completed volunteer work
- **Achievement System**: Gamification through points and milestone achievements
- **Donation Tracking**: Financial contribution management with anonymity options

### Security Architecture
- **Authentication**: Password hashing with Werkzeug security utilities
- **Authorization**: Decorator-based role checking for route protection
- **File Security**: Secure filename generation and file type validation
- **Session Security**: Configurable session secrets with environment variable support

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and model management
- **Flask-Login**: User session and authentication management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form field validation and rendering

### Frontend Dependencies
- **Bootstrap**: CSS framework via CDN (bootstrap-agent-dark-theme)
- **Feather Icons**: Icon library via CDN
- **Custom CSS**: Role-specific styling and visual enhancements

### Development Tools
- **Werkzeug**: WSGI utilities and development server
- **ProxyFix**: Middleware for deployment behind reverse proxies

### File and Media Handling
- **Werkzeug**: Secure file upload processing
- **Local filesystem**: Verification photo storage with organized directory structure

### Database Configuration
- **Configurable Database URI**: Environment-based database selection
- **Connection Pooling**: SQLAlchemy engine options for production deployment
- **Migration Support**: Declarative base model structure ready for Alembic integration

The platform is designed for scalability with environment-based configuration and modular architecture supporting easy deployment and maintenance.