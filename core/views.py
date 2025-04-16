from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from notifications.models import Notification
from .models import FAQ, SystemAnnouncement, ContactMessage
from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add active announcements to context
        context['announcements'] = SystemAnnouncement.objects.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority', '-start_date')[:5]
        return context

class FAQListView(ListView):
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        return FAQ.objects.filter(is_published=True).order_by('category', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group FAQs by category
        faqs_by_category = {}
        for faq in context['faqs']:
            category = faq.get_category_display()
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            faqs_by_category[category].append(faq)
        context['faqs_by_category'] = faqs_by_category
        return context

class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'core/contact.html'
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        messages.success(self.request, 'Your message has been sent successfully. We will get back to you soon.')
        return super().form_valid(form)

class AnnouncementListView(ListView):
    model = SystemAnnouncement
    template_name = 'core/announcements.html'
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        return SystemAnnouncement.objects.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('-priority', '-start_date')

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.request.user.notifications.unread().count()
        return context

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        request.user.notifications.mark_all_as_read()
        messages.success(request, 'All notifications marked as read.')
        return redirect('core:notifications')
    return redirect('core:notifications')

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, recipient=request.user, id=pk)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('core:notifications')
