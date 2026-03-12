from django import forms
from .models import Event, Category
from django.utils import timezone


class EventForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'image',
            'location', 'venue_name', 'date', 'time', 'end_time',
            'ticket_price', 'max_attendees', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        max_attendees = cleaned_data.get('max_attendees')

        if date and date < timezone.now().date():
            if not self.instance.pk:  # Only for new events
                raise forms.ValidationError("Event date cannot be in the past.")

        return cleaned_data

    def save(self, commit=True):
        event = super().save(commit=False)
        if commit:
            # Sync available_tickets with max_attendees for new events
            if not event.pk:
                event.available_tickets = event.max_attendees
            event.save()
        return event


class EventSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={'placeholder': 'Search events...'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='All Categories')
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    price_min = forms.DecimalField(required=False, min_value=0, label='Min Price')
    price_max = forms.DecimalField(required=False, min_value=0, label='Max Price')
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('date', 'Date (Upcoming)'),
            ('-date', 'Date (Latest)'),
            ('ticket_price', 'Price (Low to High)'),
            ('-ticket_price', 'Price (High to Low)'),
            ('title', 'Title (A-Z)'),
        ]
    )
