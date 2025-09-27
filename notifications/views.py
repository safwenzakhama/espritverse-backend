from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/?unread=1
    Paginated list, newest first.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
        if self.request.query_params.get("unread") in {"1", "true", "yes"}:
            qs = qs.filter(is_read=False)
        return qs

class NotificationMarkReadView(APIView):
    """
    POST /api/notifications/{id}/read/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        n = Notification.objects.filter(pk=pk, recipient=request.user).first()
        if not n:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if not n.is_read:
            n.is_read = True
            n.save(update_fields=["is_read"])
        return Response({"ok": True})

class NotificationMarkAllReadView(APIView):
    """
    POST /api/notifications/mark-all-read/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"ok": True})

class NotificationDeleteView(APIView):
    """
    DELETE /api/notifications/{id}/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        n = Notification.objects.filter(pk=pk, recipient=request.user).first()
        if not n:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        n.delete()
        return Response({"ok": True})

class NotificationBulkActionView(APIView):
    """
    POST /api/notifications/bulk-action/
    Body: {"action": "delete_all", "action": "delete_read", "action": "delete_unread", "action": "mark_all_read"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        action = request.data.get("action")
        user = request.user
        
        if action == "delete_all":
            count = Notification.objects.filter(recipient=user).count()
            Notification.objects.filter(recipient=user).delete()
            return Response({"deleted": count})
        
        elif action == "delete_read":
            count = Notification.objects.filter(recipient=user, is_read=True).count()
            Notification.objects.filter(recipient=user, is_read=True).delete()
            return Response({"deleted": count})
        
        elif action == "delete_unread":
            count = Notification.objects.filter(recipient=user, is_read=False).count()
            Notification.objects.filter(recipient=user, is_read=False).delete()
            return Response({"deleted": count})
        
        elif action == "mark_all_read":
            count = Notification.objects.filter(recipient=user, is_read=False).count()
            Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
            return Response({"marked_read": count})
        
        else:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
