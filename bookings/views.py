# bookings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction, IntegrityError
from events.models import Event
from .models import Booking


@login_required
def book_event(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk, status='published')

    if event.is_past():
        messages.error(request, "This event has already passed.")
        return redirect('events:detail', pk=event_pk)

    if event.is_sold_out():
        messages.error(request, "Sorry, this event is sold out.")
        return redirect('events:detail', pk=event_pk)

    # Quick pre-check: avoid showing booking form if already have confirmed booking
    existing = Booking.objects.filter(user=request.user, event=event, status='confirmed').first()
    if existing:
        messages.warning(request, "You already have a booking for this event.")
        return redirect('bookings:confirmation', booking_id=existing.booking_id)

    if request.method == 'POST':
        # safe conversion of quantity
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            messages.error(request, "Invalid ticket quantity.")
            return redirect('events:detail', pk=event_pk)

        if quantity < 1 or quantity > 10:
            messages.error(request, "Invalid ticket quantity (1–10).")
            return redirect('events:detail', pk=event_pk)

        if quantity > event.available_tickets:
            messages.error(request, f"Only {event.available_tickets} tickets left.")
            return redirect('events:detail', pk=event_pk)

        try:
            with transaction.atomic():
                # Lock the event row to prevent race conditions on available_tickets
                event_locked = Event.objects.select_for_update().get(pk=event_pk)

                # Re-check available tickets on the locked row
                if quantity > event_locked.available_tickets:
                    messages.error(request, "Not enough tickets available.")
                    return redirect('events:detail', pk=event_pk)

                # Re-check existing confirmed booking inside transaction to avoid race condition
                existing_inside = Booking.objects.select_for_update().filter(
                    user=request.user,
                    event=event_locked,
                    status='confirmed'
                ).first()

                if existing_inside:
                    messages.warning(request, "You already have a booking for this event.")
                    return redirect('bookings:confirmation', booking_id=existing_inside.booking_id)

                # Create booking (may still raise IntegrityError in extreme race cases — handled below)
                booking = Booking.objects.create(
                    user=request.user,
                    event=event_locked,
                    quantity=quantity,
                    total_price=event_locked.ticket_price * quantity,
                    status='confirmed',
                )

                # Deduct tickets and save
                event_locked.available_tickets -= quantity
                event_locked.save()

        except IntegrityError:
            # Another concurrent request created a booking for this user+event.
            # Retrieve the confirmed booking and warn/redirect.
            confirmed = Booking.objects.filter(user=request.user, event=event, status='confirmed').first()
            if confirmed:
                messages.warning(request, "You already have a booking for this event (concurrent request).")
                return redirect('bookings:confirmation', booking_id=confirmed.booking_id)
            # If we can't find a confirmed booking, show a generic error
            messages.error(request, "Could not create booking due to concurrent activity. Try again.")
            return redirect('events:detail', pk=event_pk)

        # Success
        messages.success(request, f"🎉 Booking confirmed! Your booking ID: {booking.short_id()}")
        return redirect('bookings:confirmation', booking_id=booking.booking_id)

    return render(request, 'bookings/book.html', {'event': event})


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if booking.status != 'confirmed':
        messages.error(request, "This booking is already cancelled.")
        return redirect('dashboard:user_dashboard')

    if request.method == 'POST':
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            # Restore tickets
            event = Event.objects.select_for_update().get(pk=booking.event.pk)
            event.available_tickets += booking.quantity
            event.save()

        messages.success(request, f"Booking for '{booking.event.title}' has been cancelled.")
        return redirect('dashboard:user_dashboard')

    return render(request, 'bookings/cancel.html', {'booking': booking})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event', 'event__category')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})