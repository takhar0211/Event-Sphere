from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='🎪')
    color = models.CharField(max_length=7, default='#e8c547')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    location = models.CharField(max_length=300)
    venue_name = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_attendees = models.PositiveIntegerField(default=100)
    available_tickets = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'pk': self.pk})

    def is_past(self):
        return self.date < timezone.now().date()

    def is_sold_out(self):
        return self.available_tickets == 0

    def tickets_sold(self):
        return self.max_attendees - self.available_tickets

    def occupancy_percent(self):
        if self.max_attendees == 0:
            return 0
        return int((self.tickets_sold() / self.max_attendees) * 100)

    def revenue(self):
        return self.tickets_sold() * self.ticket_price

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
