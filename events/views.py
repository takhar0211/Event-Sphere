from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Event, Category
from .forms import EventForm, EventSearchForm
from bookings.models import Booking


def home(request):
    featured = Event.objects.filter(status='published', is_featured=True, date__gte=timezone.now().date()).order_by('date')[:4]
    upcoming = Event.objects.filter(status='published', date__gte=timezone.now().date()).order_by('date')[:8]
    categories = Category.objects.all()
    stats = {
        'total_events': Event.objects.filter(status='published').count(),
        'total_categories': categories.count(),
        'total_bookings': Booking.objects.filter(status='confirmed').count(),
    }
    return render(request, 'events/home.html', {
        'featured': featured,
        'upcoming': upcoming,
        'categories': categories,
        'stats': stats,
    })


def event_list(request):
    form = EventSearchForm(request.GET)
    events = Event.objects.filter(status='published')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        sort = form.cleaned_data.get('sort') or 'date'

        if q:
            events = events.filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
            )
        if category:
            events = events.filter(category=category)
        if date_from:
            events = events.filter(date__gte=date_from)
        if date_to:
            events = events.filter(date__lte=date_to)
        if price_min is not None:
            events = events.filter(ticket_price__gte=price_min)
        if price_max is not None:
            events = events.filter(ticket_price__lte=price_max)
        events = events.order_by(sort)
    else:
        events = events.filter(date__gte=timezone.now().date()).order_by('date')

    categories = Category.objects.all()
    return render(request, 'events/list.html', {
        'events': events,
        'form': form,
        'categories': categories,
        'total': events.count(),
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_booking = None
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(user=request.user, event=event, status='confirmed').first()
    similar = Event.objects.filter(
        category=event.category, status='published', date__gte=timezone.now().date()
    ).exclude(pk=pk).order_by('date')[:3]
    return render(request, 'events/detail.html', {
        'event': event,
        'user_booking': user_booking,
        'similar': similar,
    })


def events_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    events = Event.objects.filter(category=category, status='published', date__gte=timezone.now().date()).order_by('date')
    return render(request, 'events/list.html', {
        'events': events,
        'category': category,
        'form': EventSearchForm(),
        'categories': Category.objects.all(),
        'total': events.count(),
    })


@login_required
def create_event(request):
    if not request.user.is_organizer and not request.user.is_admin_user:
        messages.error(request, "Only organizers can create events.")
        return redirect('home')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.available_tickets = event.max_attendees
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('events:detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@login_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user and not request.user.is_admin_user:
        messages.error(request, "You can only edit your own events.")
        return redirect('events:detail', pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated = form.save(commit=False)
            tickets_sold = event.tickets_sold()
            new_max = updated.max_attendees
            updated.available_tickets = max(0, new_max - tickets_sold)
            updated.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('events:detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Edit', 'event': event})


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user and not request.user.is_admin_user:
        messages.error(request, "You can only delete your own events.")
        return redirect('events:detail', pk=pk)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        if request.user.is_admin_user:
            return redirect('dashboard:admin_dashboard')
        return redirect('dashboard:organizer_dashboard')
    return render(request, 'events/confirm_delete.html', {'event': event})


def context_processors(request):
    return {'categories': Category.objects.all()}
