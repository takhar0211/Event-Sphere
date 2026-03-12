from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from accounts.models import User
from events.models import Event, Category
from bookings.models import Booking


def organizer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_organizer or request.user.is_admin_user):
            messages.error(request, "Access denied. Organizer account required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            messages.error(request, "Access denied. Admin account required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event', 'event__category').order_by('-booked_at')
    upcoming = bookings.filter(status='confirmed', event__date__gte=timezone.now().date())
    past = bookings.filter(status='confirmed', event__date__lt=timezone.now().date())
    cancelled = bookings.filter(status='cancelled')
    total_spent = bookings.filter(status='confirmed').aggregate(t=Sum('total_price'))['t'] or 0

    return render(request, 'dashboard/user_dashboard.html', {
        'bookings': bookings,
        'upcoming': upcoming,
        'past': past,
        'cancelled': cancelled,
        'total_spent': total_spent,
    })


@organizer_required
def organizer_dashboard(request):
    events = Event.objects.filter(organizer=request.user).select_related('category').order_by('-created_at')
    total_revenue = sum(e.revenue() for e in events)
    total_bookings = Booking.objects.filter(event__organizer=request.user, status='confirmed').count()
    upcoming_events = events.filter(status='published', date__gte=timezone.now().date()).count()

    recent_bookings = Booking.objects.filter(
        event__organizer=request.user
    ).select_related('user', 'event').order_by('-booked_at')[:10]

    return render(request, 'dashboard/organizer_dashboard.html', {
        'events': events,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'upcoming_events': upcoming_events,
        'recent_bookings': recent_bookings,
    })


@admin_required
def admin_dashboard(request):
    all_events = Event.objects.select_related('organizer', 'category').order_by('-created_at')
    all_users = User.objects.order_by('-date_joined')
    all_bookings = Booking.objects.select_related('user', 'event').order_by('-booked_at')

    stats = {
        'total_users': User.objects.filter(role='user').count(),
        'total_organizers': User.objects.filter(role='organizer').count(),
        'total_events': all_events.count(),
        'published_events': all_events.filter(status='published').count(),
        'total_bookings': all_bookings.filter(status='confirmed').count(),
        'total_revenue': all_bookings.filter(status='confirmed').aggregate(t=Sum('total_price'))['t'] or 0,
        'events_today': all_events.filter(date=timezone.now().date()).count(),
    }

    # Revenue by category
    category_stats = []
    for cat in Category.objects.all():
        cat_bookings = Booking.objects.filter(event__category=cat, status='confirmed')
        cat_revenue = cat_bookings.aggregate(t=Sum('total_price'))['t'] or 0
        cat_count = cat_bookings.count()
        if cat_count > 0:
            category_stats.append({'category': cat, 'bookings': cat_count, 'revenue': cat_revenue})

    return render(request, 'dashboard/admin_dashboard.html', {
        'all_events': all_events[:20],
        'all_users': all_users[:20],
        'recent_bookings': all_bookings[:15],
        'stats': stats,
        'category_stats': sorted(category_stats, key=lambda x: x['revenue'], reverse=True)[:5],
    })


@admin_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/admin_users.html', {'users': users})


@admin_required
def admin_events(request):
    events = Event.objects.select_related('organizer', 'category').order_by('-created_at')
    return render(request, 'dashboard/admin_events.html', {'events': events})


@admin_required
def admin_bookings(request):
    bookings = Booking.objects.select_related('user', 'event').order_by('-booked_at')
    return render(request, 'dashboard/admin_bookings.html', {'bookings': bookings})


@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")
    return redirect('dashboard:admin_users')
