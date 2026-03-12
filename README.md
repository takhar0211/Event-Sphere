# EventSphere — Smart Event Management Platform

A full-featured Django event management and ticket booking web application.

## Features

### Authentication
- User registration & login with role-based access
- Three roles: **User**, **Organizer**, **Admin**
- Password hashing (Django's built-in PBKDF2)
- Profile management with avatar upload

### Event Management (Organizers)
- Create, edit, delete events
- Set ticket price, max attendees, description
- Upload event images
- Category assignment
- Draft / Published / Cancelled status
- Automatic slug generation

### Ticket Booking (Users)
- Browse & search events (by keyword, category, date, price)
- Filter and sort events
- Book 1–10 tickets per event
- Automatic ticket count reduction with race-condition protection
- Prevent duplicate bookings
- Cancel bookings (tickets restored)
- Booking history dashboard

### Admin Dashboard
- View all users, events, bookings
- Revenue statistics by category
- Activate/deactivate user accounts
- Remove inappropriate events
- Platform-wide analytics

### UI/UX
- Fully responsive dark theme design
- Clean navigation with role-aware menus
- Form validation (client + server)
- Flash messages for all actions
- Event cards with occupancy progress bars
- Ticket confirmation page with unique Booking ID

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
cd eventplatform
python setup.py
```
This will:
- Run all database migrations
- Load category fixtures
- Create test accounts
- Create 8 sample events

### 3. Start the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## Test Accounts

| Role      | Username    | Password     |
|-----------|-------------|--------------|
| Admin     | admin       | admin123     |
| Organizer | organizer1  | org123456    |
| User      | user1       | user123456   |

## Project Structure
```
eventplatform/
├── eventplatform/          # Django project config
│   ├── settings.py
│   └── urls.py
├── accounts/               # Custom user model + auth
│   ├── models.py           # User with role field
│   ├── views.py            # Register, login, profile
│   └── forms.py
├── events/                 # Event management
│   ├── models.py           # Event, Category
│   ├── views.py            # CRUD + search/filter
│   ├── forms.py
│   └── fixtures/
│       └── categories.json
├── bookings/               # Ticket booking
│   ├── models.py           # Booking with UUID ID
│   └── views.py            # Book, cancel, confirm
├── dashboard/              # Role dashboards
│   └── views.py            # User/Organizer/Admin
├── templates/              # All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── events/
│   ├── bookings/
│   └── dashboard/
├── media/                  # Uploaded images
├── static/                 # CSS/JS assets
├── requirements.txt
└── setup.py                # One-click setup
```

## Security Features
- CSRF protection on all forms
- Login-required decorators on protected views
- Role checks before organizer/admin actions
- `select_for_update()` on ticket booking (prevents overbooking)
- Unique booking constraint per user per event
- Password hashing via Django's auth system

## Database
Uses SQLite by default (no setup needed). Switch to PostgreSQL:
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eventsphere',
        'USER': 'your_user',
        'PASSWORD': 'your_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
