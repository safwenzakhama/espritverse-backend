# notifications/urls.py
from django.urls import path
from .views import (
    NotificationListView, 
    NotificationMarkReadView, 
    NotificationMarkAllReadView,
    NotificationDeleteView,
    NotificationBulkActionView
)

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/mark-all-read/", NotificationMarkAllReadView.as_view(), name="notifications-mark-all"),
    path("notifications/<int:pk>/read/", NotificationMarkReadView.as_view(), name="notifications-mark-read"),
    path("notifications/<int:pk>/", NotificationDeleteView.as_view(), name="notifications-delete"),
    path("notifications/bulk-action/", NotificationBulkActionView.as_view(), name="notifications-bulk-action"),
]
