#!/usr/bin/env python3
"""
EventSphere Setup Script
Run this ONCE after installing dependencies to set up the database.
Usage: python setup.py
"""
import os
import sys
import subprocess

def run(cmd, **kwargs):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, **kwargs)
    if result.returncode != 0:
        print(f"  ❌ Command failed: {cmd}")
        sys.exit(1)
    return result

def main():
    print("\n🚀 EventSphere Setup\n" + "="*40)

    # Ensure we're in the right directory
    if not os.path.exists("manage.py"):
        print("❌ Run this script from the eventplatform directory (where manage.py is)")
        sys.exit(1)

    print("\n📦 Running migrations...")
    run("python manage.py makemigrations accounts events bookings")
    run("python manage.py migrate")

    print("\n🌱 Loading category fixtures...")
    run("python manage.py loaddata events/fixtures/categories.json")

    print("\n👤 Creating superuser (admin)...")
    create_admin = """
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventplatform.settings')
django.setup()
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@eventsphere.com', 'admin123')
    u.first_name = 'Admin'
    u.last_name = 'User'
    u.role = 'admin'
    u.save()
    print('  ✅ Admin created: username=admin, password=admin123')
else:
    print('  ℹ️  Admin already exists')
"""
    run(f'python -c "{create_admin}"')

    print("\n🎪 Creating sample organizer...")
    create_organizer = """
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventplatform.settings')
django.setup()
from accounts.models import User
if not User.objects.filter(username='organizer1').exists():
    u = User.objects.create_user('organizer1', 'organizer@eventsphere.com', 'org123456')
    u.first_name = 'Jane'
    u.last_name = 'Smith'
    u.role = 'organizer'
    u.organization = 'TechEvents Co.'
    u.save()
    print('  ✅ Organizer created: username=organizer1, password=org123456')
else:
    print('  ℹ️  Organizer already exists')
"""
    run(f'python -c "{create_organizer}"')

    print("\n🎟️  Creating sample user...")
    create_user = """
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventplatform.settings')
django.setup()
from accounts.models import User
if not User.objects.filter(username='user1').exists():
    u = User.objects.create_user('user1', 'user@eventsphere.com', 'user123456')
    u.first_name = 'John'
    u.last_name = 'Doe'
    u.role = 'user'
    u.save()
    print('  ✅ User created: username=user1, password=user123456')
else:
    print('  ℹ️  User already exists')
"""
    run(f'python -c "{create_user}"')

    print("\n📅 Creating sample events...")
    create_events = """
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventplatform.settings')
django.setup()
from events.models import Event, Category
from accounts.models import User
from datetime import date, time, timedelta

organizer = User.objects.filter(username='organizer1').first()
if not organizer:
    print('No organizer found, skipping events.')
    exit()

cats = {c.slug: c for c in Category.objects.all()}
today = date.today()
sample_events = [
    {'title': 'Global AI & Machine Learning Summit', 'category': 'technology', 'location': 'San Francisco, CA', 'venue_name': 'Moscone Center', 'date': today + timedelta(days=14), 'time': time(9,0), 'end_time': time(18,0), 'ticket_price': 299.00, 'max_attendees': 500, 'description': 'Join 500+ AI researchers and practitioners for a day of cutting-edge talks, workshops, and networking. Speakers from Google DeepMind, OpenAI, and Anthropic.', 'is_featured': True},
    {'title': 'Jazz Under the Stars — Summer Series', 'category': 'music', 'location': 'Central Park, New York', 'venue_name': 'Great Lawn', 'date': today + timedelta(days=7), 'time': time(19,30), 'end_time': time(22,0), 'ticket_price': 45.00, 'max_attendees': 200, 'description': 'An evening of world-class jazz with the NY Jazz Collective. Bring blankets, picnic baskets, and great company.', 'is_featured': True},
    {'title': 'Startup Pitch Day: Seed Edition', 'category': 'business', 'location': 'Austin, TX', 'venue_name': 'The Capital Factory', 'date': today + timedelta(days=21), 'time': time(10,0), 'end_time': time(17,0), 'ticket_price': 0.00, 'max_attendees': 150, 'description': 'Watch 20 early-stage startups pitch to a panel of top VCs. Perfect for founders, investors, and anyone who loves entrepreneurship.', 'is_featured': False},
    {'title': 'Contemporary Art Exhibition: "Futures"', 'category': 'arts-culture', 'location': 'Chicago, IL', 'venue_name': 'Museum of Contemporary Art', 'date': today + timedelta(days=5), 'time': time(11,0), 'end_time': time(20,0), 'ticket_price': 25.00, 'max_attendees': 300, 'description': 'A provocative new exhibition exploring the intersection of technology, identity, and society through 40 works by emerging artists.', 'is_featured': True},
    {'title': 'Half Marathon — City Challenge', 'category': 'sports', 'location': 'Seattle, WA', 'venue_name': 'Seattle Waterfront', 'date': today + timedelta(days=30), 'time': time(7,0), 'end_time': time(12,0), 'ticket_price': 75.00, 'max_attendees': 1000, 'description': 'Run through the beautiful streets of Seattle in our annual half marathon. All fitness levels welcome. Post-race festival included.', 'is_featured': False},
    {'title': 'Wine & Cheese Pairing Masterclass', 'category': 'food-drink', 'location': 'Napa Valley, CA', 'venue_name': 'Silver Oak Estate', 'date': today + timedelta(days=10), 'time': time(15,0), 'end_time': time(18,0), 'ticket_price': 120.00, 'max_attendees': 40, 'description': 'Learn the art of wine and cheese pairing from a certified sommelier. Taste 8 wines paired with artisan cheeses from local producers.', 'is_featured': False},
    {'title': 'Python for Data Science Bootcamp', 'category': 'education', 'location': 'Online', 'venue_name': 'Virtual Event', 'date': today + timedelta(days=3), 'time': time(9,0), 'end_time': time(17,0), 'ticket_price': 149.00, 'max_attendees': 80, 'description': 'Hands-on full-day workshop covering pandas, numpy, matplotlib, and scikit-learn. All levels welcome. Laptop required.', 'is_featured': False},
    {'title': 'Morning Yoga & Mindfulness Retreat', 'category': 'health-wellness', 'location': 'Boulder, CO', 'venue_name': 'Red Rocks Open Space', 'date': today + timedelta(days=2), 'time': time(6,30), 'end_time': time(9,0), 'ticket_price': 35.00, 'max_attendees': 30, 'description': 'Start your week with a sunrise yoga session followed by guided meditation. Mats provided. Suitable for all levels.', 'is_featured': False},
]

for data in sample_events:
    cat_slug = data.pop('category')
    cat = cats.get(cat_slug)
    if not Event.objects.filter(title=data['title']).exists():
        Event.objects.create(organizer=organizer, category=cat, status='published', available_tickets=data['max_attendees'], **data)
        print(f"  ✅ Created: {data['title']}")
    else:
        print(f"  ℹ️  Already exists: {data['title']}")
"""
    run(f'python -c "{create_events}"')

    print("\n✨ Setup Complete!\n" + "="*40)
    print("\n🔑 Test Accounts:")
    print("  Admin:     username=admin      password=admin123")
    print("  Organizer: username=organizer1 password=org123456")
    print("  User:      username=user1      password=user123456")
    print("\n🚀 Start the server:")
    print("  python manage.py runserver")
    print("\n🌐 Visit: http://127.0.0.1:8000/")
    print("  Django Admin: http://127.0.0.1:8000/admin/\n")

if __name__ == '__main__':
    main()
