from django import forms
from .models import ContactMessage, UserNotificationPreference

class ContactForm(forms.ModelForm):
    """Form for handling contact messages."""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message here...'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            # Pre-fill user information if available
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
            
            # Make these fields readonly
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True

class NotificationPreferenceForm(forms.ModelForm):
    """Form for updating user notification preferences."""
    
    class Meta:
        model = UserNotificationPreference
        fields = ['email_notifications', 'browser_notifications', 'notification_frequency']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'browser_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notification_frequency': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_notifications'].help_text = 'Receive notifications via email'
        self.fields['browser_notifications'].help_text = 'Receive notifications in browser'
        self.fields['notification_frequency'].help_text = 'How often would you like to receive notification digests?'

class AnnouncementFilterForm(forms.Form):
    """Form for filtering announcements."""
    
    PRIORITY_CHOICES = [('', 'All')] + list(SystemAnnouncement.PRIORITY_CHOICES)
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class FAQFilterForm(forms.Form):
    """Form for filtering FAQs."""
    
    CATEGORY_CHOICES = [('', 'All')] + list(FAQ.CATEGORY_CHOICES)
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search FAQs...'
        })
    )

class NotificationFilterForm(forms.Form):
    """Form for filtering notifications."""
    
    STATUS_CHOICES = [
        ('', 'All'),
        ('unread', 'Unread'),
        ('read', 'Read')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
