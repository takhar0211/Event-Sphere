from django.db import models
from django.conf import settings
from events.models import Event
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-booked_at']
        unique_together = ['user', 'event']  # prevent duplicate bookings

    def __str__(self):
        return f"Booking #{str(self.booking_id)[:8]} - {self.user.username} @ {self.event.title}"

    def short_id(self):
        return str(self.booking_id).upper()[:8]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_price = self.event.ticket_price * self.quantity
        super().save(*args, **kwargs)
