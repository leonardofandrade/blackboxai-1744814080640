def notifications_processor(request):
    """Add unread notifications count to the context."""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.unread().count()
        }
    return {'unread_notifications_count': 0}
